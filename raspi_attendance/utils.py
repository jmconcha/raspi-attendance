from openpyxl import Workbook
from datetime import datetime
from pathlib import Path
import threading
import time

ROOT_DIR = Path(__file__).resolve().parent

def save_to_excel(result_set):
    # Create a workbook and select the active worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Students"
    stud_name = result_set[0][1]

    # Add headers
    ws.append(["Email", "Name", "Subject Name", "Date", "Time In"])

    # Add student data
    for student in result_set:
        row = list(student)
        timein_str = row[3]
        timein_dt = datetime.strptime(timein_str, "%m-%d-%Y %H:%M")
        date_str = timein_dt.strftime("%B %d, %Y")
        time_str = timein_dt.strftime("%I:%M %p")
        row.pop()
        row.append(date_str)
        row.append(time_str)
        ws.append(row)

    # Save the file
    file_name = ROOT_DIR / \
        f"excel/{stud_name.lower().replace(' ', '-')}_attendance.xlsx"
    wb.save(file_name)
    
    return file_name