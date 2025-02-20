import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import PhotoImage
from datetime import datetime
from PIL import Image

Image.CUBIC = Image.BICUBIC


def create_app():
    def update_time(label):
        current_time = datetime.now().strftime("%I:%M:%S %p")
        label.config(text=current_time)
        label.after(1000, update_time, label)  # Update time every second

    def select_subj(frame):
        # Add real-time clock label
        time_label = ttk.Label(frame, font=("Arial", 16))
        time_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        # time_label.pack()
        update_time(time_label)  # Start updating the time

        lbl_subj = ttk.Label(frame, text="Choose subject", font=("Arial", 14))
        lbl_subj.grid(row=1, column=0, padx=20, sticky="ew")
        # Dropdown menu
        options = ["Option 1", "Option 2", "Option 3"]
        selected_option = ttk.StringVar()
        dropdown = ttk.Combobox(
            frame, textvariable=selected_option, values=options, state="readonly", bootstyle="primary")
        dropdown.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        dropdown.current(0)  # Set default selection
        # dropdown.pack()

        def next_step():
            time_label.destroy()
            dropdown.destroy()
            next_button.destroy()
            lbl_subj.destroy()
            scan_fingerprint(frame)
            # display_info(frame)

        # Next step button
        next_button = ttk.Button(frame, text="Next Step", command=next_step)
        next_button.grid(row=4, column=0, padx=20, pady=20, sticky="ew")

    def scan_fingerprint(frame):
        spinner = ttk.Meter(
            frame,
            metersize=180,
            metertype="full",
            padding=5,
            amountused=0,
            stripethickness=10,
            bootstyle="success",
            subtext="Scanning\nFingerprint",
            showtext=False,
            subtextstyle="success",
            subtextfont=("Arial", 14, "bold")
        )
        spinner.grid(row=0, column=0, pady=50)

        # Create a circular spinner animation by rotating the meter value

        def animate_spinner():
            current_value = spinner.amountusedvar.get()
            # Loop back to 0 after reaching 100
            next_value = (current_value + 5) % 100
            spinner.configure(amountused=next_value)
            root.after(200, animate_spinner)  # 5 steps per second

        animate_spinner()

    def display_info(frame):
        # Load and display an image
        # Change to your image file path
        image = PhotoImage(file="./img/profile.png")
        image_label = ttk.Label(frame, image=image)
        image_label.image = image  # Keep a reference to prevent garbage collection
        image_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        # image_label.pack()

        lbl_name = ttk.Label(frame, text="Name: John Doe", font=("Arial", 16))
        lbl_name.grid(row=1, column=0, padx=20, pady=20, sticky="ew")

        lbl_subj = ttk.Label(
            frame, text="Subject: IT Major", font=("Arial", 16))
        lbl_subj.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        lbl_timein = ttk.Label(
            frame, text="Time-in: 08:00 AM", font=("Arial", 16))
        lbl_timein.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

        def next_step():
            image_label.destroy()
            lbl_name.destroy()
            lbl_subj.destroy()
            next_button.destroy()
            select_subj(frame)

        # Next step button
        next_button = ttk.Button(frame, text="Next Step", command=next_step)
        next_button.grid(row=5, column=0, padx=20, pady=20, sticky="ew")

    root = ttk.Window(themename="darkly")
    root.title("Attendance System")
    root.geometry("800x700")  # Default size
    # root.state("zoomed")  # Start in full-screen mode
    root.resizable(False, False)  # Disable resizing

    # Configure grid to expand
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    # Create a frame
    frame = ttk.Frame(root, bootstyle="light")
    # frame.grid(row=0, column=0, sticky="nsew")
    frame.pack(pady=20)

    # Center content horizontally
    frame.columnconfigure(0, weight=1)

    # first step: time display and subjects selection
    select_subj(frame)

    root.mainloop()


if __name__ == "__main__":
    create_app()
