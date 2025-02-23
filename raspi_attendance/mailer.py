from dotenv import load_dotenv
import yagmail
import os
from pathlib import Path

load_dotenv()


class Mailer:
    CLIENT_EMAIL = os.getenv("EMAIL")
    PROJECT_ROOT_DIR = Path(__file__).resolve().parent.parent
    OAUTH2_CREDS_FILEPATH = PROJECT_ROOT_DIR / "oauth2_creds.json"

    def __init__(self, receiver_email, receiver_name, file_attachment):
        self.receiver_email = receiver_email
        self.receiver_name = receiver_name
        self.file_attachment = file_attachment

    def send_email(self):
        body = f"Hello {self.receiver_name}.\nAttached in this email is your attendance report."

        yag = yagmail.SMTP(self.CLIENT_EMAIL,
                           oauth2_file=self.OAUTH2_CREDS_FILEPATH)
        yag.send(
            to=self.receiver_email,
            subject="Attendance Report",
            contents=body,
            attachments=self.file_attachment,
        )
