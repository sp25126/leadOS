import httpx
import re
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict

# Specific Indian mobile-friendly regex
INDIAN_PHONE_RE = re.compile(r'(?:\+91|91|0)?[\s\-]?[6-9]\d{9}')
EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b')

JUNK_EMAIL_PREFIXES = [
    'info', 'contact', 'hello', 'support', 'admin', 'noreply',
    'no-reply', 'webmaster', 'feedback', 'help', 'service', 'dns',
]

from services.social_extractor import extract_social_handles
from services.phone_cleaner import clean_phone, detect_country_from_location

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}


async def ddg_search_lead(name: str, city: str, retries: int = 2) -> List[str]:
    """Search DuckDuckGo HTML and return raw text snippets."""
    query = f'"{name}" "{city}" phone contact email'
    
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True) as client:
                resp = await client.get(
                    "https://html.duckduckgo.com/html/",
                    params={"q": query}
                )
                if resp.status_code != 200:
                    await asyncio.sleep(1)
                    continue
                
                soup = BeautifulSoup(resp.text, "html.parser")
                snippets = []
                for result in soup.select(".result__snippet")[:5]:
                    snippets.append(result.get_text())
                return snippets
        
        except Exception as e:
            print(f"[DDG] Attempt {attempt+1} failed for {name}: {e}")
            await asyncio.sleep(1 * (attempt+1))
    
    return []


def extract_contact_from_text(text: str) -> dict:
    """Extract phone, email, and social handles from raw text."""
    result = {}
    
    # Phone extraction
    phones = INDIAN_PHONE_RE.findall(text)
    if phones:
        country = detect_country_from_location(text)
        cleaned = clean_phone(phones[0], country)
        if cleaned:
            result["phone"] = cleaned
            result["phone_source"] = "duckduckgo_osint"
    
    # Email extraction
    emails = EMAIL_RE.findall(text)
    for email in emails:
        prefix = email.split('@')[0].lower()
        if not any(prefix.startswith(j) for j in JUNK_EMAIL_PREFIXES):
            result["email"] = email
            result["email_source"] = "duckduckgo_osint"
            result["email_quality_score"] = 2
            break
    
    socials = extract_social_handles(text)
    if socials:
        result["social_media"] = str(socials)
    
    return result


async def enrich_lead_with_ddg(lead: dict) -> dict:
    """Runs single-lead OSINT lookup."""
    # Skip if already fully enriched
    if lead.get("phone") and lead.get("email"):
        return lead
    
    name = lead.get("name", "")
    city = lead.get("city") or _extract_city_from_address(lead.get("address", ""))
    
    snippets = await ddg_search_lead(name, city)
    if not snippets:
        return lead
    
    combined_text = " ".join(snippets)
    contact_data = extract_contact_from_text(combined_text)
    
    # Merge into lead
    for k, v in contact_data.items():
        if not lead.get(k):
            lead[k] = v
    
    return lead


async def enrich_batch_with_ddg(
    leads: List[Dict],
    concurrency: int = 3,
    delay: float = 0.5
) -> List[Dict]:
    """Runs parallel batch DDG searches with careful rate limiting."""
    needs_enrichment = [l for l in leads if not l.get("phone") or not l.get("email")]
    already_good = [l for l in leads if l.get("phone") and l.get("email")]
    
    if not needs_enrichment:
        return leads
    
    sem = asyncio.Semaphore(concurrency)
    
    async def bounded(lead):
        async with sem:
            res = await enrich_lead_with_ddg(lead)
            await asyncio.sleep(delay)
            return res

    results = await asyncio.gather(*[bounded(l) for l in needs_enrichment], return_exceptions=True)
    
    processed = already_good.copy()
    for item in results:
        if isinstance(item, Exception):
            continue
        processed.append(item)
    
    return processed


def _extract_city_from_address(address: str) -> str:
    # simple fallackCity extraction code if not already in common
    indian_cities = ["Pune", "Ahmedabad", "Mumbai", "Delhi", "Bangalore"]
    if not address: return ""
    for city in indian_cities:
        if city.lower() in address.lower():
            return city
    return ""
