from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from utils import config_store
from utils.auth import verify_api_key  # only admin/authorized can update config

router = APIRouter(prefix="/api/admin", tags=["config"])

class ConfigUpdateRequest(BaseModel):
    gemini_key:     Optional[str] = None
    gmaps_key:      Optional[str] = None
    hunter_key:     Optional[str] = None
    brevo_key:      Optional[str] = None
    sender_email:   Optional[str] = None
    sender_name:    Optional[str] = None
    groq_key:       Optional[str] = None
    telegram_token: Optional[str] = None

@router.get("/config")
async def get_config(_=Depends(verify_api_key)):
    """Return current config with masked values for display."""
    return {
        "status": "ok",
        "config": config_store.get_all_keys(),
        "env_fallbacks": {
            "gemini_key":     bool(config_store.gemini_key()),
            "gmaps_key":      bool(config_store.gmaps_key()),
            "hunter_key":     bool(config_store.hunter_key()),
            "brevo_key":      bool(config_store.brevo_key()),
            "sender_email":   bool(config_store.sender_email()),
            "sender_name":    bool(config_store.sender_name()),
            "groq_key":       bool(config_store.groq_key()),
            "telegram_token": bool(config_store.telegram_token()),
        }
    }

@router.post("/config")
async def update_config(
    body: ConfigUpdateRequest,
    _=Depends(verify_api_key)
):
    """
    Save API keys to server-side config.json.
    Only non-empty fields are updated. Existing keys are preserved.
    """
    config_store.update(body.model_dump(exclude_none=True))
    return { "status": "ok", "message": "Configuration saved" }

@router.delete("/config/{key}")
async def delete_config_key(
    key: str,
    _=Depends(verify_api_key)
):
    """Remove a single key from config (reverts to .env fallback)."""
    # Accessing private members for deletion as it's a specialized admin operation
    from utils.config_store import _cache, _save
    if key in _cache:
        _cache.pop(key, None)
        _save(_cache)
        return { "status": "ok", "message": f"{key} removed from config" }
    else:
        raise HTTPException(status_code=404, detail=f"Key {key} not found in persistent config")
