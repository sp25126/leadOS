import os
import json
import asyncio
import re
from services.llm_gateway import call_llm

DEFAULT_CONTEXT = os.getenv(
    "SERVICE_CONTEXT",
    "We help local businesses get their first professional website "
    "and automate customer follow-ups using AI. "
    "Typical result: 3x more enquiries within 60 days."
)

WA_PROMPT = """
Write a WhatsApp outreach message for this business lead.

NON-NEGOTIABLE RULES:
- Maximum 3 sentences total
- Address them by first name or business name naturally (no "Dear")
- Reference exactly ONE specific detail from their data:
  use no-website / their tech stack / review count / business type
- End with ONE soft question (not a pitch, not "interested?")
- Tone: peer talking to peer - friendly, zero corporate speak
- Maximum 2 emoji in the entire message
- If suggested_opening exists in lead data, use it as inspiration only

Lead data:
{lead_json}

Your service:
{context}

Return ONLY the message text. No quotes. No labels. No explanations.
"""

EMAIL_PROMPT = """
Write a cold outreach email for this business lead.

NON-NEGOTIABLE RULES:
- Subject: max 7 words, create curiosity or reference their business specifically
- Opening line: reference something specific (no website / their industry / city / review count)
- Body: 3 sentences maximum after the opening
- Close: one soft question CTA
- Mandatory: include a natural unsubscribe sentence at the end (e.g., "If you'd like me to stop reaching out, just reply 'stop'." )
- Tone: peer-to-peer, zero corporate speak, no buzzwords
- No formal sign-off like "Regards"

Lead data:
{lead_json}

Your service:
{context}

Return ONLY valid JSON with NO markdown, NO code fences:
{{"subject": "...", "body": "full email body here"}}
"""

SLIM_FIELDS = [
    "name", "types", "has_website", "rating", "review_count",
    "address", "tech_hints", "pain_points", "suggested_opening",
]

_FALLBACK_WA_TEMPLATE = (
    "Hi {name}, came across your {type} and wanted to reach out. "
    "We help local businesses like yours grow their online presence - "
    "would you be open to a quick chat?"
)
_FALLBACK_EMAIL = {
    "subject": "Quick question about your business",
    "body": (
        "Hi {name},\n\n"
        "I came across your {type} and noticed there might be an "
        "opportunity to help you get more customers online.\n\n"
        "We've helped similar businesses get their first website and "
        "automate follow-ups - would that be useful for you?\n\n"
        "(If you'd rather not hear from me again, just reply 'stop' or ignore this email.)"
    )
}


def _slim_lead(lead: dict) -> dict:
    return {k: lead.get(k, "") for k in SLIM_FIELDS}


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text, flags=re.MULTILINE)
    text = re.sub(r"```$",          "", text, flags=re.MULTILINE)
    return text.strip()


async def generate_whatsapp_message(
    lead: dict, context: str | None = None
) -> str:
    ctx    = context or DEFAULT_CONTEXT
    prompt = WA_PROMPT.format(
        lead_json=json.dumps(_slim_lead(lead), ensure_ascii=False, indent=2),
        context=ctx,
    )
    try:
        msg = await call_llm(prompt)
        msg = msg.strip().strip('"').strip("'")
        # Enforce max length (WhatsApp best practice)
        if len(msg) > 350:
            msg = msg[:347] + "..."
        return msg
    except Exception as e:
        print(f"  [Personalizer]    WA fallback used: {e}")
        return _FALLBACK_WA_TEMPLATE.format(
            name=lead.get("name", "there"),
            type=lead.get("types", "business"),
        )


async def generate_email(
    lead: dict, context: str | None = None
) -> dict:
    ctx    = context or DEFAULT_CONTEXT
    prompt = EMAIL_PROMPT.format(
        lead_json=json.dumps(_slim_lead(lead), ensure_ascii=False, indent=2),
        context=ctx,
    )
    try:
        response_text = await call_llm(prompt, expect_json=True)
        raw    = _strip_fences(response_text)
        parsed = json.loads(raw)

        # Validate structure
        if "subject" not in parsed or "body" not in parsed:
            raise ValueError("Missing subject or body keys")

        return {
            "subject": str(parsed["subject"])[:80],   # cap subject length
            "body":    str(parsed["body"]),
        }
    except Exception as e:
        print(f"  [Personalizer]    Email fallback used: {e}")
        name  = lead.get("name", "there")
        btype = lead.get("types", "business")
        return {
            "subject": _FALLBACK_EMAIL["subject"],
            "body":    _FALLBACK_EMAIL["body"].format(name=name, type=btype),
        }
