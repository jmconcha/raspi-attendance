from ttkbootstrap.constants import *
from datetime import datetime
from PIL import Image, ImageTk
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import threading
import sys
import os

# fingerprint scanner imports
import serial
import time
import board
import busio
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint

# custom module imports
from mailer import send_email
from dbms import get_subjs, get_student, get_attendance, save_attendance
from utils import save_to_excel

# fingerprint scanner setup
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT
uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

Image.CUBIC = Image.BICUBIC
ROOT_DIR = Path(__file__).resolve().parent
SCREEN_WIDTH = "800x480"


class RaspiAttendance():
    attendance = {"student": {}, "subject": {}, "timein": None}
    proceed = True
    
    
    def __init__(self, isProd):
        root = ttk.Window(themename="darkly")
        root.title("Attendance System")
        root.geometry(SCREEN_WIDTH)  # 7 inch touchscreen resolution
        root.resizable(False, False)  # Disable resizing
        if (isProd):
            root.overrideredirect(True)
            root.attributes('-fullscreen', True)

        # Create a frame
        main_frame = ttk.Frame(root, bootstyle="dark")
        main_frame.pack(padx=20, pady=20, expand=True)

        # Center content horizontally
        main_frame.columnconfigure(0, weight=1)
        
        self.root = root
        self.main_frame = main_frame
        self.style = ttk.Style()
        self.style.configure("Custom.TButton", font=(
            "Arial", 14, "bold"), padding=(20, 10))
        
        self.subjs_dict = get_subjs()
        self.draw_subj_sel()
        self.draw_spin()
    
    
    def start_loop(self):
        self.show_widgets("subj_sel")
        self.scan_fingerprint()
        
        
    def hide_widgets(self):
        for widget in self.main_frame.winfo_children():
            widget.grid_forget()


    def show_widgets(self, group_name):
        if group_name == "subj_sel":
            self.time_label.grid(row=0, column=0, padx=20, pady=20,
                        sticky="ew")
            self.lbl_subj.grid(row=1, column=0, padx=20, sticky="ew")
            self.dropdown_btn.grid(row=2, column=0, padx=20, pady=(5, 20), sticky="ew")
        elif group_name == "spinner":
            self.spinner.grid(row=0, column=0)


    def draw_subj_sel(self):
        def update_time():
            current_time = datetime.now().strftime("%I:%M %p")
            self.time_label.config(text=current_time)
            self.time_label.after(1000, update_time)  # Update time every second
        
        # Add real-time clock label
        self.time_label = ttk.Label(self.main_frame,
                               font=("Helvetica", 90, "bold"), padding=(20, 20, 20, 0), bootstyle="success")
        update_time()  # Start updating the time

        self.lbl_subj = ttk.Label(self.main_frame, text="Select Subject", padding=(0, 20, 0, 0),
                             font=("Arial", 36, "bold"), background="#303030")

        # Dropdown menu
        options = [val for val in self.subjs_dict.keys()]
        
        self.selected_var = tk.StringVar(value=options[0])  # Default selection
        self.dropdown_btn = ttk.Button(
            self.main_frame, text=self.selected_var.get(), style="Custom.TButton", bootstyle="primary",
            command=lambda: self.open_dropdown(options)
        )

        
    def animate_spinner(self):
        current_value = self.spinner.amountusedvar.get()
        # Loop back to 0 after reaching 100
        next_value = (current_value + 20) % 100
        self.spinner.configure(amountused=next_value)
        self.spin_anim_id = self.root.after(
            200, self.animate_spinner)
        
        
    def draw_spin(self):
        self.spinner = ttk.Meter(
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
        
        
    def scan_fingerprint(self):
        def get_fingerprint():
            """Get a finger print image, template it, and see if it matches!"""
            print("Waiting for image...")
            while finger.get_image() != adafruit_fingerprint.OK:
                pass
            print("Templating...")
            self.hide_widgets()
            self.show_widgets("spinner")
            self.animate_spinner()
            if finger.image_2_tz(1) != adafruit_fingerprint.OK:
                return False
            print("Searching...")
            if finger.finger_search() != adafruit_fingerprint.OK:
                return False
            return True

        def threaded_scan():
            if get_fingerprint():
                print("Detected #", finger.finger_id,
                        "with confidence", finger.confidence)
                # student information from DB
                student_info = get_student(finger.finger_id)
                
                # get selected subject from dropdown widgets
                subject_name = self.selected_var.get()
                self.attendance["subject"]["name"] = subject_name
                self.attendance["subject"]["id"] = self.subjs_dict[subject_name]
                
                self.attendance["student"]["id"] = student_info[0]
                self.attendance["student"]["name"] = student_info[2]
                self.attendance["timein"] = save_attendance(self.attendance["subject"]["id"], self.attendance["student"]["id"])
                time.sleep(2) # 2 seconds delay after identifying fingerprint
                self.hide_widgets()
                self.root.after_cancel(self.spin_anim_id)
                self.display_info()
            else:
                print("Finger not found")
                self.spinner.configure(subtext="Fingerprint\nUnrecognized")
                time.sleep(2)
                self.hide_widgets()
                self.root.after_cancel(self.spin_anim_id)
                self.spinner.configure(subtext="Scanning\nFingerprint")
                self.start_loop()
                
        thread = threading.Thread(target=threaded_scan) # Run fingerprint scanning in a separate thread.
        thread.start()
        
        
    def display_info(self): # Load and display an image
        img_path = ROOT_DIR / "img/default.png"
        img_open = Image.open(img_path)
        img_open.thumbnail((200, 200))
        image = ImageTk.PhotoImage(img_open)
        image_label = ttk.Label(self.main_frame, image=image, background="#303030")
        image_label.image = image  # Keep a reference to prevent garbage collection
        image_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        timein = datetime.strptime(self.attendance["timein"], "%m-%d-%Y %H:%M")
        
        # student information frame
        frame_info = ttk.Frame(self.main_frame, bootstyle="dark")
        frame_info.grid(row=0, column=1, padx=(0, 20))

        lbl_name = ttk.Label(frame_info, text=f"Name: {self.attendance['student']['name']}",
                             font=("Arial", 18, "bold"), background="#303030")
        lbl_name.grid(row=0, column=1, pady=(20, 0), sticky="ew")

        lbl_subj = ttk.Label(
            frame_info, text=f"Subject: {self.attendance['subject']['name']}", font=("Arial", 18, "bold"), background="#303030")
        lbl_subj.grid(row=1, column=1, pady=5, sticky="ew")

        lbl_timein = ttk.Label(
            frame_info, text=f"Time-in: {timein.strftime('%I:%M %p')}", font=("Arial", 18, "bold"), background="#303030")
        lbl_timein.grid(row=2, column=1, pady=(0, 20), sticky="ew")

        self.imp_excel_btn = ttk.Button(
            frame_info, text="Export Attendance as Excel File", style="Custom.TButton", command=self.export_attendance)
        self.imp_excel_btn.grid(row=3, column=1, pady=(10, 0), sticky="ew")
        
        time.sleep(6) # seconds delay before closing info display
        if (self.proceed):
            self.hide_widgets()
            self.start_loop()
    
    
    def export_attendance(self):
        self.proceed = False
        self.imp_excel_btn.config(text="Loading...", state="disabled")  # Change text & disable button
        self.imp_excel_btn.update_idletasks()
        student_id = self.attendance['student']['id']
        result_set = get_attendance(student_id)
        stud_email = result_set[0][0]
        stud_name = result_set[0][1]
        file_name = save_to_excel(result_set)
        send_email(stud_email, stud_name, file_name) # send excel file to student email
        os.remove(file_name)
        self.imp_excel_btn.config(text="Export Attendance as Excel File", state="normal")  # Restore button
        tk.messagebox.showinfo("Information", "Attendance report sent to your email address.")
        self.hide_widgets()
        self.start_loop()
        self.proceed = True
    
    
    def open_dropdown(self, options):
        popup = tk.Toplevel(self.root)
        popup.title("Select Subject")
        popup.geometry(SCREEN_WIDTH)
        popup.transient(self.root)

        # Frame to hold Listbox and Scrollbar
        frame = ttk.Frame(popup)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)

        # Listbox with scrollbar support
        listbox = tk.Listbox(frame, font=("Arial", 20), height=10, yscrollcommand=scrollbar.set)
        for option in options:
            listbox.insert(tk.END, option)

        # Configure scrollbar to scroll Listbox
        scrollbar.config(command=listbox.yview)

        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox.bind("<ButtonRelease-1>", lambda e: self.select_item(listbox, popup))

    def select_item(self, listbox, popup):
        """Set the selected item and close the popup."""
        try:
            selected_value = listbox.get(listbox.curselection())
            self.selected_var.set(selected_value)
            self.dropdown_btn.config(text=selected_value)
        except tk.TclError:
            pass
        popup.destroy()
        

def start_app(isProd):
    app = RaspiAttendance(True if isProd == "1" else False)
    app.start_loop()
    app.root.mainloop()


if __name__ == "__main__":
    argv = sys.argv[1] if len(sys.argv) > 1 else 0
    start_app(argv)