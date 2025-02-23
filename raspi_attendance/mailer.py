from dotenv import load_dotenv
from pathlib import Path
import yagmail
import os

load_dotenv()
CLIENT_EMAIL = os.getenv("EMAIL")
PROJECT_ROOT_DIR = Path(__file__).resolve().parent.parent
OAUTH2_CREDS = PROJECT_ROOT_DIR / "oauth2_creds.json"


def send_email(receiver_email, receiver_name, file_attachment):
    body = f"Hello {receiver_name}.\nAttached in this email is your attendance report."

    yag = yagmail.SMTP(CLIENT_EMAIL,
                       oauth2_file=OAUTH2_CREDS)
    yag.send(
        to=receiver_email,
        subject="Attendance Report",
        contents=body,
        attachments=file_attachment,
    )
