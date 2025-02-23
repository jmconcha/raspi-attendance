from ttkbootstrap.constants import *
from tkinter import PhotoImage
from datetime import datetime
from openpyxl import Workbook
from PIL import Image, ImageTk
import ttkbootstrap as ttk
import sqlite3
import threading

# UNCOMMENT ON RASPI DEVELOPMENT
# from fingerprint import *
from mailer import send_email

Image.CUBIC = Image.BICUBIC


def open_conn():
    conn = sqlite3.connect('./attend_sys.db')
    cur = conn.cursor()

    return (conn, cur)


def get_subjs():
    conn, cur = open_conn()
    result_set = cur.execute('SELECT * FROM subject')
    subj_arr = result_set.fetchall()
    conn.close()

    # get available subjects based on current time=
    now = datetime.now()
    avail_subjs = {}
    for subj in subj_arr:
        subj_id = subj[0]
        subj_name = subj[1]
        start_time = subj[2].split(':')
        end_time = subj[3].split(':')
        try:
            start_datetime = datetime.now().replace(
                hour=int(start_time[0]), minute=int(start_time[1]), second=0, microsecond=0)
            end_datetime = datetime.now().replace(
                hour=int(end_time[0]), minute=int(end_time[1]), second=0, microsecond=0)
            if now >= start_datetime and now <= end_datetime:
                avail_subjs[subj_name] = subj_id

        except ValueError as e:
            print(f"Error parsing date: {e}")

    return avail_subjs


def get_student(fingerprint_id):
    conn, cur = open_conn()
    result = cur.execute(
        f"Select * from student WHERE fingerprint_id={fingerprint_id}")
    student = result.fetchone()
    student_id = student[0]
    conn.close()

    return student_id


# temporary function replacement of fingerprint scanning
def timein(sel_subj_id):
    temp_stud_id = 1
    get_student(temp_stud_id)
    print(f"Selected subjectId: {sel_subj_id}")
    now = datetime.now()
    timein_str = now.strftime("%m-%d-%Y %H:%M")
    print(timein_str)
    conn, cur = open_conn()
    cur.execute(
        f"INSERT INTO attendance (subject, student, time_in) VALUES ({sel_subj_id}, {temp_stud_id}, '{timein_str}')")
    conn.commit()
    conn.close()


def exp_attend(stud_id):
    query = f"""
SELECT student.email, student.name, subject.name, attendance.time_in
FROM attendance
JOIN student ON student.id = attendance.student
JOIN subject ON subject.id = attendance.subject
WHERE student.id = {stud_id}
"""
    conn, cur = open_conn()
    cur.execute(query)
    result_set = cur.fetchall()
    conn.close()

    # Create a workbook and select the active worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Students"
    stud_email = result_set[0][0]
    stud_name = result_set[0][1]

    # Add headers
    ws.append(["Name", "Subject Name", "Time In"])

    # Add student data
    for student in result_set:
        row = list(student)
        row.pop(0)
        ws.append(row)

    # Save the file
    file_name = f"{stud_name.lower().replace(' ', '-')}_attendance.xlsx"
    wb.save(file_name)

    # UNCOMMENT AFTER DEVELOPMENT
    send_email(stud_email, stud_name, file_name)


def clear_frame(frame):
    print('*' * 50)
    for widget in frame.winfo_children():
        print('widget ', widget)
        widget.destroy()


def create_app():
    def update_time(label):
        current_time = datetime.now().strftime("%I:%M %p")
        label.config(text=current_time)
        label.after(1000, update_time, label)  # Update time every second

    def select_subj(frame):
        # Add real-time clock label
        time_label = ttk.Label(frame,
                               font=("Helvetica", 70, "bold"), padding=(20, 20, 20, 0), bootstyle="success")
        time_label.grid(row=0, column=0, padx=20, pady=20,
                        sticky="ew")
        update_time(time_label)  # Start updating the time

        lbl_subj = ttk.Label(frame, text="Select Subject",
                             font=("Arial", 16, "bold"), background="#303030")
        lbl_subj.grid(row=1, column=0, padx=20, sticky="ew")

        # Dropdown menu
        subjs_dict = get_subjs()
        options = [val for val in subjs_dict.keys()]

        dropdown = ttk.Combobox(
            frame, values=options, state="readonly", bootstyle="primary", font=("Arial", 14))
        dropdown.grid(row=2, column=0, padx=20, pady=(5, 20), sticky="ew")
        dropdown.current(0)  # Set default selection

        def next_step():
            sel_subj_id = subjs_dict[dropdown.get()]
            clear_frame(frame)
            scan_fingerprint(frame, sel_subj_id)

        # Next step button
        next_button = ttk.Button(
            frame, text="Scan Fingerprint", style="Custom.TButton", command=next_step)
        next_button.grid(row=4, column=0, padx=20, pady=20, sticky="ew")

    def scan_fingerprint(frame, sel_subj_id):
        spin_anim_id = None

        # Create a circular spinner animation by rotating the meter value
        def animate_spinner():
            global spin_anim_id
            current_value = spinner.amountusedvar.get()
            # Loop back to 0 after reaching 100
            next_value = (current_value + 5) % 100
            spinner.configure(amountused=next_value)
            spin_anim_id = root.after(
                200, animate_spinner)  # 5 steps per second

        def threaded_scan():
            global spin_anim_id
            """Run fingerprint scanning in a separate thread."""
            if get_fingerprint():
                print("Detected #", finger.finger_id,
                      "with confidence", finger.confidence)
                root.after_cancel(spin_anim_id)
                clear_frame(frame)
                display_info(frame)
            else:
                print("Finger not found")

        spinner = ttk.Meter(
            frame,
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
        # threading.Thread(target=threaded_scan).start()

    def display_info(frame):
        # Load and display an image
        # Change to your image file path
        img_open = Image.open("./img/default.png")
        img_open.thumbnail((200, 200))
        image = ImageTk.PhotoImage(img_open)
        image_label = ttk.Label(frame, image=image, background="#303030")
        image_label.image = image  # Keep a reference to prevent garbage collection
        image_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # student information frame
        frame_info = ttk.Frame(frame, bootstyle="dark")
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
            frame_info, text="Export Attendance as Excel File", style="Custom.TButton", command=lambda: exp_attend(1))
        imp_excel_btn.grid(row=3, column=1, pady=(10, 0), sticky="ew")

        def finish_attend():
            clear_frame(frame)
            select_subj(frame)

        # Next step button
        done_btn = ttk.Button(
            frame, text="Done Attendance", style="Custom.TButton", command=finish_attend)
        done_btn.grid(row=5, column=0, columnspan=2,
                      padx=20, pady=20, sticky="ew")

    root = ttk.Window(themename="darkly")
    style = ttk.Style()
    style.configure("Custom.TButton", font=(
        "Arial", 14, "bold"), padding=(20, 10))
    root.title("Attendance System")
    root.geometry("800x480")  # 7 inch touchscreen resolution
    # root.geometry("800x680")  # temp size for developing
    root.resizable(False, False)  # Disable resizing

    # Configure grid to expand
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    # Create a frame
    frame = ttk.Frame(root, bootstyle="dark")
    frame.pack(padx=20, pady=20, expand=True)

    # Center content horizontally
    frame.columnconfigure(0, weight=1)

    # first step: time display and subjects selection
    # select_subj(frame)

    # REMOVE AFTER DEVELOPMENT
    display_info(frame)
    # scan_fingerprint(frame, 1)

    root.mainloop()


if __name__ == "__main__":
    create_app()
