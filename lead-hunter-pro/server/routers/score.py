import csv
import os
from fastapi import APIRouter, Request, Query, Depends
from utils.auth import verify_api_key
from services.lead_scorer import score_leads

router = APIRouter(tags=["Scoring"])
RESULTS_DIR = os.getenv("RESULTS_DIR", "output")


@router.post("/run", dependencies=[Depends(verify_api_key)])
async def run_scoring(
    request: Request,
    batchsize: int = Query(50, description="Max leads to score", ge=1)
):
    """
    Scans CSVs for READY leads that lack a score, and runs them through Gemini.
    Uses BYOK Gemini Key from the frontend.
    """
    from utils.request_credentials import extract_credentials
    creds = extract_credentials(request)
    gemini_key = creds.gemini_key
    groq_key = creds.groq_key
    
    os.makedirs(RESULTS_DIR, exist_ok=True)
    all_files = [f for f in os.listdir(RESULTS_DIR) if f.endswith(".csv")]
    
    total_unscored = []
    
    for fname in all_files:
        fpath = os.path.join(RESULTS_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
                for i, row in enumerate(rows):
                    # We want to score leads that have an email (READY) but no score
                    # Or any lead that just came out of enrichment
                    if row.get("status", "").upper() == "READY" and "score" not in row:
                        total_unscored.append({"row": row, "file": fpath, "idx": i, "all_rows": rows})
        except Exception:
            continue
            
    if not total_unscored:
        return {"message": "No unscored READY leads found.", "scored": 0}
        
    # Take up to batchsize
    batch = total_unscored[:batchsize]
    leads_to_score = [item["row"] for item in batch]
    
    # Run scoring (Gemini/Groq)
    scored_leads = await score_leads(leads_to_score, gemini_key=gemini_key, groq_key=groq_key)
    
    # Save back to CSVs
    files_to_save = {}
    for i, item in enumerate(batch):
        fpath = item["file"]
        idx = item["idx"]
        all_rows = item["all_rows"]
        
        all_rows[idx] = scored_leads[i]
        files_to_save[fpath] = {"rows": all_rows}
        
    for fpath, data in files_to_save.items():
        all_keys = set()
        for r in data["rows"]: all_keys.update(r.keys())
        
        with open(fpath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_keys))
            writer.writeheader()
            writer.writerows(data["rows"])
            
    return {"message": "Scoring complete", "scored": len(batch)}
