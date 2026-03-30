from fastapi import APIRouter, Body, Depends
from utils.auth import verify_api_key
from services.llm_gateway import call_llm

router = APIRouter()

@router.post("/chat")
async def agent_chat(payload: dict = Body(...), _=Depends(verify_api_key)):
    message = payload.get("message", "")
    if not message:
        return {"assistant_message": "How can I help you today?", "actions": []}
    
    # Enhanced prompt for copilot behavior
    system_prompt = """
    You are the LeadOS Copilot, a high-performance neural assistant for Lead Hunter Pro.
    You can trigger navigation and system actions by including an 'actions' list in your response.
    
    Routes:
    - /leados/dashboard, /leados/ingest, /leados/leads, /leados/outreach, /leados/whatsapp, /leados/history, /leados/settings
    
    System Actions:
    1. NAVIGATE: {"type": "NAVIGATE", "path": "/route"}
    2. FILL_FORM: {"type": "FILL_FORM", "page": "ingest", "data": {"business_type": "...", "location": "...", "target_service": "..."}}
    3. START_HUNT: {"type": "START_HUNT", "data": {"business_type": "...", "location": "..."}}

    Context/Intents:
    - If user asks to "find", "search", or "hunt" (e.g., "Find cafe leads in NYC"), you MUST trigger BOTH FILL_FORM and START_HUNT immediately in the SAME response. Do NOT ask for more details.
    - If they ask about status or usage, NAVIGATE to dashboard.
    
    Example Response for "Find cafe leads in Pune":
    {
      "assistant_message": "Acknowledge. Calibrating neural filters for Cafe leads in Pune. Initiating discovery sequence...",
      "actions": [
        {"type": "NAVIGATE", "path": "/leados/ingest"},
        {"type": "START_HUNT", "data": {"business_type": "cafe", "location": "Pune"}}
      ]
    }

    Respond ONLY with a valid JSON object.
    """
    
    try:
        resp = await call_llm(f"{system_prompt}\nUser: {message}", expect_json=True)
        # Parse or default
        import json
        data = json.loads(resp)
        return data
    except:
        return {
            "assistant_message": "I'm here to help. What would you like to do?",
            "actions": []
        }
