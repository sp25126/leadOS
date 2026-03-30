import os
import asyncio
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from utils import config_store

def _send_sync(to_email: str, to_name: str, subject: str, body: str) -> dict:
    """Brevo SDK is primary - Falls back to standard SMTP (Gmail/Brevo) if API fails."""
    #   Attempt 1: Brevo API  
    configuration = sib_api_v3_sdk.Configuration()
    api_key = config_store.brevo_key()
    configuration.api_key["api-key"] = api_key

    api = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    sender_email = config_store.sender_email()
    sender_name  = config_store.sender_name()

    email_obj = sib_api_v3_sdk.SendSmtpEmail(
        to      = [{"email": to_email, "name": to_name}],
        sender  = {"name": sender_name, "email": sender_email},
        subject = subject,
        text_content = body,
    )
    try:
        api.send_transac_email(email_obj)
        return {"status": "sent_email", "to": to_email, "provider": "brevo_api"}
    except ApiException as e:
        print(f"  [EmailSender]    Brevo API failed ({e.status}). Falling back to SMTP...")
    except Exception as e:
        print(f"  [EmailSender]    Brevo API Error: {e}. Falling back to SMTP...")

    #   Attempt 2: Standard SMTP Fallback  
    try:
        smtp_host = config_store.get("smtp_host", "SMTP_HOST") or "smtp-relay.brevo.com"
        smtp_port = int(config_store.get("smtp_port", "SMTP_PORT") or "587")
        smtp_user = config_store.get("smtp_user", "SMTP_USER") or config_store.get("gmail_app_user", "GMAIL_APP_USER") or config_store.get("brevo_smtp_user", "BREVO_SMTP_USER") or ""
        smtp_pass = config_store.get("smtp_pass", "SMTP_PASS") or config_store.get("gmail_app_pass", "GMAIL_APP_PASS") or config_store.brevo_key()

        msg = MIMEMultipart()
        msg['From']    = f"{sender_name} <{sender_email}>"
        msg['To']      = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        print(f"  [EmailSender]   Sent via SMTP ({smtp_host})")
        return {"status": "sent_email", "to": to_email, "provider": "smtp"}
    except Exception as e:
        print(f"  [EmailSender]   All email providers failed: {e}")
        return {"status": "email_failed", "to": to_email, "error": str(e)}

async def send_email(to_email: str, to_name: str, subject: str, body: str) -> dict:
    """Async wrapper - runs sync email logic in thread pool."""
    if not to_email or "@" not in to_email:
        return {"status": "email_skipped", "error": "invalid email", "to": to_email}
    return await asyncio.to_thread(_send_sync, to_email, to_name, subject, body)
