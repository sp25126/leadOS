import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

# Load environment variables from .env file
load_dotenv()

@dataclass
class Settings:
    # Database & Redis
    DATABASE_URL: str
    REDIS_URL: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # AI
    GEMINI_API_KEY: str

    # Outreach (SMTP)
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str
    FROM_EMAIL: str
    FROM_NAME: str

    # Communications
    TELEGRAM_BOT_TOKEN: str

    # App Settings
    DOMAIN: str
    SENDER_EMAIL: str
    SENDER_NAME: str
    API_KEY: str

    # Discovery (Required)
    GOOGLE_PLACES_API_KEY: str

    # Optional Fields (must come last)
    GROQ_API_KEY: Optional[str] = None
    BREVO_SMTP_KEY: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    GOOGLE_CSE_API_KEY: Optional[str] = None
    GOOGLE_CSE_ID: Optional[str] = None
    HUNTER_API_KEY: Optional[str] = None
    APOLLO_API_KEY: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None


def get_settings() -> Settings:
    # Required keys for basic functionality
    required_keys = [
        "DATABASE_URL", "REDIS_URL",
        "SUPABASE_URL", "SUPABASE_KEY",
        "GEMINI_API_KEY",
        "SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS",
        "FROM_EMAIL", "FROM_NAME",
        "TELEGRAM_BOT_TOKEN",
        "GOOGLE_PLACES_API_KEY",
        "DOMAIN", "SENDER_EMAIL", "SENDER_NAME", "API_KEY"
    ]
    
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
    
    return Settings(
        DATABASE_URL=os.getenv("DATABASE_URL"),
        REDIS_URL=os.getenv("REDIS_URL"),
        SUPABASE_URL=os.getenv("SUPABASE_URL"),
        SUPABASE_KEY=os.getenv("SUPABASE_KEY"),
        GEMINI_API_KEY=os.getenv("GEMINI_API_KEY"),
        GROQ_API_KEY=os.getenv("GROQ_API_KEY"),
        SMTP_HOST=os.getenv("SMTP_HOST"),
        SMTP_PORT=int(os.getenv("SMTP_PORT", 587)),
        SMTP_USER=os.getenv("SMTP_USER"),
        SMTP_PASS=os.getenv("SMTP_PASS"),
        FROM_EMAIL=os.getenv("FROM_EMAIL"),
        FROM_NAME=os.getenv("FROM_NAME"),
        TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN"),
        BREVO_SMTP_KEY=os.getenv("BREVO_SMTP_KEY"),
        TELEGRAM_CHAT_ID=os.getenv("TELEGRAM_CHAT_ID"),
        GOOGLE_PLACES_API_KEY=os.getenv("GOOGLE_PLACES_API_KEY"),
        GOOGLE_CSE_API_KEY=os.getenv("GOOGLE_CSE_API_KEY"),
        GOOGLE_CSE_ID=os.getenv("GOOGLE_CSE_ID"),
        HUNTER_API_KEY=os.getenv("HUNTER_API_KEY"),
        APOLLO_API_KEY=os.getenv("APOLLO_API_KEY"),
        GITHUB_TOKEN=os.getenv("GITHUB_TOKEN"),
        DOMAIN=os.getenv("DOMAIN"),
        SENDER_EMAIL=os.getenv("SENDER_EMAIL"),
        SENDER_NAME=os.getenv("SENDER_NAME"),
        API_KEY=os.getenv("API_KEY")
    )
    if not settings.SENDER_EMAIL:
        raise ValueError("SENDER_EMAIL must be set in .env")
    return settings

settings = get_settings()
