import httpx
import asyncio
import re
from typing import Optional

# Google Places API Endpoints
PLACES_TEXT_SEARCH = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACES_DETAILS    = "https://maps.googleapis.com/maps/api/place/details/json"

async def get_gmaps_contact(
    name: str,
    city: str,
    api_key: str,
    timeout: int = 15
) -> dict:
    """
    Two-step Google Maps lookup:
    1. Text search -> get place_id
    2. Place details -> get phone, website, rating, review_count, opening_hours
    """
    if not api_key:
        return {}
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Step 1: Text search
            search = await client.get(PLACES_TEXT_SEARCH, params={
                "query": f"{name} {city}",
                "key": api_key,
                "region": "in",  # Bias results to India
            })
            resp_search = search.json()
            results = resp_search.get("results", [])
            if not results:
                return {}
            
            # Use top result
            place = results[0]
            place_id = place.get("place_id")
            if not place_id:
                return {}
            
            # Step 2: Place details
            detail = await client.get(PLACES_DETAILS, params={
                "place_id": place_id,
                "fields": ",".join([
                    "international_phone_number",
                    "formatted_phone_number", 
                    "website",
                    "rating",
                    "user_ratings_total",
                    "opening_hours",
                    "business_status",
                ]),
                "key": api_key,
            })
            
            resp_detail = detail.json()
            result = resp_detail.get("result", {})
            
            # Skip if closed
            if result.get("business_status") == "CLOSED_PERMANENTLY":
                return {"_gmaps_closed": True}
            
            enriched = {}
            
            phone = (result.get("international_phone_number") or 
                    result.get("formatted_phone_number") or "")
            if phone:
                enriched["phone"] = phone
                enriched["phone_source"] = "google_maps"
            
            website = result.get("website", "")
            if website:
                enriched["website"] = website
            
            rating = result.get("rating")
            if rating:
                enriched["rating"] = rating
            
            review_count = result.get("user_ratings_total")
            if review_count:
                enriched["review_count"] = review_count
            
            hours = result.get("opening_hours", {})
            if hours.get("weekday_text"):
                # Store first 2 lines as representative
                enriched["opening_hours"] = "; ".join(hours["weekday_text"][:2])
            
            return enriched
    
    except Exception as e:
        print(f"[GMAPS] Detailed Enrichment error for {name}: {e}")
        return {}


async def enrich_batch_with_gmaps(
    leads: list[dict],
    api_key: str,
    only_missing_phone: bool = True
) -> list[dict]:
    """Runs parallel Gmaps Details lookups."""
    if not api_key or not leads:
        return leads
    
    sem = asyncio.Semaphore(5)  # Moderate concurrency
    
    async def bounded_enrich(lead: dict):
        if only_missing_phone and lead.get("phone"):
            return lead
            
        async with sem:
            city = lead.get("city") or _extract_city_from_address(lead.get("address", ""))
            gmaps_data = await get_gmaps_contact(lead["name"], city, api_key)
            
            if gmaps_data.get("_gmaps_closed"):
                lead["status"] = "CLOSED"
                return lead
                
            # Merge missing fields
            for k, v in gmaps_data.items():
                if not lead.get(k) and not k.startswith("_"):
                    lead[k] = v
            return lead

    return list(await asyncio.gather(*[bounded_enrich(l) for l in leads]))


def _extract_city_from_address(address: str) -> str:
    indian_cities = [
        "Mumbai", "Delhi", "Bangalore", "Bengaluru", "Pune", "Ahmedabad",
        "Hyderabad", "Chennai", "Kolkata", "Surat", "Jaipur", "Lucknow",
        "Nagpur", "Indore", "Bhopal", "Vadodara", "Agra", "Nashik",
        "Coimbatore", "Visakhapatnam", "Patna", "Ranchi", "Guwahati",
        "Chandigarh", "Kochi", "Thiruvananthapuram", "Mysuru",
    ]
    if not address: return ""
    for city in indian_cities:
        if city.lower() in address.lower():
            return city
    return ""
