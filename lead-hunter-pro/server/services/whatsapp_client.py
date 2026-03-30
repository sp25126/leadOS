import httpx
from utils import config_store

def _get_wa_url():
    return config_store.get("wa_server_url", "WA_SERVER_URL") or "http://localhost:3001"

TIMEOUT       = httpx.Timeout(60.0, connect=5.0)


async def check_wa_ready() -> bool:
    """Returns True if wa-server is running and WhatsApp is connected."""
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
            resp = await client.get(f"{_get_wa_url()}/health")
            return resp.status_code == 200 and resp.json().get("ready", False)
    except Exception:
        return False


async def send_whatsapp(phone: str, message: str) -> dict:
    """
    Send a single WhatsApp message via wa-server.
    Returns status dict - never raises.
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.post(
                f"{_get_wa_url()}/send",
                json={"phone": phone, "message": message},
                headers={"X-API-Key": config_store.get("internal_api_key", "X-API-Key")}
            )
            if resp.status_code == 403:
                return {"status": "error", "error": "WA Server authentication failed (Invalid X-API-Key)"}
            if resp.status_code == 503:
                return {"status": "wa_server_not_ready", "phone": phone}
            return resp.json()
    except httpx.ConnectError:
        return {"status": "wa_server_offline", "phone": phone,
                "error": "WA server not running - start wa-server/index.js"}
    except httpx.TimeoutException:
        return {"status": "wa_timeout", "phone": phone}
    except Exception as e:
        return {"status": "error", "phone": phone, "error": str(e)}
