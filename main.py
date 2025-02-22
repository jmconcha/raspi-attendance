from ttkbootstrap.constants import *
from tkinter import PhotoImage
from datetime import datetime
from openpyxl import Workbook
from PIL import Image
import ttkbootstrap as ttk
import sqlite3

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
SELECT student.name, subject.name, attendance.time_in
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
    stud_name = result_set[0][0]

    # Add headers
    ws.append(["Name", "Subject Name", "Time IN"])

    # Add student data
    for student in result_set:
        ws.append(student)

    # Save the file
    wb.save(f"{stud_name.lower().replace(' ', '-')}_attendance.xlsx")


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
            time_label.destroy()
            dropdown.destroy()
            next_button.destroy()
            lbl_subj.destroy()
            scan_fingerprint(frame, sel_subj_id)

        # Next step button
        next_button = ttk.Button(
            frame, text="Scan Fingerprint", command=next_step)
        next_button.grid(row=4, column=0, padx=20, pady=20, sticky="ew")

    def scan_fingerprint(frame, sel_subj_id):
        # Create a circular spinner animation by rotating the meter value
        def animate_spinner():
            current_value = spinner.amountusedvar.get()
            # Loop back to 0 after reaching 100
            next_value = (current_value + 5) % 100
            spinner.configure(amountused=next_value)
            root.after(200, animate_spinner)  # 5 steps per second

        # def info_step():
        #     spinner.destroy()
        #     next_button.destroy()
        #     imp_excel_btn.destroy()
        #     display_info()

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

        animate_spinner()

        # Next step button
        # next_button = ttk.Button(
        #     frame, text="Temp Scan", command=lambda: timein(sel_subj_id))
        next_button = ttk.Button(
            frame, text="Temp Scan", command=lambda: display_info(frame))
        next_button.grid(row=4, column=0, padx=20, pady=20, sticky="ew")

        imp_excel_btn = ttk.Button(
            frame, text="Export Attendance as Excel File", command=lambda: exp_attend(1))
        imp_excel_btn.grid(row=6, column=0, padx=20, pady=20, sticky="ew")

    def display_info(frame):
        # Load and display an image
        # Change to your image file path
        image = PhotoImage(file="./img/default.png")
        image_label = ttk.Label(frame, image=image)
        image_label.image = image  # Keep a reference to prevent garbage collection
        image_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        # image_label.pack()

        lbl_name = ttk.Label(frame, text="Name: John Doe",
                             font=("Arial", 18, "bold"))
        lbl_name.grid(row=1, column=0, padx=20, pady=(20, 0), sticky="ew")

        lbl_subj = ttk.Label(
            frame, text="Subject: IT Major", font=("Arial", 18, "bold"))
        lbl_subj.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        lbl_timein = ttk.Label(
            frame, text="Time-in: 08:00 AM", font=("Arial", 18, "bold"))
        lbl_timein.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

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
    root.geometry("800x480")  # Default size, 7 inch touchscreen resolution
    # root.geometry("800x680")  # Default size
    # root.state("zoomed")  # Start in full-screen mode
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
    select_subj(frame)

    root.mainloop()


if __name__ == "__main__":
    create_app()
