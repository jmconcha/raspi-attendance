from dotenv import load_dotenv
import yagmail
import os

load_dotenv()
CLIENT_EMAIL = os.getenv("EMAIL")


def send_email(receiver_email, receiver_name, file_attachment):
    body = f"Hello {receiver_name}.\nAttached in this email is your attendance report."

    yag = yagmail.SMTP(CLIENT_EMAIL,
                       oauth2_file="./oauth2_creds.json")
    yag.send(
        to=receiver_email,
        subject="Attendance Report",
        contents=body,
        attachments=file_attachment,
    )
