import os
import smtplib
from email.message import EmailMessage
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from utils.auth import verify_api_key

router = APIRouter(tags=["Forms & Notifications"])

# Models
class HelpForm(BaseModel):
    name: str
    email: str
    details: str

class ReferForm(BaseModel):
    referrerName: str
    referrerEmail: str
    referreeName: str
    referreeEmail: str | None = None
    notes: str

class WaitlistForm(BaseModel):
    email: str

def send_notification_email(subject: str, text_content: str):
    """
    Sends an email to saumyavishwam@gmail.com using the webroxofficial@gmail.com 
    SMTP credentials provided in the environment variables.
    """
    sender_email = "webroxofficial@gmail.com"
    receiver_email = "saumyavishwam@gmail.com"
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not app_password:
        print("[Mailer] GMAIL_APP_PASSWORD not set. Cannot send email.")
        return

    msg = EmailMessage()
    msg.set_content(text_content)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        # Connect to Gmail SMTP over SSL
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)
    except Exception as e:
        print(f"[Mailer Error] Failed to send email: {e}")
        raise ValueError("Failed to send email.")

@router.post("/help", dependencies=[Depends(verify_api_key)])
async def submit_help_form(data: HelpForm):
    try:
        subject = f"LeadOS Alert: Project Launch Help requested by {data.name}"
        body = (
            f"  NEW PROJECT LAUNCH HELP REQUEST\n\n"
            f"Name: {data.name}\n"
            f"Email: {data.email}\n\n"
            f"Details / Bottlenecks:\n"
            f"{data.details}\n"
        )
        send_notification_email(subject, body)
        return {"ok": True, "message": "Help request sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refer", dependencies=[Depends(verify_api_key)])
async def submit_refer_form(data: ReferForm):
    try:
        subject = f"LeadOS Alert: New Referral from {data.referrerName}"
        body = (
            f"  NEW REFERRAL BOUNTY LEAD\n\n"
            f"--- Referrer Info ---\n"
            f"Name: {data.referrerName}\n"
            f"Email: {data.referrerEmail}\n\n"
            f"--- Referree Info ---\n"
            f"Name/Business: {data.referreeName}\n"
            f"Email (Optional): {data.referreeEmail or 'Not provided'}\n\n"
            f"--- Notes / Fit ---\n"
            f"{data.notes}\n"
        )
        send_notification_email(subject, body)
        return {"ok": True, "message": "Referral sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/waitlist")
async def submit_waitlist_form(data: WaitlistForm):
    try:
        subject = f"LeadOS Alert: New Deep Research Waitlist Signup"
        body = f"  NEW WAITLIST SIGNUP\n\nEmail: {data.email}\n"
        send_notification_email(subject, body)
        return {"ok": True, "message": "Added to waitlist."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
