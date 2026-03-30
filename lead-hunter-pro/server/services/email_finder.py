import os
import re
import asyncio
from urllib.parse import urlparse
from utils.rate_limiter import quota
from utils.request_manager import safe_get

EMAIL_FORMAT_TEMPLATES = [
    "{first}@{domain}",
    "{first}.{last}@{domain}",
    "{f}{last}@{domain}",
    "{first}{last}@{domain}",
    "{first}_{last}@{domain}",
    "info@{domain}",        # Always include as last-resort fallback
    "contact@{domain}",
    "hello@{domain}",
]


def extract_domain(website: str) -> str | None:
    if not website:
        return None
    if "://" not in website:
        website = "https://" + website
    parsed = urlparse(website)
    netloc = parsed.netloc.replace("www.", "").strip()
    return netloc if netloc else None


async def hunter_find_email(domain: str, full_name: str) -> str | None:
    if not quota.has_quota("hunter_io"):
        print("    [Hunter.io]    Monthly quota (25) exhausted")
        return None

    api_key = os.getenv("HUNTER_API_KEY", "")
    if not api_key:
        return None

    parts = full_name.strip().split()
    first = parts[0].lower()  if parts          else ""
    last  = parts[-1].lower() if len(parts) > 1 else ""

    result = await safe_get(
        "https://api.hunter.io/v2/email-finder",
        params={
            "domain":     domain,
            "first_name": first,
            "last_name":  last,
            "api_key":    api_key,
        }
    )
    quota.consume("hunter_io")

    if not result:
        return None

    data       = result.get("data", {})
    email      = data.get("email", "")
    confidence = data.get("score", 0)

    return email if email and confidence >= 50 else None


def guess_emails(domain: str, full_name: str) -> list[str]:
    parts = full_name.strip().lower().split()
    first = re.sub(r"[^a-z]", "", parts[0])  if parts          else "contact"
    last  = re.sub(r"[^a-z]", "", parts[-1]) if len(parts) > 1 else ""
    f     = first[0] if first else "c"

    seen = set()
    out  = []
    for tmpl in EMAIL_FORMAT_TEMPLATES:
        try:
            email = tmpl.format(first=first, last=last, f=f, domain=domain)
            if email not in seen and "@" in email:
                seen.add(email)
                out.append(email)
        except KeyError:
            # Template uses {last} but last is empty - skip
            continue

    return out


async def validate_email_abstract(email: str) -> bool:
    if not quota.has_quota("abstract_email"):
        return True   # Optimistic fallback - don't block on quota

    api_key = os.getenv("ABSTRACT_API_KEY", "")
    if not api_key:
        return True

    result = await safe_get(
        "https://emailvalidation.abstractapi.com/v1/",
        params={"api_key": api_key, "email": email}
    )
    quota.consume("abstract_email")

    if not result or not isinstance(result, dict):
        return True   # Optimistic

    deliverable    = result.get("deliverability", "") == "DELIVERABLE"
    mx_found       = result.get("is_mx_found", {}).get("value", False)
    not_disposable = not result.get("is_disposable_email", {}).get("value", True)

    return deliverable and mx_found and not_disposable


async def find_email_for_lead(lead: dict) -> str:
    # Already have a valid email
    existing = lead.get("email", "").strip()
    if existing and "@" in existing:
        return existing

    domain = extract_domain(lead.get("website", ""))
    name   = lead.get("name", "")

    if not domain:
        return ""

    # Try Hunter.io first (most accurate, uses quota)
    hunter_email = await hunter_find_email(domain, name)
    if hunter_email:
        valid = await validate_email_abstract(hunter_email)
        if valid:
            return hunter_email

    # Fallback: info@domain (safest guess, no validation needed)
    guesses = guess_emails(domain, name)
    return guesses[0] if guesses else f"info@{domain}"
