#!/usr/bin/python

# import sqlite3

# conn = sqlite3.connect('./attendance.db')
# cur = conn.cursor()
# print("Opened database successfully")

# cur.execute(
#     "INSERT INTO student VALUES (2, 'John Doe', 'Web Programming', '2025-02-20 15:43:36', 2)")

# conn.commit()
# print("Records created successfully")
# conn.close()


# from datetime import datetime


# subjects = [(1, 'IT Major 4', '08:00', '09:30'), (2, 'Software Engineering',
#                                                   '09:30', '11:00'), (3, 'Web Programming', '13:00', '14:30'), (4, 'Computer Programming', '11:00', '12:30')]
# now = datetime.now()

# for subj in subjects:
#     subj_name = subj[1]
#     start_time = subj[2].split(':')
#     end_time = subj[3].split(':')
#     try:
#         start_datetime = datetime.now().replace(
#             hour=int(start_time[0]), minute=int(start_time[1]), second=0, microsecond=0)
#         end_datetime = datetime.now().replace(
#             hour=int(end_time[0]), minute=int(end_time[1]), second=0, microsecond=0)
#         print(
#             f'{subj_name} [{subj[2]}-{subj[3]}] {'' if now >= start_datetime and now <= end_datetime else 'not '}available')
#     except ValueError as e:
#         print(f"Error parsing date: {e}")


# import tkinter as tk
# from tkinter import ttk


# def on_select(event):
#     print(f"Selected value: {combo.get()}")


# root = tk.Tk()
# root.title("Combobox Default Value Troubleshooting")

# options = ["Apple", "Banana", "Cherry"]

# # Create Combobox
# combo = ttk.Combobox(root, values=options, state="readonly")
# combo.pack(pady=10)

# # Set default value using both current() and set() for testing
# try:
#     combo.current(1)  # Should set "Banana"
# except Exception as e:
#     print(f"Error using current(): {e}")

# # try:
# #     combo.set("Banana")  # Should also set "Banana"
# # except Exception as e:
# #     print(f"Error using set(): {e}")

# combo.bind("<<ComboboxSelected>>", on_select)

# # Button to check selected value
# btn = tk.Button(root, text="Get Selected Value",
#                 command=lambda: print(f"Selected: {combo.get()}"))
# btn.pack(pady=5)

# root.mainloop()


# from openpyxl import Workbook

# filename = "hello_world.xlsx"

# workbook = Workbook()
# sheet = workbook.active

# sheet["A1"] = "hello"
# sheet["B1"] = "world!"

# workbook.save(filename=filename)


# from openpyxl import Workbook

# # Sample data
# students = [
#     {"name": "Alice", "age": 20, "grade": "A"},
#     {"name": "Bob", "age": 21, "grade": "B"},
#     {"name": "Charlie", "age": 19, "grade": "A"},
# ]

# # Create a workbook and select the active worksheet
# wb = Workbook()
# ws = wb.active
# ws.title = "Students"

# # Add headers
# ws.append(["Name", "Age", "Grade"])

# # Add student data
# for student in students:
#     ws.append([student["name"], student["age"], student["grade"]])

# # Save the file
# wb.save("students.xlsx")

# print("Excel file 'students.xlsx' created successfully! 🎉")

# import sqlite3

# conn = sqlite3.connect('./attend_sys.db')
# cur = conn.cursor()
# query = """
# SELECT student.name, subject.name, attendance.time_in
# FROM attendance
# JOIN student ON student.id = attendance.student
# JOIN subject ON subject.id = attendance.subject
# """

# cur.execute(query)
# all_data = cur.fetchall()

# # Display the combined data
# for row in all_data:
#     print(row)

# import yagmail
# from dotenv import load_dotenv
# import os

# load_dotenv()

# receiver = "jmconcha.testing@gmail.com"
# body = "Hello there from Yagmail"
# filename = "students.xlsx"

# yag = yagmail.SMTP(os.getenv("EMAIL_USERNAME"), os.getenv("EMAIL_PASSWORD"))
# yag.send(
#     to=receiver,
#     subject="Yagmail test with attachment",
#     contents=body,
#     attachments=filename,
# )


# from pathlib import Path

# # Get the root directory
# ROOT_DIR = Path(__file__).resolve().parent

# # Access a file in the root directory
# file_path = ROOT_DIR / './img/default.png'
# print('*' * 50)
# print(ROOT_DIR)
# print(file_path)
# print(ROOT_DIR.parent)
# print('*' * 50)

# with open(file_path, 'r') as file:
#     print(file.read())
