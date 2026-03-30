import re
import asyncio
import httpx
from urllib.parse import quote
from utils.request_manager import safe_get, get_headers

async def search_duckduckgo(query: str) -> list[str]:
    """Scrape DuckDuckGo (HTML) for potential links."""
    search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(search_url, headers=get_headers())
            if resp.status_code == 200:
                # Simple link extraction for demo; in reality, use a better parser
                links = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', resp.text)
                return list(set(links))
    except Exception as e:
        print(f"  [IndiaEnrich] DuckDuckGo search failed: {e}")
    return []

async def get_google_place_details(place_name: str, city: str, api_key: str) -> dict:
    """Get phone and address from Google Maps Place Details."""
    if not api_key:
        return {}
    
    # First, find the place ID
    search_url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={quote(f'{place_name} {city}')}&inputtype=textquery&fields=place_id&key={api_key}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(search_url)
            data = resp.json()
            if data.get("candidates"):
                place_id = data["candidates"][0]["place_id"]
                # Now get details
                details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=formatted_phone_number,international_phone_number,formatted_address,website&key={api_key}"
                resp = await client.get(details_url)
                details = resp.json().get("result", {})
                return {
                    "phone": details.get("international_phone_number") or details.get("formatted_phone_number"),
                    "address": details.get("formatted_address"),
                    "website": details.get("website")
                }
    except Exception as e:
        print(f"  [IndiaEnrich] GMaps Details failed: {e}")
    return {}

def format_indian_phone(phone: str) -> str:
    """Normalize Indian phone numbers to +91XXXXXXXXXX."""
    if not phone: return ""
    clean = re.sub(r"\D", "", phone)
    if len(clean) == 10:
        return f"+91{clean}"
    if len(clean) == 12 and clean.startswith("91"):
        return f"+{clean}"
    return phone

async def enrich_indian_lead(lead: dict, gmaps_key: str = "") -> dict:
    """Special enrichment waterfall for Indian SMBs."""
    name = lead.get("name", "")
    city = lead.get("city", "") or lead.get("address", "")
    
    print(f"    [IndiaEnrich] Processing: {name} in {city}")
    
    # 1. Try Google Maps Place Details (Best for Indian Phone/Address)
    if gmaps_key:
        details = await get_google_place_details(name, city, gmaps_key)
        if details.get("phone"):
            lead["phone"] = format_indian_phone(details["phone"])
        if details.get("address") and not lead.get("address"):
            lead["address"] = details["address"]
        if details.get("website") and not lead.get("website"):
            lead["website"] = details["website"]
            lead["has_website"] = True

    # 2. Try DuckDuckGo for Justdial/Instagram/FB
    if not lead.get("phone") or not lead.get("social_media"):
        links = await search_duckduckgo(f"{name} {city} contact number instagram facebook")
        for link in links:
            if "justdial.com" in link and not lead.get("phone"):
                # Potential JD link; in a real scraper, we'd follow it
                pass 
            if "instagram.com" in link:
                social = lead.get("social_media", "{}")
                if isinstance(social, str): 
                    try: social = json.loads(social)
                    except: social = {}
                social["instagram"] = link
                lead["social_media"] = social
            if "facebook.com" in link:
                social = lead.get("social_media", "{}")
                if isinstance(social, str): 
                    try: social = json.loads(social)
                    except: social = {}
                social["facebook"] = link
                lead["social_media"] = social

    return lead
