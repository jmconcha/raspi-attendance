import sqlite3


class Attendance:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_FILEPATH)
        self.cur = conn.cursor()


    def get_subjects(self):
        result_set = self.cur.execute('SELECT * FROM subject')
        subj_arr = result_set.fetchall()
        self.close()

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


    def get_student(self, fingerprint_id):
        result = self.cur.execute(
            f"Select * from student WHERE fingerprint_id={fingerprint_id}")
        student = result.fetchone()
        self.close()
        print('student info', student)
        stud_info = {}

        return stud_info


    def timein(self, student_id, selected_subject_id):
        student_info = self.get_student(student_id)
        print(f"Selected subjectId: {selected_subject_id}")
        now = datetime.now()
        timein_str = now.strftime("%m-%d-%Y %H:%M")
        print(timein_str)
        conn, cur = open_conn()
        cur.execute(
            f"INSERT INTO attendance (subject, student, time_in) VALUES ({selected_subject_id}, {student_id}, '{timein_str}')")
        conn.commit()
        conn.close()
        
        
    def export_attendance(self, student_id):
        query = f"""
SELECT student.email, student.name, subject.name, attendance.time_in
FROM attendance
JOIN student ON student.id = attendance.student
JOIN subject ON subject.id = attendance.subject
WHERE student.id = {student_id}
"""
        self.cur.execute(query)
        result_set = self.cur.fetchall()
        self.conn.close()

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
        file_name = ROOT_DIR / f"excel/{stud_name.lower().replace(' ', '-')}_attendance.xlsx"
        wb.save(file_name)

        # UNCOMMENT AFTER DEVELOPMENT
        mailer = Mailer(stud_email, stud_name, file_name)
        mailer.send()

    
    def close(self):
        self.conn.close()



