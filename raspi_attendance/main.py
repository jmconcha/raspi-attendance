from ttkbootstrap.constants import *
from tkinter import PhotoImage
from datetime import datetime
from openpyxl import Workbook
from PIL import Image, ImageTk
import ttkbootstrap as ttk
import threading
from pathlib import Path

# UNCOMMENT ON RASPI DEVELOPMENT
from fingerprint import *
from mailer import Mailer
from dbms import Attendance

Image.CUBIC = Image.BICUBIC
ROOT_DIR = Path(__file__).resolve().parent  # Get the root directory
DATABASE_FILEPATH = ROOT_DIR / "db/attend_sys.db"


class AttendanceApp:
    root = None

    def __init__(self):
        self.attendance = Attendance()
        self.style = ttk.Style()
        style.configure("Custom.TButton", font=(
            "Arial", 14, "bold"), padding=(20, 10))


    def start(self):
        self.root = ttk.Window(themename="darkly")
        self.root.title("Attendance System")
        self.root.geometry("800x480")  # 7 inch touchscreen resolution
        self.root.resizable(False, False)  # Disable resizing
        self.root.mainloop()

        # Configure grid to expand
        # self.root.rowconfigure(0, weight=1)
        # self.root.columnconfigure(0, weight=1)

        # Create a main frame
        self.main_frame = ttk.Frame(root, bootstyle="dark")
        self.main_frame.pack(padx=20, pady=20, expand=True)

        # Center content horizontally
        self.main_frame.columnconfigure(0, weight=1)

        # first step: time display and subjects selection
        self.select_subject()


    def clear_frame(self):
        print('*' * 50)
        for widget in self.main_frame.winfo_children():
            print('widget ', widget)
            widget.destroy()


    def update_time(self):
        def update_time():
            current_time = datetime.now().strftime("%I:%M %p")
            time_label.config(text=current_time)
            # Update time every second
            time_label.after(1000, update_time, label)
            
        # Add real-time clock label
        time_label = ttk.Label(self.main_frame,
                               font=("Helvetica", 70, "bold"), padding=(20, 20, 20, 0), bootstyle="success")
        time_label.grid(row=0, column=0, padx=20, pady=20,
                        sticky="ew")
        update_time()  # Start updating the time


    def select_subject(self):
        self.create_time_label();

        lbl_subj = ttk.Label(self.main_frame, text="Select Subject",
                             font=("Arial", 16, "bold"), background="#303030")
        lbl_subj.grid(row=1, column=0, padx=20, sticky="ew")

        # Dropdown menu
        subjs_dict = self.attendance.get_subjects()
        options = [val for val in subjs_dict.keys()]

        dropdown = ttk.Combobox(
            self.main_frame, values=options, state="readonly", bootstyle="primary", font=("Arial", 14))
        dropdown.grid(row=2, column=0, padx=20, pady=(5, 20), sticky="ew")
        dropdown.current(0)  # Set default selection

        def next_step():
            selected_subject_id = subjs_dict[dropdown.get()]
            clear_frame()
            scan_fingerprint(selected_subject_id)

        # Next step button
        next_button = ttk.Button(
            self.main_frame, text="Scan Fingerprint", style="Custom.TButton", command=next_step)
        next_button.grid(row=4, column=0, padx=20, pady=20, sticky="ew")

    def scan_fingerprint(self, selected_subject_id):
        spin_anim_id = None

        # Create a circular spinner animation by rotating the meter value
        def animate_spinner():
            global spin_anim_id
            current_value = spinner.amountusedvar.get()
            # Loop back to 0 after reaching 100
            next_value = (current_value + 5) % 100
            spinner.configure(amountused=next_value)
            spin_anim_id = self.root.after(
                200, animate_spinner)  # 5 steps per second

        def threaded_scan():
            global spin_anim_id
            """Run fingerprint scanning in a separate thread."""
            if get_fingerprint():
                print("Detected #", finger.finger_id,
                      "with confidence", finger.confidence)
                student_info = timein(finger.finger_id, selected_subject_id)
                clear_frame()
                root.after_cancel(spin_anim_id)
                display_info()
            else:
                print("Finger not found")

        spinner = ttk.Meter(
            self.main_frame,
            metersize=400,
            metertype="full",
            meterthickness=20,
            amountused=0,
            stripethickness=5,
            bootstyle="success",
            subtext="Scanning\nFingerprint",
            showtext=False,
            subtextstyle="success",
            subtextfont=("Arial", 35, "bold")
        )

        spinner.grid(row=0, column=0)
        animate_spinner()

        # Run the scan in a separate thread
        # UNCOMMENT ON RASPI DEVELOPMENT
        threading.Thread(target=threaded_scan).start()

    def display_info(self):
        # Load and display an image
        # Change to your image file path
        img = ROOT_DIR / 'img/default.png'
        img_open = Image.open("img/default.png")
        img_open.thumbnail((200, 200))
        image = ImageTk.PhotoImage(img_open)
        image_label = ttk.Label(self.main_frame, image=image, background="#303030")
        image_label.image = image  # Keep a reference to prevent garbage collection
        image_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # student information frame
        frame_info = ttk.Frame(self.main_frame, bootstyle="dark")
        # frame_info.pack(padx=20, pady=20, expand=True)
        frame_info.grid(row=0, column=1, padx=(0, 20))

        lbl_name = ttk.Label(frame_info, text="Name: John Doe",
                             font=("Arial", 18, "bold"), background="#303030")
        lbl_name.grid(row=0, column=1, pady=(20, 0), sticky="ew")

        lbl_subj = ttk.Label(
            frame_info, text="Subject: IT Major", font=("Arial", 18, "bold"), background="#303030")
        lbl_subj.grid(row=1, column=1, pady=5, sticky="ew")

        lbl_timein = ttk.Label(
            frame_info, text="Time-in: 08:00 AM", font=("Arial", 18, "bold"), background="#303030")
        lbl_timein.grid(row=2, column=1, pady=(0, 20), sticky="ew")

        # export attendance report  as excel file
        imp_excel_btn = ttk.Button(
            frame_info, text="Export Attendance as Excel File", style="Custom.TButton", command=lambda: export_attendance(1))
        imp_excel_btn.grid(row=3, column=1, pady=(10, 0), sticky="ew")

        def finish_attend():
            clear_frame()
            select_subject()

        # Next step button
        done_btn = ttk.Button(
            frame, text="Done Attendance", style="Custom.TButton", command=finish_attend)
        done_btn.grid(row=5, column=0, columnspan=2,
                      padx=20, pady=20, sticky="ew")


if __name__ == "__main__":
    attendance_app = AttendanceApp()
    attendance_app.start()
