from fastapi import APIRouter, Body, Depends, BackgroundTasks, HTTPException
from utils.auth import verify_api_key as verify_key
from services.batch_sender import run_all_batches
import time
import csv
import os

router = APIRouter()
_task_store: dict = {}  # In-memory task tracking
RESULTS_DIR = os.getenv("RESULTS_DIR", "output")

def _load_leads(session_id: str) -> list[dict]:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    for fname in os.listdir(RESULTS_DIR):
        if session_id in fname and fname.endswith(".csv"):
            fpath = os.path.join(RESULTS_DIR, fname)
            with open(fpath, newline="", encoding="utf-8") as f:
                return list(csv.DictReader(f))
    return []

async def run_outreach_background(task_id: str, session_id: str, batch_wa: int, batch_email: int):
    leads = _load_leads(session_id)
    if not leads:
        _task_store[task_id]["status"] = "error"
        _task_store[task_id]["error"] = "Leads not found"
        return

    _task_store[task_id]["total"] = len(leads)
    _task_store[task_id]["status"] = "running"
    
    async def _progress(info: dict):
        _task_store[task_id].update({
            "wa_sent": info.get("wa_sent", 0),
            "email_sent": info.get("email_sent", 0),
            "skipped": info.get("skipped", 0)
        })

    try:
        results = await run_all_batches(leads, session_id, "both", _progress)
        _task_store[task_id]["status"] = "completed"
    except Exception as e:
        _task_store[task_id]["status"] = "error"
        _task_store[task_id]["error"] = str(e)

@router.post("/start")
async def start_outreach(
    session_id: str = Body(None),
    batch_size_wa: int = Body(default=50),
    batch_size_email: int = Body(default=150),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    _=Depends(verify_key)
):
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
        
    task_id = f"task_{session_id}_{int(time.time())}"
    _task_store[task_id] = {
        "task_id": task_id,
        "session_id": session_id,
        "status": "queued", 
        "wa_sent": 0, 
        "email_sent": 0, 
        "skipped": 0, 
        "total": 0,
        "started_at": time.time()
    }
    background_tasks.add_task(
        run_outreach_background, 
        task_id, session_id, batch_size_wa, batch_size_email
    )
    return _task_store[task_id]

@router.post("/single")
async def start_single_outreach(
    lead: dict = Body(...),
    channel: str = Body(...), # "email" or "whatsapp"
    _=Depends(verify_key)
):
    from services.batch_sender import send_single_email
    from services.whatsapp_client import send_whatsapp, check_wa_ready
    from services.personalizer import generate_whatsapp_message
    
    if channel == "email":
        result = await send_single_email(lead)
        if not result.get("sent"):
            raise HTTPException(status_code=400, detail="Failed to send email. Check if lead has valid email.")
        return {"ok": True, "message": "Email sent"}
        
    elif channel == "whatsapp":
        wa_ready = await check_wa_ready()
        if not wa_ready:
            raise HTTPException(status_code=503, detail="WhatsApp server not ready")
        if not lead.get("phone"):
            raise HTTPException(status_code=400, detail="Lead has no phone number")
            
        msg = await generate_whatsapp_message(lead)
        resp = await send_whatsapp(lead["phone"], msg)
        if resp.get("status") == "sent":
            return {"ok": True, "message": "WhatsApp message sent"}
        else:
            raise HTTPException(status_code=400, detail=resp.get("error", "Failed to send WA message"))
            
    else:
        raise HTTPException(status_code=400, detail="Invalid channel")


@router.get("/tasks")
async def get_all_tasks(_=Depends(verify_key)):
    return list(_task_store.values())

@router.get("/status/{task_id}")
async def get_outreach_status(task_id: str, _=Depends(verify_key)):
    if task_id not in _task_store:
        raise HTTPException(status_code=404, detail="Task not found")
    return _task_store[task_id]
