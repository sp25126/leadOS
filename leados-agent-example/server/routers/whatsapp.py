import os
import httpx
from fastapi import APIRouter, Depends, HTTPException
from utils.auth import verify_api_key

router = APIRouter()
WA_URL = os.getenv("WA_SERVER_URL", "http://localhost:3001")

@router.get("/health")
async def wa_health():
    try:
        async with httpx.AsyncClient(timeout=3) as c:
            r = await c.get(f"{WA_URL}/health")
            if r.status_code != 200:
                return {"connected": False, "error": f"WA Server returned {r.status_code}"}
            data = r.json()
            return {
                "connected": data.get("ready", False),
                "qr_available": data.get("qr_generated", False),
                "timestamp": data.get("timestamp")
            }
    except Exception as e:
        return {"connected": False, "error": str(e)}

@router.get("/qr")
async def wa_qr(_=Depends(verify_api_key)):
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{WA_URL}/qr")
            if r.status_code != 200:
                return {"qr_base64": None, "error": "QR not available from server"}
            return r.json()
    except Exception as e:
        return {"qr_base64": None, "error": str(e)}

@router.post("/send")
async def wa_send(payload: dict, _=Depends(verify_api_key)):
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(f"{WA_URL}/send", json=payload)
            return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to relay to WA server: {str(e)}")
