import os
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk
import pygame
import glob
import re


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
        self.total_items = self.count_total_sets()

        self.original_images = {}  # Preloaded images
        self.texts = {}            # Preloaded texts
        self.sounds = {}           # Preloaded sounds

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
        self.image_name_label.pack(pady=5)

        # Right side: Scrollable text with adjusted size
        self.text_frame = tk.Frame(self.content_frame)
        self.text_frame.pack(side="right", fill="both", expand=True)

        # Adjust the text frame height by giving it some padding
        self.text_widget = tk.Text(self.text_frame, wrap="word", font=("Arial", 14))
        self.text_widget.config(state="disabled")  # Non-editable
        self.text_widget.pack(side="left", fill="both", expand=True, padx=10, pady=(10, 40))  # Added padding for better space

        # Text filename display (top left of the text frame)
        self.text_name_label = Label(self.text_frame, text="", font=("Arial", 10))
        self.text_name_label.pack(anchor="w", padx=10, pady=5)  # Anchor left, some padding

        # Progress display (bottom of text frame)
        self.progress_label = Label(self.text_frame, text="", font=("Arial", 10))
        self.progress_label.pack(side="bottom", anchor="w", padx=10, pady=5)

        # Text scrollbar
        self.text_scroll = tk.Scrollbar(self.text_frame, command=self.text_widget.yview)
        self.text_scroll.pack(side="right", fill="y")
        self.text_widget.config(yscrollcommand=self.text_scroll.set)

        # Bottom navigation buttons
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(side="bottom", pady=10)
        self.prev_button = Button(self.button_frame, text="Previous", command=self.prev_item)
        self.prev_button.pack(side="left", padx=20)
        self.next_button = Button(self.button_frame, text="Next", command=self.next_item)
        self.next_button.pack(side="right", padx=20)

        # Sound filename display (bottom-left corner)
        self.sound_name_label = Label(root, text="", font=("Arial", 10))
        self.sound_name_label.pack(side="left", padx=20, pady=10)

        # Keyboard shortcuts
        self.root.bind("<Left>", lambda e: self.prev_item())
        self.root.bind("<Right>", lambda e: self.next_item())

        self.total_items = self.count_total_sets()
        self.preload_all_media()
        self.load_media()






    def preload_all_media(self):
        for i in range(1, self.total_items + 1):
            # Load image
            image_path = find_file(IMAGE_FOLDER, "image", i, SUPPORTED_IMAGE_EXTENSIONS)
            if image_path:
                try:
                    self.original_images[i] = Image.open(image_path)
                    image_filename = os.path.basename(image_path)
                    clean_image_name = clean_filename(image_filename)
                    self.image_name_label.config(text=f"Image: {clean_image_name}")
                except Exception as e:
                    print(f"Failed to load image {image_path}: {e}")

            # Load text
            text_path = os.path.join(TEXT_FOLDER, f"text{i}.txt")
            if os.path.exists(text_path):
                with open(text_path, "r", encoding="utf-8") as f:
                    self.texts[i] = f.read()
                text_filename = os.path.basename(text_path)
                clean_text_name = clean_filename(text_filename)
                self.text_name_label.config(text=f"Text: {clean_text_name}")

            # Load sound
            sound_path = find_file(SOUND_FOLDER, "sound", i, SUPPORTED_SOUND_EXTENSIONS)
            if sound_path:
                self.sounds[i] = sound_path
                sound_filename = os.path.basename(sound_path)
                clean_sound_name = clean_filename(sound_filename)
                self.sound_name_label.config(text=f"Sound: {clean_sound_name}")



    def count_total_sets(self):
        image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().startswith("image")]
        numbers = [int(f[5:].split('.')[0]) for f in image_files if f[5:].split('.')[0].isdigit()]
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
        print(sound_path)
        if sound_path:
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play()
        else:
            pygame.mixer.music.stop()

        # Update progress
        self.progress_label.config(text=f"{self.current_index} / {self.total_items}")

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


def find_file(base_folder, prefix, index, extensions):
    print(prefix)
    for ext in extensions:
        pattern = os.path.join(base_folder, f"{prefix}{index}.{ext}")
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
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


if __name__ == "__main__":
    root = tk.Tk()
    app = MediaViewer(root)
    root.mainloop()
