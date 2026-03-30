from fastapi import APIRouter, Depends
from utils.auth import verify_api_key
from utils.rate_limiter import quota
from services.whatsapp_client import check_wa_ready

router = APIRouter()

@router.get("/quota/status", dependencies=[Depends(verify_api_key)])
async def get_quota_status():
    status = quota.status()
    
    QUOTA_LIMITS = {
        "gemini":   1500,
        "brevo":    300,
        "overpass": 10000,
        "maps":     200,
        "hunter":   25,
        "abstract": 100,
        "wa":       500,
    }

    quotas = []
    for provider, limit in QUOTA_LIMITS.items():
        # Map source names to provider keys if necessary
        source_map = {
            "gemini": "gemini_ai",
            "brevo": "brevo_email",
            "overpass": "overpass_main",
            "maps": "google_maps",
            "hunter": "hunter_io",
            "abstract": "abstract_api",
            "wa": "wa"
        }
        source = source_map.get(provider, provider)
        stat = status.get(source, {"remaining": limit, "used": 0, "limit": limit})
        used = stat.get("used", 0)
        
        quotas.append({
            "provider": provider,
            "used": min(int(used), limit),
            "limit": limit,
        })

    return {"quotas": quotas}
