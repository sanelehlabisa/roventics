from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import csv
import os
import smtplib
from email.mime.text import MIMEText
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

class Inquiry(BaseModel):
    name: str
    email: EmailStr
    message: str


# Load env variables
load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL")

app = FastAPI(
    title="Roventics Backend API",
    description="""
API for receiving website inquiries, storing them, and sending email notifications.
    """,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to secure storage
DATA_FILE = Path("private/inquiries.csv")
DATA_FILE.parent.mkdir(exist_ok=True, parents=True)


def send_notification_email(name, email, message):
    """Send email using SMTP."""
    body = f"""
New Inquiry Received

Name: {name}
Email: {email}
Message:
{message}

Timestamp: {datetime.utcnow().isoformat()}
"""
    msg = MIMEText(body)
    msg["Subject"] = "New Inquiry from Roventics Website"
    msg["From"] = SMTP_USER
    msg["To"] = NOTIFY_EMAIL

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print("Email error:", e)
        return False


@app.post("/api/inquiry")
async def save_inquiry(inquiry: Inquiry):
    name = inquiry.name.strip()
    email = inquiry.email.strip()
    message = inquiry.message.strip()

    timestamp = datetime.utcnow().isoformat()
    new_entry = [timestamp, name, email, message]

    # Save to CSV
    file_exists = DATA_FILE.exists()
    with DATA_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "name", "email", "message"])
        writer.writerow(new_entry)

    # Send email
    email_sent = send_notification_email(name, email, message)

    return {
        "success": True,
        "email_sent": email_sent,
        "message": "Inquiry saved successfully"
    }
