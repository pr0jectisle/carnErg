import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk
import Agent


a = Agent.Agent()



def reset():
    a.__init__()
    update_labels()

def update_labels():
    status_label.config(text=f"Status: {a.status}")
    reward_label.config(text=f"Mood: {a.reward_points}")
    dependence_label.config(text=f"Dependence: {a.dependence}")
    tolerance_label.config(text=f"Tolerance: {a.tolerance}")
    craving_label.config(text=f"Craving: {a.craving}")
def act():
    a.act()
    update_labels()
def dont_act():
    a.dont_act()
    update_labels()

# Initialize the main window
root = tk.Tk()
root.geometry("700x700")
root.title("Humain Addicted AI")
# Create a frame for the middle section
middle_frame = tk.Frame(root, width=500, height=500)
middle_frame.pack(expand=True)

# Add the status label in the middle
status_label = tk.Label(middle_frame, text=f"Status: {a.status}", font=("Helvetica", 24))
reward_label = tk.Label(middle_frame, text=f"Mood: {a.reward_points}", font=("Helvetica", 18))
dependence_label = tk.Label(middle_frame, text=f"Dependence: {a.dependence}", font=("Helvetica", 18))
tolerance_label = tk.Label(middle_frame, text=f"Tolerance: {a.tolerance}", font=("Helvetica", 18))
craving_label = tk.Label(middle_frame, text=f"Craving: {a.craving}", font=("Helvetica", 18))
reset_button = tk.Button(middle_frame,text=f"Reset",font=("Helvetica", 18), command=reset)


status_label.pack(pady=15)
reward_label.pack(pady=15)
dependence_label.pack(pady=15)
tolerance_label.pack(pady=15)
craving_label.pack(pady=15)
reset_button.pack()

# Create a frame for the bottom buttons
button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, pady=30)

people_label = tk.Label(button_frame, text = "Are there humans to consume?", font = ("Helvetica", 12))
people_label.pack(pady = 20)
# Add the "Yes" and "No" buttons
yes_button = tk.Button(button_frame, text="Yes", width=20, height = 10, font=("Helvetica", 12), command=act)
yes_button.pack(side=tk.LEFT, padx=10)

no_button = tk.Button(button_frame, text="No", width=20, height = 10, font=("Helvetica", 12), command=dont_act)
no_button.pack(side=tk.RIGHT, padx=10)



root.mainloop()
#a.simulate()
