from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from ..config import get_settings
from pathlib import Path
import aiofiles

settings = get_settings()

BASE_DIR = Path(__file__).parent
TEMPLATE_FOLDER = BASE_DIR / "email_templates"

# Ensure the template directory exists
TEMPLATE_FOLDER.mkdir(parents=True, exist_ok=True)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.SMTP_USER,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=TEMPLATE_FOLDER
)

async def send_verification_email(email: str, verification_code: str):
    message = MessageSchema(
        subject="Verify your Meetyfi account",
        recipients=[email],
        body=f"""
        Welcome to Meetyfi!
        
        Your verification code is: {verification_code}
        
        Please use this code to verify your account.
        
        Best regards,
        The Meetyfi Team
        """,
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)

async def send_meeting_notification(email: str, meeting_details: dict):
    message = MessageSchema(
        subject="New Meeting Request",
        recipients=[email],
        body=f"""
        A new meeting has been scheduled:
        
        Date: {meeting_details['date']}
        Time: {meeting_details['time']}
        Client: {meeting_details['client_name']}
        Location: {meeting_details['location']}
        
        Please review and confirm the meeting.
        
        Best regards,
        The Meetyfi Team
        """,
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)