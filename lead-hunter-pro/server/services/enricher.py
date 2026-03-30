import re
import asyncio
import json
import os
import time
import logging
import httpx
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from utils.request_manager import safe_get, get_headers
from services.email_waterfall_adapter import (
    find_email_octagon,
    score_email_quality,
    is_waterfall_available,
)

logger = logging.getLogger("LeadOS.enricher")

#   Circuit Breaker Config  
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

#   Regexes  
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


async def _scrape_path(client: httpx.AsyncClient, url: str) -> list[str]:
    """Helper for concurrent path scraping."""
    try:
        resp = await client.get(url, timeout=10.0)
        if resp.status_code == 200 and isinstance(resp.text, str):
            return _extract_emails(resp.text)
    except Exception:
        pass
    return []


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
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=get_headers())
            if resp.status_code != 200 or not isinstance(resp.text, str) or len(resp.text) < 100:
                record_failure(domain)
                return result

            html = resp.text
            result["is_live"]          = True
            html_lower                 = html.lower()
            result["emails"]           = _extract_emails(html)
            result["tech_hints"]       = _extract_tech_hints(html_lower)
            result["social"]           = _extract_social(html)
            result["has_contact_form"] = _has_contact_form(html)

            # Phone extraction
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

            # If still no emails -> concurrent scrape contact pages
            if not result["emails"]:
                scheme = urlparse(url).scheme
                netloc = urlparse(url).netloc
                base = f"{scheme}://{netloc}"
                tasks = []
                for path in CONTACT_PATHS:
                    tasks.append(_scrape_path(client, urljoin(base, path)))
                
                path_results = await asyncio.gather(*tasks)
                for found in path_results:
                    if found:
                        result["emails"].extend(found)
                
                # Deduplicate
                result["emails"] = list(dict.fromkeys(result["emails"]))

    except Exception:
        record_failure(domain)

    return result


async def try_social_search(company_name: str, domain: str) -> dict:
    """Ported from Octagon: Scrape social links via DuckDuckGo HTML."""
    if not company_name:
        return {}
    
    query = f"{company_name} {domain} site:facebook.com OR site:linkedin.com/company OR site:twitter.com"
    search_url = f"https://html.duckduckgo.com/html/?q={re.sub(r'[^a-zA-Z0-9 ]', '', query)}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as c:
            resp = await c.get(search_url, headers=get_headers())
            if resp.status_code == 200:
                html = resp.text
                li_matches = re.findall(r'https://[a-z]{0,3}\.?linkedin\.com/company/[^"&\s]+', html)
                fb_matches = re.findall(r'https://[a-z]{0,3}\.?facebook\.com/[^"&\s/]+', html)
                tw_matches = re.findall(r'https://(?:twitter|x)\.com/[^"&\s/]+', html)
                
                social = {}
                if li_matches: social["linkedin"] = li_matches[0].split("?")[0]
                if fb_matches: social["facebook"] = fb_matches[0].split("?")[0]
                if tw_matches: social["twitter"] = tw_matches[0].split("?")[0]
                return social
    except Exception:
        pass
    return {}


async def try_google_places_details(company_name: str, lat: float = None, lon: float = None) -> dict:
    """Ported from Octagon: Fallback for local leads missing websites."""
    from utils import config_store
    api_key = config_store.gmaps_key()
    if not api_key or not company_name:
        return {}

    from services.google_places import search_google_places
    try:
        results = await search_google_places(company_name, f"{lat},{lon}" if (lat and lon) else "Dubai")
        if results:
            best = results[0]
            return {
                "phone":   best.get("phone"),
                "website": best.get("website"),
                "address": best.get("address"),
                "rating":  best.get("rating"),
            }
    except Exception:
        pass
    return {}


from services.india_enrichment import enrich_indian_lead

def _lead_key(lead: dict) -> str:
    return f"{lead.get('name', '')}_{lead.get('address', '')}_{lead.get('city', '')}".lower()

def _lead_key(lead: dict) -> str:
    return f"{lead.get('name', '')}_{lead.get('address', '')}_{lead.get('city', '')}".lower()

#   Per-process attempt counters (keyed by name+address)  
_attempt_counters: dict[str, int] = {}


from services.lead_filter import filter_leads
from services.google_places_enricher import enrich_batch_with_gmaps
from services.duckduckgo_enricher import enrich_batch_with_ddg
from services.email_validator import score_email_quality, determine_lead_status
from services.ai_scorer import score_leads_batch
from services.social_extractor import extract_social_handles

async def run_enrichment_pipeline(
    raw_leads: list[dict],
    creds,  # RequestCredentials object
    target_service: str = "digital marketing and website development"
) -> dict:
    """
    Full enrichment pipeline. Returns enrichment summary + enriched leads.
    """
    stats = {
        "raw": len(raw_leads),
        "after_filter": 0,
        "with_phone": 0,
        "with_email": 0,
        "ai_scored": 0,
        "ready": 0,
        "storage": "csv",
    }
    
    # Stage 0: Filter junk leads
    leads, dropped = filter_leads(raw_leads)
    stats["after_filter"] = len(leads)
    print(f"\n{'-'*50}")
    print(f"[PIPELINE] Starting enrichment: {len(leads)} leads")
    print(f"[PIPELINE] Dropped {len(dropped)} junk leads")
    
    # Stage 1: Google Maps enrichment (phone, rating, hours)
    print(f"[STAGE 1/5] Google Maps enrichment...")
    if creds and hasattr(creds, 'google_maps_key') and creds.google_maps_key:
        leads = await enrich_batch_with_gmaps(leads, creds.google_maps_key)
    else:
        print("[STAGE 1/5] Skipped - no Google Maps key in request headers")
    
    # Stage 2: DuckDuckGo OSINT (phone, email, social)
    print(f"[STAGE 2/5] DuckDuckGo OSINT enrichment...")
    leads = await enrich_batch_with_ddg(leads, concurrency=3)
    
    # Stage 3: Website scrape (Existing logic)
    print(f"[STAGE 3/5] Website scraping...")
    for lead in leads:
        if lead.get("website") and not lead.get("email"):
            web = await scrape_website(lead["website"])
            if web["is_live"]:
                if web["emails"] and not lead.get("email"):
                    lead["email"] = web["emails"][0]
                    lead["email_source"] = "website_scrape"
                    # Merge social using extractor
                    import ast
                    social_dict = extract_social_handles(web["raw_html"]) if "raw_html" in web else web["social"]
                    existing = {}
                    try: 
                        if lead.get("social_media"):
                            existing = ast.literal_eval(lead["social_media"])
                    except: pass
                    existing.update(social_dict)
                    lead["social_media"] = str(existing)
                if web["tech_hints"]:
                    lead["tech_hints"] = ", ".join(web["tech_hints"])
    
    # Stage 4: Email quality re-scoring
    print(f"[STAGE 4/5] Email quality scoring...")
    for lead in leads:
        if lead.get("email"):
            lead["email_quality_score"] = score_email_quality(
                lead["email"], 
                lead.get("email_source", "")
            )
        else:
            lead["email_quality_score"] = 0
            
        lead["status"] = determine_lead_status(lead)
    
    # Stage 5: AI Scoring
    print(f"[STAGE 5/5] AI scoring...")
    g_key = getattr(creds, 'gemini_key', "") if creds else ""
    gr_key = getattr(creds, 'groq_key', "") if creds else ""
    
    if g_key or gr_key:
        leads = await score_leads_batch(
            leads,
            gemini_key=g_key,
            groq_key=gr_key,
            target_service=target_service,
            concurrency=5
        )
        stats["ai_scored"] = sum(1 for l in leads if l.get("score", 5) != 5)
    else:
        print("[STAGE 5/5] No AI keys - using rule-based scoring")
        from services.ai_scorer import _rule_based_score
        leads = [{**l, **_rule_based_score(l)} for l in leads]
    
    # Final stats
    stats["with_phone"] = sum(1 for l in leads if l.get("phone"))
    stats["with_email"] = sum(1 for l in leads if l.get("email"))
    stats["ready"] = sum(1 for l in leads if l.get("status") == "READY")
    
    print(f"\n[PIPELINE COMPLETE]")
    print(f"  Leads: {stats['raw']} -> {stats['after_filter']} (after filter)")
    print(f"  Phone: {stats['with_phone']}/{stats['after_filter']} ({100*stats['with_phone']//max(1,stats['after_filter'])}%)")
    print(f"  Email: {stats['with_email']}/{stats['after_filter']} ({100*stats['with_email']//max(1,stats['after_filter'])}%)")
    print(f"  AI Scored: {stats['ai_scored']}/{stats['after_filter']}")
    print(f"  READY: {stats['ready']}")
    print(f"{'='*50}\n")
    
    return {"leads": leads, "stats": stats}

async def enrich_all(leads: list[dict], concurrency: int = 5, gmaps_key: str = "", hunter_key: str = "") -> list[dict]:
    """Backward compatibility wrapper for newer 5-stage pipeline."""
    from utils.request_credentials import RequestCredentials
    creds = RequestCredentials(
        google_maps_key=gmaps_key,
        gemini_key="", # Not provided in old signature
        groq_key=""    # Not provided in old signature
    )
    result = await run_enrichment_pipeline(leads, creds)
    return result["leads"]
