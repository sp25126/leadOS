import os
import asyncio
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def _send_sync(to_email: str, to_name: str, subject: str, body: str) -> dict:
    """Brevo SDK is primary — Falls back to standard SMTP (Gmail/Brevo) if API fails."""
    # ── Attempt 1: Brevo API ──────────────────────────────────────────
    configuration = sib_api_v3_sdk.Configuration()
    api_key = os.getenv("BREVO_API_KEY") or os.getenv("BREVO_SMTP_KEY", "")
    configuration.api_key["api-key"] = api_key

    api = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    sender_email = os.getenv("SENDER_EMAIL") or os.getenv("FROM_EMAIL", "")
    sender_name  = os.getenv("SENDER_NAME")  or os.getenv("FROM_NAME", "Lead Hunter")

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
        print(f"  [EmailSender] ⚠️  Brevo API failed ({e.status}). Falling back to SMTP...")
    except Exception as e:
        print(f"  [EmailSender] ⚠️  Brevo API Error: {e}. Falling back to SMTP...")

    # ── Attempt 2: Standard SMTP Fallback ──────────────────────────────
    try:
        smtp_host = os.getenv("SMTP_HOST") or os.getenv("BREVO_SMTP_HOST", "smtp-relay.brevo.com")
        smtp_port = int(os.getenv("SMTP_PORT") or os.getenv("BREVO_SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER") or os.getenv("GMAIL_APP_USER") or os.getenv("BREVO_SMTP_USER", "")
        smtp_pass = os.getenv("SMTP_PASS") or os.getenv("GMAIL_APP_PASS") or os.getenv("BREVO_SMTP_KEY", "")

        msg = MIMEMultipart()
        msg['From']    = f"{sender_name} <{sender_email}>"
        msg['To']      = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        print(f"  [EmailSender] ✅ Sent via SMTP ({smtp_host})")
        return {"status": "sent_email", "to": to_email, "provider": "smtp"}
    except Exception as e:
        print(f"  [EmailSender] ❌ All email providers failed: {e}")
        return {"status": "email_failed", "to": to_email, "error": str(e)}

async def send_email(to_email: str, to_name: str, subject: str, body: str) -> dict:
    """Async wrapper — runs sync email logic in thread pool."""
    if not to_email or "@" not in to_email:
        return {"status": "email_skipped", "error": "invalid email", "to": to_email}
    return await asyncio.to_thread(_send_sync, to_email, to_name, subject, body)
