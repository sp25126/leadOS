import os
import httpx
from utils.rate_limiter import quota
from utils.request_manager import safe_get

FSQ_SEARCH_URL = "https://api.foursquare.com/v3/places/search"

FOURSQUARE_CATEGORY_IDS = {
    "cafe":        "13032",
    "restaurant":  "13065",
    "clinic":      "15014",
    "hospital":    "15011",
    "shop":        "17000",
    "salon":       "11134",
    "gym":         "18021",
    "hotel":       "19014",
    "pharmacy":    "15039",
    "bakery":      "13040",
    "bar":         "13003",
    "dentist":     "15027",
    "school":      "12058",
    "supermarket": "17069",
}


from utils import config_store

async def search_foursquare(
    query: str, location_str: str, radius_m: int = 5000
) -> list[dict]:
    if not quota.has_quota("foursquare"):
        print("    [Foursquare]    Monthly quota exhausted")
        return []

    api_key = config_store.get("foursquare_api_key", "FOURSQUARE_API_KEY")
    if not api_key:
        print("    [Foursquare]   API key missing")
        return []

    category_id = FOURSQUARE_CATEGORY_IDS.get(query.lower(), "")
    params = {
        "query":   query,
        "near":    location_str,
        "limit":   20,
        "radius":  radius_m,
        "fields":  "name,location,tel,website,rating,stats,categories",
    }
    if category_id:
        params["categories"] = category_id

    headers = {
        "Authorization": api_key,
        "Accept":        "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(FSQ_SEARCH_URL, params=params, headers=headers)
            resp.raise_for_status()
            result = resp.json()
    except Exception as e:
        print(f"    [Foursquare]   Error fetching: {e}")
        quota.consume("foursquare")
        return []

    quota.consume("foursquare")
    
    if not isinstance(result, dict) or "results" not in result:
        print(f"    [Foursquare]   Bad response or no results: {str(result)[:80]}")
        return []

    leads = []
    for place in result.get("results", []):
        loc     = place.get("location", {})
        website = place.get("website", "")
        phone   = "".join(c for c in place.get("tel", "") if c.isdigit() or c == "+")
        cats    = ", ".join(c.get("name", "") for c in place.get("categories", [])[:2])

        leads.append({
            "name":         place.get("name", ""),
            "address":      ", ".join(filter(None, [
                loc.get("address", ""),
                loc.get("locality", ""),
                loc.get("region", ""),
            ])),
            "phone":        phone,
            "website":      website,
            "email":        "",
            "has_website":  bool(website),
            "rating":       place.get("rating", 0.0),
            "review_count": place.get("stats", {}).get("total_ratings", 0),
            "types":        cats,
            "opening_hours": "",
            "lat":          loc.get("lat", 0),
            "lon":          loc.get("lng", 0),
            "source":       "foursquare",
        })
    return leads
