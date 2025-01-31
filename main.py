import tkinter as tk
import os
import random
from PIL import Image, ImageTk, ExifTags
import cv2
import numpy as np
import sys

# Global variable for video capture
cap = None

# Folder settings
text_folder_selection = "archive"
image_folder_selection = "archive"

# Get the directory where the executable is located
if getattr(sys, 'frozen', False):  # If the script is running as a bundled executable
    bundle_dir = sys._MEIPASS  # Temporary folder where resources are extracted
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))  # Regular script location

# Media and text folder paths relative to the executable or script
images_path = os.path.join(bundle_dir, 'images')
textes_path = os.path.join(bundle_dir, 'textes')

# Load random media (image/video)
def load_random_media():
    media_folder = os.path.join(images_path, image_folder_selection)  # Use bundled path
    media_files = [f for f in os.listdir(media_folder) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.mp4', '.avi', '.mov', '.mkv'))]

    if media_files:
        random_media_file = random.choice(media_files)
        media_path = os.path.join(media_folder, random_media_file)

        if media_path.endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif')):
            img = Image.open(media_path)
            try:
                exif = img._getexif()
                if exif:
                    for orientation in ExifTags.TAGS.keys():
                        if ExifTags.TAGS[orientation] == 'Orientation':
                            break
                    if exif.get(orientation) == 3:
                        img = img.rotate(180, expand=True)
                    elif exif.get(orientation) == 6:
                        img = img.rotate(270, expand=True)
                    elif exif.get(orientation) == 8:
                        img = img.rotate(90, expand=True)
            except (AttributeError, KeyError, IndexError):
                pass
            img = scale_image_to_window(img)
            return img, random_media_file, "image"

        elif media_path.endswith(('mp4', 'avi', 'mov', 'mkv')):
            return media_path, random_media_file, "video"

    return None, None, None

# Scale the image to fit within the window size
def scale_image_to_window(img):
    max_width, max_height = 1000, 600  # Larger media display size
    img_width, img_height = img.size
    width_ratio = max_width / img_width
    height_ratio = max_height / img_height
    scale_factor = min(width_ratio, height_ratio)
    new_width = int(img_width * scale_factor)
    new_height = int(img_height * scale_factor)
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return img

# Load random text
def load_random_text():
    text_folder = os.path.join(textes_path, text_folder_selection)  # Use bundled path
    text_files = [f for f in os.listdir(text_folder) if f.endswith('.txt')]
    if text_files:
        random_text_file = random.choice(text_files)
        text_path = os.path.join(text_folder, random_text_file)
        with open(text_path, 'r') as file:
            sentences = [line.strip() for line in file if line.strip()]
            if sentences:
                return random.choice(sentences), random_text_file
            else:
                return f"No valid sentences in {random_text_file}.", random_text_file
    else:
        return f"No text files found in 'texte/{text_folder_selection}' folder.", ""

# Updated display_video function
def display_video(video_path):
    global cap
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file")
        return
    
    # Hide text labels during video playback
    label_text_filename.pack_forget()
    label_text.pack_forget()
    
    def show_frame():
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop the video
            ret, frame = cap.read()
        frame_resized = cv2.resize(frame, (1000, 600))
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        frame_image = Image.fromarray(frame_rgb)
        frame_image = ImageTk.PhotoImage(frame_image)
        label_video.config(image=frame_image)
        label_video.image = frame_image
        label_video.after(33, show_frame)
    
    label_video.pack(pady=10)
    show_frame()

# Updated update_content function
def update_content():
    global cap
    if cap is not None:
        cap.release()
        cap = None
        label_video.pack_forget()  # Hide video label
    
    # Show text labels by default (when not displaying a video)
    label_text_filename.pack(pady=10)
    label_text.pack(pady=10)
    
    # Media handling
    media, media_filename, media_type = load_random_media()
    if media_type == "image" and media:
        img_tk = ImageTk.PhotoImage(media)
        label_media.config(image=img_tk)
        label_media.image = img_tk
        label_media.pack(pady=10)
        label_video.pack_forget()  # Ensure video label is hidden
    elif media_type == "video" and media:
        label_media.pack_forget()  # Hide image label
        display_video(media)
    else:
        label_media.config(text="No media found.")
        label_media.pack(pady=10)
        label_video.pack_forget()
    label_media_filename.config(text=f"Media File: {media_filename or 'N/A'}")

    # Text handling
    random_text, text_filename = load_random_text()
    label_text.config(text=random_text)
    label_text_filename.config(text=f"Text File: {text_filename}")

# Toggle folder selection
def toggle_text_folder():
    global text_folder_selection
    text_folder_selection = "archive" if text_folder_selection == "creation" else "creation"
    button_text_toggle.config(text=f"Text: {text_folder_selection.capitalize()}")
    update_content()

def toggle_image_folder():
    global image_folder_selection
    image_folder_selection = "archive" if image_folder_selection == "creation" else "creation"
    button_image_toggle.config(text=f"Media: {image_folder_selection.capitalize()}")
    update_content()

# Create the main window
root = tk.Tk()
root.title("Random Media and Text Viewer")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")
root.config(bg='black')

# Left frame for toggle buttons
frame_left = tk.Frame(root, bg='black', width=200)
frame_left.place(relx=0.2, rely=0.5, anchor='center')  # Position at 1/4 horizontally, center vertically

button_image_toggle = tk.Button(frame_left, text=f"Media: {image_folder_selection.capitalize()}", command=toggle_image_folder, height=2, width=15, font=("Helvetica", 14), bg='grey')
button_image_toggle.pack(pady=10)
button_text_toggle = tk.Button(frame_left, text=f"Text: {text_folder_selection.capitalize()}", command=toggle_text_folder, height=2, width=15, font=("Helvetica", 14), bg='grey')
button_text_toggle.pack(pady=10)

# Center frame for main content
frame_center = tk.Frame(root, bg='black')
frame_center.place(relx=0.5, rely=0.5, anchor='center')  # Center of the canvas

label_media_filename = tk.Label(frame_center, text="Media File: ", fg="white", bg="black", font=("Helvetica", 16))
label_media_filename.pack(pady=10)

label_media = tk.Label(frame_center, bg='black')
label_media.pack(pady=10)

label_video = tk.Label(frame_center, bg='black')

label_text_filename = tk.Label(frame_center, text="Text File: ", fg="white", bg="black", font=("Helvetica", 16))
label_text_filename.pack(pady=10)

label_text = tk.Label(frame_center, text="", fg="white", bg="black", font=("Helvetica", 18), wraplength=screen_width // 2)
label_text.pack(pady=10)

button_resample = tk.Button(frame_center, text="Resample", command=update_content, height=2, width=20, font=("Helvetica", 14), bg='grey')
button_resample.pack(pady=10)

# Run the initial update
update_content()
root.mainloop()
