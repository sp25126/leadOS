import csv
import os
from fastapi import APIRouter, Request, Query, Depends
from utils.auth import verify_api_key
from services.enricher import enrich_all

router = APIRouter(tags=["Enrichment"])
RESULTS_DIR = os.getenv("RESULTS_DIR", "output")


@router.post("/run", dependencies=[Depends(verify_api_key)])
async def run_enrichment(
    request: Request,
    batchsize: int = Query(20, description="Max NEW leads to enrich", ge=1)
):
    """
    Scans CSVs for NEW leads and runs them through the enricher pipeline.
    Uses BYOK Snov/GetProspect keys if provided from the frontend.
    """
    #   Keys from BYOK Headers or Environment  
    from utils.request_credentials import extract_credentials
    creds = extract_credentials(request)
    
    os.makedirs(RESULTS_DIR, exist_ok=True)
    all_files = [f for f in os.listdir(RESULTS_DIR) if f.endswith(".csv")]
    
    total_new = []
    file_map = {}  # Keep track of which lead belongs to which file for saving
    
    # Find NEW leads
    for fname in all_files:
        fpath = os.path.join(RESULTS_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
                for i, row in enumerate(rows):
                    if row.get("status", "NEW").upper() == "NEW":
                        total_new.append({"row": row, "file": fpath, "idx": i, "all_rows": rows})
        except Exception:
            continue
            
    if not total_new:
        return {"message": "No NEW leads found to enrich.", "enriched": 0}
        
    # Take up to batchsize
    batch = total_new[:batchsize]
    leads_to_enrich = [item["row"] for item in batch]
    
    # Run enrichment
    enriched_leads = await enrich_all(leads_to_enrich, concurrency=5, hunter_key=creds.hunter_key, gmaps_key=creds.google_maps_key)
    
    # Save back to CSVs
    files_to_save = {}
    for i, item in enumerate(batch):
        fpath = item["file"]
        idx = item["idx"]
        all_rows = item["all_rows"]
        
        all_rows[idx] = enriched_leads[i] # Update the row
        files_to_save[fpath] = {"rows": all_rows, "fieldnames": enriched_leads[i].keys()}
        
    for fpath, data in files_to_save.items():
        # Ensure all rows have all fieldnames (enrichment adds new ones)
        all_keys = set()
        for r in data["rows"]: all_keys.update(r.keys())
        
        with open(fpath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_keys))
            writer.writeheader()
            writer.writerows(data["rows"])
            
    return {"message": "Enrichment complete", "enriched": len(batch)}
