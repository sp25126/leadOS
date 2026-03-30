import os
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from utils.auth import verify_api_key

router = APIRouter(tags=["Security & Authentication"])

KEY_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "master.key")

class KeyInitRequest(BaseModel):
    key: str

@router.post("/initialize")
async def initialize_security(data: KeyInitRequest, request: Request):
    """
    Persists the user-defined master key to the backend.
    Allows unauthenticated initialization ONLY IF no key exists.
    """
    current_key = request.headers.get("X-API-Key")
    stored_key = None
    
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            stored_key = f.read().strip()
    
    # If a key exists, you MUST provide it to rotate
    if stored_key and current_key != stored_key:
         raise HTTPException(status_code=403, detail="Security already initialized. Authorization required to rotate.")
    
    # If no key exists, we allow it (the verify_api_key dependency handles the routing logic)
    try:
        os.makedirs(os.path.dirname(KEY_FILE), exist_ok=True)
        with open(KEY_FILE, "w") as f:
            f.write(data.key)
        
        return {"ok": True, "message": "Sovereign security key persisted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to persist key: {str(e)}")

@router.get("/status")
async def get_security_status():
    return {
        "initialized": os.path.exists(KEY_FILE),
        "mode": "sovereign" if os.path.exists(KEY_FILE) else "setup"
    }
