import os
import csv
import time
from fastapi import APIRouter, Depends
from utils.auth import verify_api_key
from routers.outreach import _task_store

router = APIRouter()

RESULTS_DIR = os.getenv("RESULTS_DIR", "output")

@router.get("/overview", dependencies=[Depends(verify_api_key)])
async def get_stats_overview():
    """
    Returns summary statistics for the dashboard.
    Aggregates data from CSV results and in-memory task store.
    """
    total_leads = 0
    enriched = 0
    ready = 0
    
    # 1. Aggregate leads from CSVs
    if os.path.exists(RESULTS_DIR):
        for fname in os.listdir(RESULTS_DIR):
            if fname.endswith(".csv") and "leads_" in fname:
                try:
                    with open(os.path.join(RESULTS_DIR, fname), newline="", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            total_leads += 1
                            # Enriched: has email or phone
                            if row.get("email") or row.get("phone"):
                                enriched += 1
                            # Ready: status is READY or score >= 7
                            status = row.get("status", "").upper()
                            score = 0
                            try:
                                score = int(row.get("score", row.get("icp_score", 0)))
                            except:
                                pass
                            if status == "READY" or score >= 7:
                                ready += 1
                except:
                    continue

    # 2. Aggregate outreach stats from tasks
    emailed = 0
    wa_sent = 0
    for task in _task_store.values():
        emailed += task.get("email_sent", 0)
        wa_sent += task.get("wa_sent", 0)

    return {
        "total_leads": total_leads,
        "enriched": enriched,
        "ready": ready,
        "emailed": emailed,
        "wa_sent": wa_sent,
        "timestamp": time.time()
    }
