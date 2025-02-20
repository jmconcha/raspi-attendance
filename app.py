import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from datetime import datetime


def update_time(label):
    current_time = datetime.now().strftime("%I:%M:%S %p")
    label.config(text=current_time)
    label.after(1000, update_time, label)  # Update time every second


def create_app():
    root = tk.Tk()
    root.title("Attendance System")
    root.geometry("800x600")  # Default size
    # root.state("zoomed")  # Start in full-screen mode
    root.resizable(False, False)  # Disable resizing

    # Configure grid to expand
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    # Create a frame
    frame = ttk.Frame(root, padding=10)
    frame.grid(row=0, column=0, sticky="nsew")

    # Center content horizontally
    frame.columnconfigure(0, weight=1)

    # Add real-time clock label
    time_label = ttk.Label(frame, font=("Arial", 16))
    time_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
    update_time(time_label)  # Start updating the time

    # Dropdown menu
    options = ["Option 1", "Option 2", "Option 3"]
    selected_option = tk.StringVar()
    dropdown = ttk.Combobox(
        frame, textvariable=selected_option, values=options, state="readonly")
    dropdown.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
    dropdown.current(0)  # Set default selection

    # Load and display an image
    # Change to your image file path
    image = PhotoImage(file="./img/profile.png")
    image_label = ttk.Label(frame, image=image)
    image_label.image = image  # Keep a reference to prevent garbage collection
    image_label.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

    root.mainloop()


if __name__ == "__main__":
    create_app()
