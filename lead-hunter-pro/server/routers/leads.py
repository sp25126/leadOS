import csv
import os
import time
from typing import Optional, Any

from fastapi import APIRouter, Query, Request, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form
from pydantic import BaseModel, field_validator

from services.source_manager import discover_leads
from services.enricher import run_enrichment_pipeline
from services.lead_scorer import score_leads
from services.email_finder import find_email_for_lead
from utils.auth import verify_api_key
from fastapi.responses import FileResponse
from services.fileimporter import import_file
from datetime import datetime
from database import AsyncSessionLocal
from models import Lead
from sqlalchemy import select
from utils.request_credentials import RequestCredentials, extract_credentials

# In-memory search task store (In production, use Redis)
_search_store: dict = {}

async def _save_leads_db(leads_data: list[dict], session_id: str):
    """Saves leads to Supabase using SQLAlchemy with duplicate check."""
    async with AsyncSessionLocal() as db:
        for data in leads_data:
            # Check if lead already exists by name + city to prevent duplicates
            city = data.get("city") or data.get("location") or ""
            existing = await db.execute(
                select(Lead).where(
                    Lead.name == data["name"],
                    Lead.city == city
                )
            )
            if existing.scalar_one_or_none():
                continue  # Skip duplicate

            lead = Lead(
                name=data.get("name", ""),
                address=data.get("address", ""),
                city=city,
                phone=data.get("phone"),
                email=data.get("email"),
                website=data.get("website"),
                has_website=data.get("has_website", False),
                rating=data.get("rating", 0.0),
                review_count=data.get("review_count", 0),
                types=data.get("types", ""),
                source=data.get("source", ""),
                merged_sources=data.get("merged_sources", ""),
                score=data.get("score", 5),
                priority=data.get("priority", "medium"),
                reason=data.get("reason", ""),
                pain_points=data.get("pain_points", []),
                suggested_opening=data.get("suggested_opening", ""),
                tech_hints=data.get("tech_hints", ""),
                social_media=data.get("social_media", ""),
                website_live=data.get("website_live", False),
                has_contact_form=data.get("has_contact_form", False),
                lat=data.get("lat", 0.0),
                lon=data.get("lon", 0.0),
                session_id=session_id,
                status=data.get("status", "NEW").upper()
            )
            db.add(lead)
        await db.commit()

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10MB limit

router = APIRouter(tags=["Leads"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.getenv("RESULTS_DIR", os.path.join(BASE_DIR, "output"))


#   Request / Response models  
class LeadSearchRequest(BaseModel):
    business_type:  str
    location:       str
    radius_km:      int = 5
    target_service: str = "website and AI automation"

    @field_validator("business_type", "location")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()

    @field_validator("radius_km")
    @classmethod
    def radius_in_range(cls, v: int) -> int:
        if not (1 <= v <= 50):
            raise ValueError("radius_km must be between 1 and 50")
        return v


class LeadResponse(BaseModel):
    name:              str
    address:           str       = ""
    phone:             str       = ""
    email:             str       = ""
    website:           str       = ""
    has_website:       bool      = False
    rating:            float     = 0.0
    review_count:      int       = 0
    types:             str       = ""
    source:            str       = ""
    merged_sources:    str       = ""
    score:             int       = 5
    priority:          str       = "medium"
    reason:            str       = ""
    pain_points:       list[str] = []
    suggested_opening: str       = ""
    tech_hints:        str       = ""
    social_media:      str       = ""
    website_live:      bool      = False
    has_contact_form:  bool      = False
    lat:               float     = 0.0
    lon:               float     = 0.0

    model_config = {"extra": "ignore"}   # Ignore unknown fields from pipeline


class LeadSearchResponse(BaseModel):
    session_id:            str
    total:                 int
    high_priority_count:   int
    medium_priority_count: int
    low_priority_count:    int
    sources_used:          list[str]
    leads:                 list[dict[str, Any]]


#   Endpoints  
@router.post("/upload", dependencies=[Depends(verify_api_key)])
async def upload_leads_file(
    file: UploadFile = File(...),
    target_service: str = Form(default="website and automation"),
    score_with_ai: bool = Form(default=False),
):
    """
    Upload your own leads as CSV, XLSX, XLS, or JSON.
    Returns session_id which can be passed to POST /api/outreach/start
    """
    # 1. Read and validate file
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large. Max 10MB.")
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    # 2. Parse file into leads
    try:
        leads = import_file(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if not leads:
        raise HTTPException(
            status_code=422,
            detail="No valid leads found. Ensure your file has at least a 'name' column."
        )

    # 3. Optional AI scoring
    if score_with_ai and leads:
        try:
            leads = await score_leads(leads, target_service)
        except Exception:
            pass  # Scoring is optional; proceed without it if it fails

    # 4. Save to output CSV with session_id
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in file.filename.split("."))[:30]
    session_id = f"upload_{safe_name}_{timestamp}"
    out_path = os.path.join(RESULTS_DIR, f"leads_{session_id}.csv")

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        if leads:
            writer = csv.DictWriter(f, fieldnames=leads[0].keys())
            writer.writeheader()
            writer.writerows(leads)

    # 5. Summary stats
    with_email = sum(1 for l in leads if l.get("email"))
    with_phone = sum(1 for l in leads if l.get("phone"))
    high = sum(1 for l in leads if l.get("priority") == "high")

    return {
        "session_id": session_id,
        "total": len(leads),
        "with_email": with_email,
        "with_phone": with_phone,
        "high_priority": high,
        "score_applied": score_with_ai,
        "message": f"  {len(leads)} leads imported. Run outreach with session_id: {session_id}",
        "leads_preview": leads[:3],  # Show first 3 as preview
    }


async def run_search_background(task_id: str, req: LeadSearchRequest, gemini_key: str, groq_key: str, google_maps_key: str):
    try:
        ts = str(int(time.time()))
        session_id = f"{req.business_type}_{req.location}_{ts}".replace(" ", "_").lower()
        
        print(f"\n  [Task {task_id}] STARTING HUNT: {req.business_type} in {req.location}")
        print(f" " * 60)

        # Stage 1: Discover
        print(f"  [Task {task_id}] Stage 1/4: Discovering leads...")
        _search_store[task_id]["status"] = "discovering"
        _search_store[task_id]["progress"] = 25
        raw_leads = await discover_leads(req.business_type, req.location, req.radius_km, gmaps_key=google_maps_key)
        
        # Defensive check: Ensure raw_leads is a list of dicts
        raw_leads = [l for l in raw_leads if isinstance(l, dict)] if isinstance(raw_leads, list) else []
        
        print(f"  [Task {task_id}] Discovery complete. Found {len(raw_leads)} potential leads.")

        if not raw_leads:
            print(f"  [Task {task_id}] No leads found. Ending task.")
            _search_store[task_id]["status"] = "completed"
            _search_store[task_id]["progress"] = 100
            _search_store[task_id]["result"] = {
                "session_id": session_id, "total": 0, "leads": [],
                "high_priority_count": 0, "medium_priority_count": 0, "low_priority_count": 0,
                "sources_used": [], "storage_mode": "none"
            }
            return

        # Stage 2-3: Overhaul Enrichment & Scoring (5-Stage Pipeline)
        print(f"  [Task {task_id}] Stage 2/4: Overhauled Enrichment & AI Scoring...")
        _search_store[task_id]["status"] = "enriching"
        _search_store[task_id]["progress"] = 60
        
        from utils.request_credentials import RequestCredentials
        creds = RequestCredentials(
            gemini_key=gemini_key,
            groq_key=groq_key,
            google_maps_key=google_maps_key
        )
        
        pipeline_result = await run_enrichment_pipeline(raw_leads, creds, target_service=req.target_service)
        scored = pipeline_result["leads"]
        scored = [l for l in scored if isinstance(l, dict)]

        # Stage 4: Save
        print(f"  [Task {task_id}] Stage 4/4: Saving results and finalizing...")
        for l in scored: l["session_id"] = session_id # Critical fix: ensure session_id is in CSV
        _save_leads_csv(scored, session_id)
        
        # PERSIST TO SUPABASE (Primary Store)
        storage_mode = "csv_fallback"
        try:
            await _save_leads_db(scored, session_id)
            storage_mode = "supabase"
            print(f"  [Task {task_id}] Leads persisted to Supabase.")
        except Exception as e:
            print(f"  [Task {task_id}] Supabase persistence failed: {e} - falling back to CSV")
        
        sources = list({l.get("source", "") for l in scored if l.get("source")})
        _search_store[task_id]["status"] = "completed"
        _search_store[task_id]["progress"] = 100
        _search_store[task_id]["result"] = {
            "session_id": session_id,
            "total": len(scored),
            "high_priority_count": sum(1 for l in scored if l.get("priority") == "high"),
            "medium_priority_count": sum(1 for l in scored if l.get("priority") == "medium"),
            "low_priority_count": sum(1 for l in scored if l.get("priority") == "low"),
            "sources_used": sources,
            "leads": scored,
            "storage_mode": storage_mode
        }
        print(f"  [Task {task_id}] HUNT SUCCESSFUL. Session: {session_id}")
        print(f" " * 60)

    except Exception as e:
        import traceback
        err_msg = f"  [Task {task_id}] HUNT FAILED: {str(e)}\n{traceback.format_exc()}"
        print(err_msg)
        with open("error.log", "a") as f:
            f.write(f"\n[{int(time.time())}] {err_msg}\n")
        _search_store[task_id]["status"] = "error"
        _search_store[task_id]["error"] = str(e)
        _search_store[task_id]["progress"] = 0

from utils.limiter import limiter

@router.post("/search", dependencies=[Depends(verify_api_key)])
@limiter.limit("5/minute")
async def search_leads(
    req: LeadSearchRequest, 
    request: Request, 
    background_tasks: BackgroundTasks
):
    try:
        task_id = f"search_{int(time.time())}"
        _search_store[task_id] = {
            "task_id": task_id,
            "status": "queued",
            "progress": 0,
            "result": None,
            "error": None
        }
        
        from utils.request_credentials import extract_credentials
        keys = extract_credentials(request)
        gemini_key = keys.gemini_key
        groq_key = keys.groq_key
        google_maps_key = keys.google_maps_key
        
        background_tasks.add_task(
            run_search_background, 
            task_id, 
            req, 
            gemini_key, 
            groq_key, 
            google_maps_key
        )
        
        return {"task_id": task_id}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/status/{task_id}")
async def get_search_status(task_id: str):
    if task_id not in _search_store:
        raise HTTPException(status_code=404, detail="Search task not found")
    return _search_store[task_id]


@router.get("/", dependencies=[Depends(verify_api_key)])
async def get_all_leads(
    status: str | None = Query(None, description="Filter by status (e.g., READY)"),
    limit:  int        = Query(100,  description="Max leads to return"),
    session_id: str | None = Query(None, description="Filter by session ID")
):
    """Get all leads from Supabase (primary) or local CSVs (fallback)."""
    # 1. Try Supabase first
    try:
        async with AsyncSessionLocal() as db:
            query = select(Lead)
            if status:
                query = query.where(Lead.status == status.upper())
            if session_id:
                query = query.where(Lead.session_id == session_id)
            
            query = query.order_by(Lead.created_at.desc()).limit(limit)
            result = await db.execute(query)
            leads = result.scalars().all()
            if leads:
                print(f"  Fetched {len(leads)} leads from Supabase.")
                return [l.to_dict() for l in leads]
    except Exception as e:
        print(f"  Supabase fetch failed, falling back to CSV: {e}")

    # 2. Fallback to CSV files
    os.makedirs(RESULTS_DIR, exist_ok=True)
    all_leads = []
    
    csv_files = []
    for fname in os.listdir(RESULTS_DIR):
        if fname.endswith(".csv") and "leads_" in fname:
            fpath = os.path.join(RESULTS_DIR, fname)
            csv_files.append((fpath, os.path.getmtime(fpath)))
            
    csv_files.sort(key=lambda x: x[1], reverse=True)

    for fpath, _ in csv_files:
        try:
            with open(fpath, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Apply filters
                    row_status = row.get("status", "NEW").upper()
                    if status and status.upper() != row_status:
                        continue
                    if session_id and row.get("session_id") != session_id:
                        continue
                    all_leads.append(row)
        except Exception:
            continue

    return all_leads[:limit]


@router.get("/{session_id}/download")
async def download_leads(session_id: str):
    """Download leads CSV by session ID."""
    os.makedirs(RESULTS_DIR, exist_ok=True)

    for fname in os.listdir(RESULTS_DIR):
        if fname == f"leads_{session_id}.csv":
            fpath = os.path.join(RESULTS_DIR, fname)
            return FileResponse(
                path       = fpath,
                media_type = "text/csv",
                filename   = fname,
            )

    raise HTTPException(
        status_code = 404,
        detail      = f"No CSV found for session '{session_id}'. Run /api/leads/search first."
    )


#   Helpers  
LEAD_CSV_COLUMNS = [
    "session_id", "name", "status", "priority", "score", "email", "phone",
    "website", "address", "city", "rating", "review_count", "types",
    "opening_hours", "social_media", "pain_points", "suggested_opening",
    "reason", "email_quality_score", "email_source", "phone_source",
    "website_live", "tech_hints", "has_contact_form", "source",
    "merged_sources", "lat", "lon"
]

def _save_leads_csv(leads: list[dict], session_id: str) -> str:
    """
    Saves leads to a CSV file with deterministic column order.
    Removes legacy redundant columns.
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)
    fpath = os.path.join(RESULTS_DIR, f"leads_{session_id}.csv")
    if not leads: return fpath
    
    # Drop legacy columns if present
    for l in leads:
        l.pop("emailqualityscore", None)
        l["session_id"] = session_id # Ensure it's there
    
    # Ensure all leads have the required columns
    normalized_leads = []
    for l in leads:
        norm = {k: l.get(k, "") for k in LEAD_CSV_COLUMNS}
        normalized_leads.append(norm)

    # Write to file
    with open(fpath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LEAD_CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(normalized_leads)
    
    return fpath
