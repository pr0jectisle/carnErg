import tkinter as tk
import os
import random
from PIL import Image, ImageTk, ExifTags
import cv2
import numpy as np

# Global variable for video capture to handle stopping/resetting the video
cap = None

# Function to load a random media (image/video) from the "images" folder and handle rotation
def load_random_media():
    media_folder = "images"
    media_files = [f for f in os.listdir(media_folder) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.mp4', '.avi', '.mov', '.mkv'))]
    
    if media_files:
        random_media_file = random.choice(media_files)
        media_path = os.path.join(media_folder, random_media_file)
        
        # Check if it's an image
        if media_path.endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif')):
            img = Image.open(media_path)
            
            # Handle rotation based on EXIF data, only if EXIF data exists
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
                pass  # If no EXIF or errors, just skip the rotation
                
            # Scale the image to fit within the window while maintaining aspect ratio
            img = scale_image_to_window(img)
            return img, "image"
        
        # If it's a video
        elif media_path.endswith(('mp4', 'avi', 'mov', 'mkv')):
            return media_path, "video"
    
    return None, None

# Function to scale the image to fit within the window size while maintaining the aspect ratio
def scale_image_to_window(img):
    max_width, max_height = 1300, 800  # Window size
    
    # Subtract the height of the text and button from the available space for the image
    button_height = 40  # Approximate height of the button
    text_height = 100   # Approximate height of the text area (adjust if needed)
    
    available_height = max_height - button_height - text_height  # Space available for image
    
    # Get the original image size
    img_width, img_height = img.size
    
    # Calculate the scaling factors for width and height
    width_ratio = max_width / img_width
    height_ratio = available_height / img_height
    
    # Use the smaller ratio to maintain the aspect ratio
    scale_factor = min(width_ratio, height_ratio)
    
    # Calculate the new size of the image
    new_width = int(img_width * scale_factor)
    new_height = int(img_height * scale_factor)
    
    # Resize the image using LANCZOS for high-quality downsampling
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return img

# Function to load a random sentence from a random file in the "texte" folder (ignores empty lines)
def load_random_text():
    text_folder = "texte"
    text_files = [f for f in os.listdir(text_folder) if f.endswith('.txt')]
    
    if text_files:
        # Select a random .txt file
        random_text_file = random.choice(text_files)
        text_path = os.path.join(text_folder, random_text_file)
        
        with open(text_path, 'r') as file:
            sentences = file.readlines()
            # Filter out empty lines
            sentences = [line.strip() for line in sentences if line.strip()]
            if sentences:
                # Randomly select a sentence
                return random.choice(sentences), random_text_file
            else:
                return f"No valid sentences found in {random_text_file}.", random_text_file
    else:
        return "No text files found in the 'texte' folder.", ""

# Function to update the window with new random media (image or video) and text
def update_content():
    global cap  # To access the global video capture object
    
    # Stop and release the current video if it's playing
    if cap is not None:
        cap.release()
        cap = None
        label_video.pack_forget()  # Hide the video label

    # Load and display random media
    media, media_type = load_random_media()
    
    if media_type == "image" and media:
        img_tk = ImageTk.PhotoImage(media)
        label_img.config(image=img_tk)
        label_img.image = img_tk
        label_img.pack(pady=20)
        label_video.pack_forget()  # Hide the video label if it's an image
        
    elif media_type == "video" and media:
        label_img.pack_forget()  # Hide the image label if it's a video
        display_video(media)
        
    else:
        label_img.config(text="No media found.")
    
    # Load and display random text (sentence from a random file)
    random_text, text_filename = load_random_text()

    # Limit the length of the text displayed to avoid long sentences pushing buttons
    max_text_length = 400  # Maximum number of characters (can span multiple lines)
    if len(random_text) > max_text_length:
        random_text = random_text[:max_text_length] + "..."  # Truncate and add ellipsis

    label_text.config(text=random_text)
    
    # Display the name of the text file on top of the text
    label_file.config(text=f"Phrase issue de : {text_filename}")

# Function to display a video using OpenCV
def display_video(video_path):
    global cap  # To access the global video capture object
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error opening video file")
        return
    
    # Get video frame dimensions
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Get the video frame rate (FPS)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps == 0:
        fps = 30  # Default fallback FPS if the video doesn't provide it

    # Calculate the scaling factor for video to fit the available window size
    max_width, max_height = 1300, 800  # Window size

    # Subtract the height of the text and button from the available space for the video
    button_height = 40  # Approximate height of the button
    text_height = 100   # Approximate height of the text area (adjust if needed)
    available_height = max_height - button_height - text_height  # Space available for video

    # Calculate the scaling factors for width and height
    width_ratio = max_width / video_width
    height_ratio = available_height / video_height

    # Use the smaller ratio to maintain the aspect ratio
    scale_factor = min(width_ratio, height_ratio)

    # Calculate the new size of the video
    new_width = int(video_width * scale_factor)
    new_height = int(video_height * scale_factor)

    # Create a Tkinter-compatible photo object for the video frame
    def show_frame():
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset video to the start
            ret, frame = cap.read()

        # Resize the frame to fit within the window
        frame_resized = cv2.resize(frame, (new_width, new_height))

        # Convert the frame to RGB
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        frame_image = Image.fromarray(frame_rgb)
        frame_image = ImageTk.PhotoImage(frame_image)

        # Update the label with the new frame
        label_video.config(image=frame_image)
        label_video.image = frame_image
        
        # Delay to match the frame rate of the video
        delay = int(1000 / fps)  # Delay in milliseconds between frames
        label_video.after(delay, show_frame)

    # Pack the video label to show the video
    label_video.pack(pady=20)
    show_frame()

# Create the main window
root = tk.Tk()
root.title("Random Media and Text Viewer")

# Maximize the window by setting its size to match the screen resolution
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}+0+0")

root.config(bg='black')  # Set the background color to black

# Frame for the content (image + text)
frame_content = tk.Frame(root, bg='black')
frame_content.pack(fill="both", expand=True)

# Frame for the image/video
frame_media = tk.Frame(frame_content, bg='black')
frame_media.pack(pady=20)

# Label to display the image
label_img = tk.Label(frame_media, bg='black')
label_img.pack()

# Label to display the random text
label_text = tk.Label(frame_content, fg="white", bg="black", font=("Helvetica", 14), wraplength=800)
label_text.pack()

# Label to display the name of the text file
label_file = tk.Label(frame_content, fg="white", bg="black", font=("Helvetica", 12))
label_file.pack()

# Label to display the video
label_video = tk.Label(frame_media, bg='black')

# Reset button (smaller, centered)
reset_button = tk.Button(root, text="Reset", command=update_content, height=2, width=25, font=("Helvetica", 16), bg='grey')
reset_button.pack(side="bottom", padx=5, pady=20)

# Run the update_content function to populate the window initially
update_content()

# Start the Tkinter event loop
root.mainloop()
