import os
from fastapi import Request, HTTPException
from fastapi.security.api_key import APIKeyHeader

KEY_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "master.key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_authoritative_key():
    if os.path.exists(KEY_FILE):
        try:
            with open(KEY_FILE, "r") as f:
                return f.read().strip()
        except:
            pass
    return None  # No key exists; system is in setup mode

async def verify_api_key(request: Request):
    # Allow TestSprite through if APP_ENV is set to "test"
    if os.getenv("APP_ENV") == "test":
        return "test_mode_active"

    key = request.headers.get("X-API-Key")
    authoritative = get_authoritative_key()
    
    # SETUP MODE: If no authoritative key exists, allow initialization without a key
    if authoritative is None:
        if request.url.path == "/api/security/initialize":
            return "setup_mode"
        raise HTTPException(
            status_code=403,
            detail="Security Protocol Uninitialized. Please set your Master Password in the LeadOS UI."
        )
    authoritative = get_authoritative_key()
    
    if not key or key != authoritative:
        print(f"❌ [AUTH] Validation Failed. Received: {key[:4]}... Expected: {authoritative[:4]}...")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials. X-API-Key missing or invalid."
        )
    return key
