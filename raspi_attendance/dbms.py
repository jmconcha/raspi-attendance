from datetime import datetime
from pathlib import Path
import sqlite3


ROOT_DIR = Path(__file__).resolve().parent
DATABASE = ROOT_DIR / "db/attend_sys.db"

def open_conn():
    conn = sqlite3.connect(DATABASE)
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
    conn.close()

    return student


def get_attendance(student_id):
    query = f"""
SELECT student.email, student.name, subject.name, attendance.time_in
FROM attendance
JOIN student ON student.id = attendance.student
JOIN subject ON subject.id = attendance.subject
WHERE student.id = {student_id}
"""
    conn, cur = open_conn()
    cur.execute(query)
    result_set = cur.fetchall()
    conn.close()

    return result_set


def save_attendance(sel_subj_id, student_id):
    now = datetime.now()
    timein_str = now.strftime("%m-%d-%Y %H:%M")
    conn, cur = open_conn()
    cur.execute(
        f"INSERT INTO attendance (subject, student, time_in) VALUES ({sel_subj_id}, {student_id}, '{timein_str}')")
    cur.execute(f"SELECT time_in FROM attendance WHERE id={cur.lastrowid}")
    timein = cur.fetchone()[0]
    conn.commit()
    conn.close()

    return timein