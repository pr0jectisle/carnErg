import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import laDiction.Agent as Agent
import random

a = Agent.Agent() #Init agent

num_faces = False

def sample():
    if num_faces > 0:
        a.act(num_faces)
    else :
        a.dont_act()
    update_labels()
    a.compute_high()

def update_frame(): # "Recursive" update method to read cam & detect face
    global num_faces
    ret, frame = cap.read()
    if ret: #If cam accessible

        #Detect face in grayscale and draw rectangle around it
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(
            gray_frame, scaleFactor=1.1, minNeighbors=8, minSize=(40, 40)
        )
        
        num_faces = len(faces)

        for (x, y, w, h) in faces: #Draw faces
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 4)

        # Convert the frame to RGB, to PIL and then to ImageTK
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        
        # Update the label with the new image
        label.config(image=img_tk)
        label.image = img_tk  # Keep a reference to avoid garbage collection
    
    # "Recursive" call after 10ms
    window.after(10, update_frame)




# Main Tkinter window
window = tk.Tk()
window.geometry("1000x900")
window.title("Human-Addicted Program")
window.config(bg = "black")

# Agent frame
agent_frame = tk.Frame(window, width=500, height=500, bg = "black")
agent_frame.pack(expand=True)

def update_labels(): #Method to update agent section info
    status_label.config(text=f"Status: {a.status}")
    reward_label.config(text=f"Mood: {a.reward_points}")
    dependence_label.config(text=f"Dependence: {a.dependence}")
    tolerance_label.config(text=f"Tolerance: {a.tolerance}")
    craving_label.config(text=f"Craving: {a.craving}")
def reset(): #Method to reset
    a.__init__()
    update_labels()

pb = ttk.Progressbar(agent_frame, orient = "vertical", mode = "determinate", length = 200)
pb.place(relx=0.95, rely=0.5, anchor="center")
pb.start()

# Add labels in agent frame
status_label = tk.Label(agent_frame, text=f"Status: {a.status}", font=("Helvetica", 22), fg='white', bg='black')
reward_label = tk.Label(agent_frame, text=f"Wellbeing: {a.reward_points}", font=("Helvetica", 16), fg='white', bg='black')
dependence_label = tk.Label(agent_frame, text=f"Dependence: {a.dependence}", font=("Helvetica", 16), fg='white', bg='black')
tolerance_label = tk.Label(agent_frame, text=f"Tolerance: {a.tolerance}", font=("Helvetica", 16), fg='white', bg='black')
craving_label = tk.Label(agent_frame, text=f"Craving: {a.craving}", font=("Helvetica", 16), fg='white', bg='black')
reset_button = tk.Button(agent_frame,text=f"Reset",font=("Helvetica", 16), command=reset, fg='white', bg='black') 

#Pack
status_label.pack(pady=5)
reward_label.pack(pady=5)
dependence_label.pack(pady=5)
tolerance_label.pack(pady=5)
craving_label.pack(pady=5)
reset_button.pack(pady = 5)



cam_frame = tk.Frame(window, bg = "black")
cam_frame.pack(padx=10, pady=10)

label = tk.Label(cam_frame)
label.pack()

cap = cv2.VideoCapture(0)
face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
if not cap.isOpened():
    print("Error: Could not access the camera.")
    exit()

update_frame()



#"sample_frame = tk.Frame(window)
#sample_frame.pack()
sample_button = tk.Button(cam_frame, text = "Sample", width = 20,font = ("Helvetica", 18), command = sample, fg='white', bg='black')
sample_button.pack(pady = 10)

window.mainloop()

# Release
cap.release()
cv2.destroyAllWindows()
