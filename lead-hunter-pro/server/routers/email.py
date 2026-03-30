"""
routers/email.py
 
Email diagnostics + smart outreach dispatch.
Operates over the file-based CSV lead store (output/leads_*.csv).
"""
import csv
import os
import time
from typing import Any

from fastapi import APIRouter, Query, Request, HTTPException, Depends
from services.batch_sender import run_all_batches, send_single_email
from utils.auth import verify_api_key

router = APIRouter(tags=["Email Outreach"])

RESULTS_DIR = os.getenv("RESULTS_DIR", "output")

# Local parts that indicate a generic/junk catch-all address
JUNK_LOCAL_PARTS = {
    "info", "contact", "hello", "sales", "support",
    "customercare", "hr", "admin",
}

REGISTRAR_EMAILS = {
    "root@", "admin@", "webmaster@", "postmaster@", "hostmaster@",
    "@onlydomains.com", "@godaddy.com", "@namecheap.com"
}


#   Helpers  

def _load_all_ready_leads() -> list[dict]:
    """
    Load every lead from every CSV in RESULTS_DIR whose status is READY
    (or has a non-empty email and no explicit failing status).
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)
    leads: list[dict] = []
    for fname in os.listdir(RESULTS_DIR):
        if not fname.endswith(".csv"):
            continue
        fpath = os.path.join(RESULTS_DIR, fname)
        try:
            with open(fpath, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    status = row.get("status", "READY").upper()
                    email  = row.get("email", "").strip()
                    # Consider a lead READY if: status is READY or (no status col and email exists)
                    if email and status not in {"UNENRICHABLE", "ENRICHMENT_FAILED", "SENT"}:
                        leads.append(row)
        except Exception:
            continue
    return leads


def _is_junk_local(email: str) -> bool:
    if "@" not in email:
        return False
    local = email.split("@")[0].lower().strip()
    return local in JUNK_LOCAL_PARTS


def _icp_score(lead: dict) -> int:
    """Parse icpscore / score field, default 0."""
    for field in ("icpscore", "score"):
        try:
            return int(float(lead.get(field, 0) or 0))
        except (ValueError, TypeError):
            continue
    return 0


def _is_registrar_email(email: str) -> bool:
    email = email.lower().strip()
    for pattern in REGISTRAR_EMAILS:
        if pattern.startswith("@"):
            if email.endswith(pattern): return True
        else:
            if email.startswith(pattern): return True
    return False


#   Endpoints  

@router.get("/skip-report")
async def skip_report() -> dict[str, Any]:
    """
    Analyse all READY leads and report how many would be filtered as junk.
    Schema: {total_ready, sendable, skipped, breakdown: {junk_local, no_email}}
    """
    all_leads  = _load_all_ready_leads()
    total      = len(all_leads)

    junk_local_samples: list[str] = []
    junk_local_count   = 0
    no_email_count     = 0

    for lead in all_leads:
        email = lead.get("email", "").strip()
        if not email:
            no_email_count += 1
        elif _is_junk_local(email):
            junk_local_count += 1
            if len(junk_local_samples) < 10:
                junk_local_samples.append(email)

    skipped  = junk_local_count + no_email_count
    sendable = total - skipped

    return {
        "total_ready": total,
        "sendable":    max(sendable, 0),
        "skipped":     skipped,
        "breakdown": {
            "junk_local": {
                "count":   junk_local_count,
                "samples": junk_local_samples,
            },
            "no_email": {
                "count": no_email_count,
            },
        },
    }


@router.post("/send-run-by-source", dependencies=[Depends(verify_api_key)])
async def send_run_by_source(
    request:    Request,
    source:     str  = Query(default="all"),
    batch_size: int  = Query(default=10, alias="batchsize"),
    dry_run:    bool = Query(default=True, alias="dryrun"),
    min_score:  int  = Query(default=0,  ge=0),
) -> dict[str, Any]:
    """
    Group READY leads by source, filter junk, then run email outreach through batch_sender.
    """
    #   BYOK Authentication  
    from utils.request_credentials import extract_credentials
    creds = extract_credentials(request)
    
    if creds.brevo_key:
        os.environ["BREVO_API_KEY"] = creds.brevo_key
    if creds.sender_email:
        os.environ["SENDER_EMAIL"] = creds.sender_email
    if creds.sender_name:
        os.environ["SENDER_NAME"] = creds.sender_name
        
    all_leads = _load_all_ready_leads()

    # Filter by source and junk/score
    leads = []
    for lead in all_leads:
        if source != "all" and (lead.get("source") or "unknown") != source:
            continue
        email = lead.get("email", "").strip()
        if not email or _is_junk_local(email):
            continue
        if _icp_score(lead) < min_score:
            continue
        leads.append(lead)

    if not leads:
        return {
            "mode": "dryrun" if dry_run else "live",
            "attempted": 0,
            "details": {},
            "message": f"No leads found for source: {source}"
        }

    # Sort and cap
    leads.sort(key=_icp_score, reverse=True)
    batch = leads[:batch_size]
    
    #   Summary for UI  
    details = {}
    for l in batch:
        src = l.get("source", "unknown") or "unknown"
        details[src] = details.get(src, 0) + 1

    if dry_run:
        return {
            "mode":      "dryrun",
            "attempted": len(batch),
            "details":   details,
        }

    #   REAL SEND  
    session_id = f"smart_run_{int(time.time())}"
    
    results = await run_all_batches(
        leads=batch,
        session_id=session_id
    )

    sent = sum(1 for r in results if r.get("status") == "sent")
    failed = sum(1 for r in results if r.get("status") in ("failed", "error"))

    return {
        "mode":      "live",
        "session_id": session_id,
        "attempted": len(batch),
        "sent":      sent,
        "failed":    failed,
        "details":   details,
    }


@router.post("/send-test-to-self", dependencies=[Depends(verify_api_key)])
async def send_test_to_self(request: Request):
    """
    Send a single test email to the SENDER_EMAIL configured in .env.
    Confirms SMTP/Brevo connectivity.
    """
    sender = os.getenv("SENDER_EMAIL")
    if not sender:
        raise HTTPException(status_code=500, detail="SENDER_EMAIL not configured in .env")
    
    #   BYOK Authentication  
    brevo_key = request.headers.get("X-Brevo-Key")
    if brevo_key:
        os.environ["BREVO_API_KEY"] = brevo_key

    test_lead = {
        "name": "Test User",
        "email": sender,
        "first_name": "Developer"
    }
    
    try:
        ok = await send_single_email(test_lead)
        if ok:
            return {"ok": True, "message": f"Test email sent to {sender}"}
        else:
            return {"ok": False, "message": "Failed to send test email. Check logs."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent", dependencies=[Depends(verify_api_key)])
async def get_recent_sends(limit: int = 10):
    """
    Returns latest emailed leads with status: SENT/EMAILED.
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)
    recent = []
    
    # Simple walk of CSVs to find EMAILED leads
    for fname in os.listdir(RESULTS_DIR):
        if not fname.endswith(".csv"):
            continue
        fpath = os.path.join(RESULTS_DIR, fname)
        try:
            with open(fpath, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    if row.get("status", "").upper() in ("SENT", "EMAILED"):
                        recent.append(row)
                        if len(recent) >= limit * 3: # Buffer for sorting
                            break
        except Exception:
            continue
            
    # Sort by timestamp if available, else just cap
    recent.reverse()
    return recent[:limit]
