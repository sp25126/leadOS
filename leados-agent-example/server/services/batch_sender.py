import asyncio
import csv
import os
import random
import re
import time
from datetime import datetime

from services.whatsapp_client import send_whatsapp, check_wa_ready
from services.email_sender    import send_email
from services.personalizer    import generate_whatsapp_message, generate_email

# ── Configurable limits ──────────────────────────────────────────
BATCH_WA_LIMIT    = int(os.getenv("BATCH_WA_LIMIT",    "50"))
BATCH_EMAIL_LIMIT = int(os.getenv("BATCH_EMAIL_LIMIT", "150"))
BATCH_GAP_MIN_HRS = float(os.getenv("BATCH_GAP_MIN",  "7.0"))
BATCH_GAP_MAX_HRS = float(os.getenv("BATCH_GAP_MAX",  "8.0"))
WA_MSG_DELAY_MIN  = int(os.getenv("WA_DELAY_MIN",     "25"))   # seconds
WA_MSG_DELAY_MAX  = int(os.getenv("WA_DELAY_MAX",     "50"))   # seconds

RESULTS_DIR = os.getenv("RESULTS_DIR", "output")


def _append_result(results: list, lead: dict, batch: int,
                   channel: str, status: str, message: str):
    results.append({
        **lead,
        "batch":        batch,
        "channel":      channel,
        "status":       status,
        "message_sent": message,
        "sent_at":      datetime.now().isoformat(),
    })


async def run_batch(
    leads: list[dict],
    start_index: int,
    batch_num: int,
    existing_results: list,
    channel: str = "both",      # whatsapp | email | both
    progress_callback=None,     # Optional async fn(dict) for Telegram updates
) -> tuple[list, int]:
    """
    Process one batch. Returns (updated_results, next_start_index).
    Stops when channel limits hit for this batch.
    """
    results    = existing_results.copy()
    wa_sent    = 0
    email_sent = 0
    i          = start_index
    total      = len(leads)
    wa_ready   = await check_wa_ready()

    print(f"\n{'═'*50}")
    print(f"  📦 BATCH {batch_num} | Starting at lead #{i+1}/{total}")
    print(f"  🎯 WA limit: {BATCH_WA_LIMIT} | Email limit: {BATCH_EMAIL_LIMIT}")
    print(f"  📱 WA Server: {'✅ Ready' if wa_ready else '❌ Offline — email only'}")
    print(f"{'═'*50}\n")

    while i < total:
        if wa_sent >= BATCH_WA_LIMIT and email_sent >= BATCH_EMAIL_LIMIT:
            print(f"\n✅ Batch {batch_num} limits reached.")
            break

        lead     = leads[i]
        name     = lead.get("name", f"Lead #{i+1}")
        print(f"[{i+1}/{total}] {name:<30}", end="  ")

        sent    = False
        used_wa = False
        print(f"  [Batch] Processing lead: {name} | Channel filter: {channel}")
        print(f"  [Batch] Lead contact: Phone={lead.get('phone')} | Email={lead.get('email')}")

        # ── WhatsApp ─────────────────────────────────────
        if (channel in ("whatsapp", "both")) and wa_ready and lead.get("phone") and wa_sent < BATCH_WA_LIMIT:
            message = await generate_whatsapp_message(lead)
            resp    = await send_whatsapp(lead["phone"], message)

            if resp.get("status") == "sent":
                wa_sent += 1
                _append_result(results, lead, batch_num, "WhatsApp", "sent", message)
                print(f"→ ✅ WhatsApp [{wa_sent}/{BATCH_WA_LIMIT}]")
                sent    = True
                used_wa = True

            elif resp.get("status") == "not_on_whatsapp":
                print(f"→ ↩️  Not on WA", end="  ")

            elif resp.get("status") in ("wa_server_offline", "wa_server_not_ready"):
                wa_ready = False   # Stop trying WA for this batch
                print(f"→ 📵 WA offline", end="  ")

            else:
                print(f"→ ❌ WA err: {resp.get('error','?')[:30]}", end="  ")

        # ── Email ─────────────────────────────────────
        # Only fallback if sent is still False, OR if channel is 'both' and we want to try both?
        # Standard behavior: if channel is 'both', it tries WA then Email if WA fails.
        # If channel is 'email', it skips WA.
        if (channel in ("email", "both")) and not sent and lead.get("email") and email_sent < BATCH_EMAIL_LIMIT:
            content = await generate_email(lead)
            result  = await send_email(
                lead["email"],
                lead.get("name", ""),
                content["subject"],
                content["body"],
            )
            if result.get("status") == "sent_email":
                email_sent += 1
                _append_result(results, lead, batch_num,
                               "Email", "sent", content["body"])
                print(f"→ 📧 Email [{email_sent}/{BATCH_EMAIL_LIMIT}]")
                sent = True
            else:
                print(f"→ ❌ Email failed: {result.get('error','?')[:30]}")

        # ── No contact at all ──────────────────────────────────
        if not sent:
            _append_result(results, lead, batch_num, "None", "skipped", "")
            if not lead.get("phone") and not lead.get("email"):
                print(f"→ ⚠️  No contact info")

        i += 1

        # Progress callback for Telegram bot
        if progress_callback:
            await progress_callback({
                "current": i, "total": total,
                "wa_sent": wa_sent, "email_sent": email_sent,
                "batch": batch_num,
            })

        # Human-like delay — only after WA messages
        if used_wa and i < total:
            delay = random.randint(WA_MSG_DELAY_MIN, WA_MSG_DELAY_MAX)
            print(f"  ⏳ {delay}s delay...")
            await asyncio.sleep(delay)

    # Batch summary
    skipped = sum(1 for r in results[len(existing_results):]
                  if r.get("status") == "skipped")
    print(f"\n{'─'*50}")
    print(f"  Batch {batch_num} complete:")
    print(f"  📱 WhatsApp : {wa_sent}")
    print(f"  📧 Email    : {email_sent}")
    print(f"  ⚠️  Skipped  : {skipped}")
    print(f"{'─'*50}")

    return results, i


async def run_all_batches(
    leads: list[dict],
    session_id: str,
    channel: str = "both",
    progress_callback=None,
) -> list[dict]:
    """
    Run all batches with automatic gap between them.
    Saves results to CSV after each batch.
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)
    results     = []
    start_index = 0
    batch_num   = 1

    while start_index < len(leads):
        results, next_index = await run_batch(
            leads, start_index, batch_num,
            results, channel, progress_callback
        )
        _save_results(results, session_id)
        start_index = next_index
        batch_num  += 1

        if start_index < len(leads):
            gap_hrs  = random.uniform(BATCH_GAP_MIN_HRS, BATCH_GAP_MAX_HRS)
            gap_secs = gap_hrs * 3600 + random.uniform(-600, 600)
            gap_mins = int(gap_secs / 60)
            print(f"\n⏸️  Pausing {gap_hrs:.1f}h before batch {batch_num}...")
            print(f"⏰ Next batch in ~{gap_mins} minutes\n")
            await asyncio.sleep(gap_secs)

    return results


def is_sendable_email(email: str) -> bool:
    """Basic regex check for email validity."""
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email)) if email else False

async def send_single_email(lead: dict, dry_run: bool = False) -> dict:
    """Single-lead email send wrapper used by email router and test suite."""
    from services.email_sender import send_email
    from services.personalizer import generate_email
    
    email = lead.get("email", "")
    if not email or not is_sendable_email(email):
        return {"lead_id": lead.get("id"), "sent": False, "reason": "invalid_email"}
    
    content = await generate_email(lead)
    subject, body = content["subject"], content["body"]
    
    if dry_run:
        return {"lead_id": lead.get("id"), "sent": False, "dry_run": True,
                "subject": subject, "body_preview": body[:200]}
    
    ok_result = await send_email(email, lead.get("name", ""), subject, body)
    ok = ok_result.get("status") == "sent_email"
    return {"lead_id": lead.get("id"), "sent": ok, "subject": subject}


def _save_results(results: list, session_id: str):
    if not results:
        return
    path = os.path.join(RESULTS_DIR, f"outreach_{session_id}.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
