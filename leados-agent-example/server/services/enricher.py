import re
import asyncio
import json
import os
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from utils.request_manager import safe_get

# ── Circuit Breaker Config ──────────────────────────────────────────
BREAKER_FILE = os.path.join("output", "breaker_state.json")
BREAKER_THRESHOLD = 3       # failures before open
BREAKER_RESET_HOURS = 24    # auto-reset after 24h

def _load_breaker_state() -> dict:
    """Load persisted breaker state from disk."""
    if os.path.exists(BREAKER_FILE):
        try:
            with open(BREAKER_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save_breaker_state(state: dict):
    """Persist breaker state to disk."""
    os.makedirs("output", exist_ok=True)
    try:
        with open(BREAKER_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception:
        pass

# Module-level state loaded ONCE at import
_breaker: dict = _load_breaker_state()

def record_failure(domain: str):
    """Record a scrape failure for a domain."""
    if not domain: return
    entry = _breaker.get(domain, {"failures": 0, "opened_at": None})
    entry["failures"] += 1
    if entry["failures"] >= BREAKER_THRESHOLD:
        entry["opened_at"] = time.time()
    _breaker[domain] = entry
    _save_breaker_state(_breaker)

def is_circuit_open(domain: str) -> bool:
    """Return True if this domain is blocked."""
    if not domain: return False
    entry = _breaker.get(domain)
    if not entry or not entry.get("opened_at"):
        return False
    
    # Auto-reset after BREAKER_RESET_HOURS
    age_hours = (time.time() - entry["opened_at"]) / 3600
    if age_hours > BREAKER_RESET_HOURS:
        if domain in _breaker:
            del _breaker[domain]
            _save_breaker_state(_breaker)
        return False
    return True

# ── Regexes ─────────────────────────────────────────────────────────
EMAIL_RE  = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
PHONE_RE  = re.compile(r'(\+?\d[\d\s\-\(\)\.]{7,}\d)')
SOCIAL_RE = {
    "instagram": re.compile(r'instagram\.com/(?!p/)([^/"\'?\s\\]+)'),
    "facebook":  re.compile(r'facebook\.com/(?!sharer|share|pages)([^/"\'?\s\\]+)'),
    "twitter":   re.compile(r'(?:twitter|x)\.com/([^/"\'?\s\\]+)'),
    "linkedin":  re.compile(r'linkedin\.com/company/([^/"\'?\s\\]+)'),
    "youtube":   re.compile(r'youtube\.com/(?:@|c/|channel/)([^"\'?\s\\]+)'),
}

JUNK_EMAILS = {
    "noreply", "no-reply", "donotreply", "webmaster", "postmaster",
    "admin", "test", "example", "info@example", "user@example",
    "email@domain", "name@domain", "yourname", "youremail",
}
JUNK_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".css", ".js",
                   ".svg", ".ico", ".pdf", ".zip", ".woff"}

CONTACT_PATHS = [
    "/contact", "/contact-us", "/contactus", "/about", "/about-us",
    "/get-in-touch", "/reach-us", "/connect", "/support",
]

TECH_SIGNALS = {
    "wordpress":   ["wp-content", "wp-includes", "wp-json", "wordpress"],
    "wix":         ["wix.com", "wixsite", "_wix"],
    "shopify":     ["shopify", "cdn.shopify", "myshopify"],
    "squarespace": ["squarespace", "static1.squarespace"],
    "webflow":     ["webflow.io", "webflow.com"],
    "blogger":     ["blogger.com", "blogspot.com"],
    "booking":     ["booking.com", "bookingkit", "simplybook", "calendly",
                    "book-now", "book now", "schedule appointment"],
    "whatsapp_widget": ["wa.me", "api.whatsapp.com", "whatsapp"],
    "online_menu":     ["zomato", "swiggy", "talabat", "menu", "food-menu"],
    "payment":         ["razorpay", "paytm", "stripe", "paypal", "payment-gateway"],
}


def is_valid_email(email: str) -> bool:
    email_lower = email.lower()
    if any(j in email_lower for j in JUNK_EMAILS):
        return False
    if any(email_lower.endswith(ext) for ext in JUNK_EXTENSIONS):
        return False
    if len(email) > 100:
        return False
    # Must have valid TLD (2-6 chars)
    parts = email.split("@")
    if len(parts) != 2:
        return False
    domain_part = parts[1]
    if "." not in domain_part:
        return False
    tld = domain_part.split(".")[-1]
    if not (2 <= len(tld) <= 6):
        return False
    return True


def _extract_emails(html: str) -> list[str]:
    raw  = EMAIL_RE.findall(html)
    seen = set()
    out  = []
    for e in raw:
        e = e.lower().strip().rstrip(".,;\"'")
        if e not in seen and is_valid_email(e):
            seen.add(e)
            out.append(e)
    return out


def _extract_tech_hints(html_lower: str) -> list[str]:
    found = []
    for tech, signals in TECH_SIGNALS.items():
        if any(s in html_lower for s in signals):
            found.append(tech)
    return found


def _extract_social(html: str) -> dict:
    handles = {}
    for platform, pattern in SOCIAL_RE.items():
        m = pattern.search(html)
        if m:
            handle = m.group(1).strip("/").split("?")[0]
            if handle and len(handle) > 1:
                handles[platform] = handle
    return handles


def _has_contact_form(html: str) -> bool:
    html_lower = html.lower()
    if "<form" not in html_lower:
        return False
    contact_keywords = ["email", "contact", "message", "enquir", "inquiry", "name"]
    return sum(1 for kw in contact_keywords if kw in html_lower) >= 2


async def scrape_website(url: str) -> dict:
    result = {
        "emails":           [],
        "phones_from_web":  [],
        "social":           {},
        "is_live":          False,
        "tech_hints":       [],
        "has_contact_form": False,
    }

    if not url or not url.startswith("http"):
        return result

    domain = urlparse(url).netloc
    if is_circuit_open(domain):
        return result

    try:
        html = await safe_get(url, is_scrape=True)
        if not html or not isinstance(html, str) or len(html) < 100:
            record_failure(domain)
            return result
    except Exception:
        record_failure(domain)
        return result

    result["is_live"]          = True
    html_lower                 = html.lower()
    result["emails"]           = _extract_emails(html)
    result["tech_hints"]       = _extract_tech_hints(html_lower)
    result["social"]           = _extract_social(html)
    result["has_contact_form"] = _has_contact_form(html)

    # Phone extraction from visible text
    try:
        soup       = BeautifulSoup(html, "lxml")
        text       = soup.get_text(separator=" ")
        raw_phones = PHONE_RE.findall(text)
        result["phones_from_web"] = [
            re.sub(r"[\s\-\(\)]", "", p)
            for p in raw_phones
            if len(re.sub(r"\D", "", p)) >= 10
        ][:3]
    except Exception:
        pass

    # If still no emails → scrape contact pages
    if not result["emails"]:
        base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        for path in CONTACT_PATHS:
            try:
                target_url = urljoin(base, path)
                contact_html = await safe_get(target_url, is_scrape=True)
                if contact_html and isinstance(contact_html, str):
                    found = _extract_emails(contact_html)
                    if found:
                        result["emails"].extend(found)
                        break
                else:
                    # Minor failure on contact page doesn't trip the main domain breaker as easily
                    # but we track it if requested (skipped for brevity/noise reduction)
                    pass
                await asyncio.sleep(0.5)
            except Exception:
                continue

    return result


# ── Per-process attempt counters (keyed by name+address) ─────────────
_attempt_counters: dict[str, int] = {}

_GENERIC_LOCAL_PARTS = {
    "info", "contact", "hello", "sales", "support",
    "admin", "customercare", "hr",
}


def _lead_key(lead: dict) -> str:
    return f"{lead.get('name', '')}|{lead.get('address', '')}".lower()


def _email_quality_score(email: str) -> int:
    """1 = generic/low-value, 3 = personal/high-value."""
    local = email.split("@")[0].lower() if "@" in email else email.lower()
    return 1 if local in _GENERIC_LOCAL_PARTS else 3


async def enrich_lead(lead: dict) -> dict:
    enriched = lead.copy()
    key = _lead_key(lead)

    # ── Circuit breaker ────────────────────────────────────────────────
    attempts = _attempt_counters.get(key, 0)
    if attempts >= 3:
        enriched["status"]             = "UNENRICHABLE"
        enriched["emailqualityscore"]  = 0
        return enriched

    # Increment attempt counter before doing any work
    _attempt_counters[key] = attempts + 1

    if lead.get("website"):
        web = await scrape_website(lead["website"])

        enriched["website_live"]     = web["is_live"]
        enriched["tech_hints"]       = ", ".join(web["tech_hints"])
        enriched["social_media"]     = str(web["social"]) if web["social"] else ""
        enriched["has_contact_form"] = web["has_contact_form"]

        # Upgrade phone if we found one on website and lead had none
        if not enriched.get("phone") and web["phones_from_web"]:
            enriched["phone"] = web["phones_from_web"][0]

        # Set email (website scrape is most accurate)
        if not enriched.get("email") and web["emails"]:
            enriched["email"] = web["emails"][0]
    else:
        enriched["website_live"]     = False
        enriched["tech_hints"]       = ""
        enriched["social_media"]     = ""
        enriched["has_contact_form"] = False

    # ── Post-enrichment status + quality ─────────────────────────────
    email_found = enriched.get("email", "").strip()
    if email_found:
        enriched["emailqualityscore"] = _email_quality_score(email_found)
        enriched["status"]            = "READY"
    else:
        current_attempts = _attempt_counters.get(key, 1)
        enriched["emailqualityscore"] = 0
        enriched["status"]            = "ENRICHMENT_FAILED" if current_attempts >= 3 else "NEW"

    return enriched


async def enrich_all(leads: list[dict], concurrency: int = 5) -> list[dict]:
    sem   = asyncio.Semaphore(concurrency)
    total = len(leads)
    counter = {"n": 0}

    async def bounded(lead: dict) -> dict:
        async with sem:
            enriched = await enrich_lead(lead)
            counter["n"] += 1
            if counter["n"] % 10 == 0 or counter["n"] == total:
                print(f"  Enriched {counter['n']}/{total}...")
            return enriched

    return list(await asyncio.gather(*[bounded(l) for l in leads]))
