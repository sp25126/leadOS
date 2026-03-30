import os
from fastapi import Request
from dataclasses import dataclass

@dataclass
class RequestCredentials:
    gemini_key: str
    groq_key: str
    openrouter_key: str
    google_maps_key: str
    brevo_key: str
    hunter_key: str
    sender_email: str
    sender_name: str

    def __init__(
        self, gemini_key="", groq_key="", openrouter_key="", google_maps_key="",
        brevo_key="", hunter_key="", sender_email="", sender_name="LeadOS"
    ):
        self.gemini_key = gemini_key
        self.groq_key = groq_key
        self.openrouter_key = openrouter_key
        self.google_maps_key = google_maps_key
        self.brevo_key = brevo_key
        self.hunter_key = hunter_key
        self.sender_email = sender_email
        self.sender_name = sender_name
        
        # Log key availability (masked for security)
        def mask(k): return f"{k[:4]}...{k[-4:]}" if len(k) > 10 else ("YES" if k else "NO")
        print(f"[AUTH] BYOK Keys Loaded: Gemini={mask(gemini_key)}, Groq={mask(groq_key)}, GMaps={mask(google_maps_key)}")

def extract_credentials(request: Request) -> RequestCredentials:
    """
    Priority order: X- request header -> .env fallback
    This enables full BYOK without storing any user key server-side.
    """
    return RequestCredentials(
        gemini_key=request.headers.get("X-Gemini-Key") or os.getenv("GEMINI_API_KEY", ""),
        groq_key=request.headers.get("X-Groq-Key") or os.getenv("GROQ_API_KEY", ""),
        openrouter_key=request.headers.get("X-Openrouter-Key") or os.getenv("OPENROUTER_API_KEY", ""),
        google_maps_key=request.headers.get("X-Google-Maps-Key") or os.getenv("GOOGLE_MAPS_API_KEY", ""),
        brevo_key=request.headers.get("X-Brevo-Key") or os.getenv("BREVO_API_KEY", ""),
        hunter_key=request.headers.get("X-Hunter-Key") or os.getenv("HUNTER_API_KEY", ""),
        sender_email=request.headers.get("X-Sender-Email") or os.getenv("SENDER_EMAIL", ""),
        sender_name=request.headers.get("X-Sender-Name") or os.getenv("SENDER_NAME", "LeadOS"),
    )
