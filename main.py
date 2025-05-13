import os
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk
import pygame
import glob
import re
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller sets this in --onefile mode
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


SUPPORTED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'tif', 'tiff', 'bmp', 'gif', 'webp']
SUPPORTED_SOUND_EXTENSIONS = ['mp3', 'wav']
# Initialize pygame mixer
pygame.mixer.init()

# Constants
IMAGE_FOLDER = "images"
TEXT_FOLDER = "textes"
SOUND_FOLDER = "sons"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

class MediaViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Viewer")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self.current_index = 1

        self.original_images = {}  # Preloaded images
        self.image_filenames = {}
        self.texts = {}            # Preloaded texts
        self.text_filenames = {}
        self.sounds = {}           # Preloaded sounds
        self.sound_filenames = {}

        self.root.bind("<Configure>", self.on_resize)

        self.original_images = {}
        self.texts = {}
        self.sounds = {}

        # Main split frame (left = image, right = text)
        self.content_frame = tk.Frame(root)
        self.content_frame.pack(fill="both", expand=True)

        # Left side: Image
        self.image_frame = tk.Frame(self.content_frame)
        self.image_frame.pack(side="left", fill="both", expand=True)
        self.image_label = Label(self.image_frame)
        self.image_label.pack(expand=True)

        # Image filename display (below image)
        self.image_name_label = Label(self.image_frame, text="", font=("Arial", 10))
        self.image_name_label.pack(pady=15)

        # Container for text filename and text content
        self.text_content_frame = tk.Frame(self.content_frame)
        self.text_content_frame.pack(fill="both", expand=True)

        # Text filename display (top-left)
        self.text_name_label = Label(self.text_content_frame, text="", font=("Arial", 10))
        self.text_name_label.pack(anchor="w", padx=5, pady=(5, 0))

        # Text widget
        self.text_widget = tk.Text(self.text_content_frame, wrap="word", font=("Arial", 14))
        self.text_widget.config(state="disabled")
        self.text_widget.pack(side="left", fill="both", expand=True, padx=10, pady=(0, 40))  # leave room at bottom

        # Sound filename display (bottom-left corner)
        self.sound_name_label = Label(self.content_frame, text="", font=("Arial", 10))
        self.sound_name_label.pack(side="bottom",anchor="center", padx=0, pady=5)


        # Text scrollbar
        self.text_scroll = tk.Scrollbar(self.content_frame, command=self.text_widget.yview)
        self.text_scroll.pack(side="right", fill="y")
        self.text_widget.config(yscrollcommand=self.text_scroll.set)

        # Bottom navigation buttons
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(side="bottom", pady=10)
        self.prev_button = Button(self.button_frame, text="Previous", command=self.prev_item)
        self.prev_button.pack(side="left", padx=20)
        self.next_button = Button(self.button_frame, text="Next", command=self.next_item)
        self.next_button.pack(side="right", padx=20)

        
        # Progress display (bottom of text frame)
        self.progress_label = Label(self.button_frame, text="", font=("Arial", 10))
        self.progress_label.pack(side="left", anchor="center", padx=20)

        # Keyboard shortcuts
        self.root.bind("<Left>", lambda e: self.prev_item())
        self.root.bind("<Right>", lambda e: self.next_item())

        #Find pages number : 
        self.total_items = detect_max_index(
        [resource_path(IMAGE_FOLDER), resource_path(TEXT_FOLDER), resource_path(SOUND_FOLDER)],  # Use resource_path here!
        [SUPPORTED_IMAGE_EXTENSIONS, [".txt"], SUPPORTED_SOUND_EXTENSIONS]
        )

        
        self.preload_all_media()
        self.load_media()





    def preload_all_media(self):
        for i in range(1, self.total_items + 1):
            # Load image if available
            image_path = find_file(IMAGE_FOLDER, i, SUPPORTED_IMAGE_EXTENSIONS)
            image_path = resource_path(image_path)  # Use resource_path to get the correct path

            print(str(i) + " " + str(image_path))
            if image_path:
                try:
                    self.original_images[i] = Image.open(image_path)
                    self.image_filenames[i] = os.path.basename(image_path)
                except Exception as e:
                    print(f"Failed to load image {image_path}: {e}")
                    self.original_images[i] = None
                    self.image_filenames[i] = ""
            else:
                self.original_images[i] = None
                self.image_filenames[i] = ""

            # Load text if available
            text_path = find_file(TEXT_FOLDER, i, [".txt"])
            text_path = resource_path(text_path)  # Use resource_path here too

            print(str(i) + " " + str(text_path))

            if text_path:
                try:
                    with open(text_path, "r", encoding="utf-8") as f:
                        self.texts[i] = f.read()
                    self.text_filenames[i] = os.path.basename(text_path)
                except Exception as e:
                    print(f"Failed to load text {text_path}: {e}")
                    self.texts[i] = ""
                    self.text_filenames[i] = ""
            else:
                self.texts[i] = ""
                self.text_filenames[i] = ""

            # Load sound if available
            sound_path = find_file(SOUND_FOLDER, i, SUPPORTED_SOUND_EXTENSIONS)
            sound_path = resource_path(sound_path)  # And here too

            print(str(i) + " " + str(sound_path))

            if sound_path:
                self.sounds[i] = sound_path
                self.sound_filenames[i] = os.path.basename(sound_path)
            else:
                self.sounds[i] = None
                self.sound_filenames[i] = ""




    def count_total_sets(self):
        image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().startswith("image")]
        print(image_files)  
        numbers = [int(f[5:].split('.')[0]) for f in image_files if f[5:].split('.')[0].isdigit()]
        print(numbers)
        return max(numbers) if numbers else 0

    def load_media(self):
        self.update_displayed_image()

        # Display text
        text = self.texts.get(self.current_index, "Text not found")
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", text)
        self.text_widget.config(state="disabled")

        # Play sound
        sound_path = self.sounds.get(self.current_index)

        #print(sound_path)
        if sound_path:
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play()
        else:
            pygame.mixer.music.stop()

        # Update progress
        self.progress_label.config(text=f"{self.current_index} / {self.total_items}")

        # Remove extension and index from file name
        def format_filename(filename):
            return re.sub(r"[\d]+(\.[a-zA-Z0-9]+)?$", "", filename)
        
        self.image_name_label.config(text=f"Image : {format_filename(self.image_filenames.get(self.current_index, ''))}")
        self.text_name_label.config(text=f"Texte : {format_filename(self.text_filenames.get(self.current_index, ''))}")
        self.sound_name_label.config(text=f"Sons : {format_filename(self.sound_filenames.get(self.current_index, ''))}")


    def resize_image(self, image, max_width, max_height):
        image = image.copy()
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        return image


    def next_item(self):
        if self.current_index < self.total_items:
            self.current_index += 1
            self.load_media()

    def prev_item(self):
        if self.current_index > 1:
            self.current_index -= 1
            self.load_media()

    def on_resize(self, event):
        self.update_displayed_image()

    def update_displayed_image(self):
        original_image = self.original_images.get(self.current_index)
        if not original_image:
            self.image_label.config(image="", text="Image not found")
            return

        max_width = self.root.winfo_width() // 2 - 20
        max_height = self.root.winfo_height() - 100  # Leave space for buttons
        if max_width <= 0 or max_height <= 0:
            return

        resized = self.resize_image(original_image, max_width, max_height)
        tk_image = ImageTk.PhotoImage(resized)
        self.image_label.configure(image=tk_image)
        self.image_label.image = tk_image



def find_file(folder, index, allowed_extensions):
    """
    Searches for a file in 'folder' that ends with the given index before its extension,
    and has an allowed extension (e.g., jpg, mp3).
    """
    folder_path = resource_path(folder)  # Make sure the folder path is correct
    for file in os.listdir(folder_path):
        if any(file.lower().endswith(ext) for ext in allowed_extensions):
            name_without_ext = os.path.splitext(file)[0]
            match = re.search(r'(\d+)$', name_without_ext)
            if match and int(match.group(1)) == index:
                return os.path.join(folder_path, file)
    return None


def extract_index_from_filename(filename):
    match = re.search(r'(\d+)(?=\.[a-zA-Z]+$)', filename)
    return int(match.group(1)) if match else None

def clean_filename(filename):
    # Remove file extension
    base_name = os.path.splitext(filename)[0]
    
    # Remove the index number at the end of the filename
    base_name = re.sub(r'\d+$', '', base_name)
    
    return base_name
def detect_max_index(folders, allowed_extensions_map):
    max_index = -1
    for folder, extensions in zip(folders, allowed_extensions_map):
        folder_path = resource_path(folder)  # Use resource_path here!
        for file in os.listdir(folder_path):
            if any(file.lower().endswith(ext) for ext in extensions):
                name_without_ext = os.path.splitext(file)[0]
                match = re.search(r'(\d+)$', name_without_ext)
                if match:
                    idx = int(match.group(1))
                    max_index = max(max_index, idx)
    return max_index


if __name__ == "__main__":
    root = tk.Tk()
    app = MediaViewer(root)
    root.mainloop()
