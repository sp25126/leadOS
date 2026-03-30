import os
from utils.rate_limiter import quota
from utils.request_manager import safe_get

HERE_GEOCODE_URL  = "https://geocode.search.hereapi.com/v1/geocode"
HERE_DISCOVER_URL = "https://discover.search.hereapi.com/v1/discover"


async def _geocode_here(location_str: str, api_key: str) -> tuple[float, float] | None:
    result = await safe_get(
        HERE_GEOCODE_URL,
        params={"q": location_str, "apiKey": api_key, "limit": 1}
    )
    if isinstance(result, dict) and result.get("items"):
        pos = result["items"][0].get("position", {})
        return pos.get("lat", 0), pos.get("lng", 0)
    return None


async def search_here(
    query: str, location_str: str, radius_m: int = 5000
) -> list[dict]:
    if not quota.has_quota("here_places"):
        print("    [HERE Places]    Daily quota exhausted (resets midnight)")
        return []

    api_key = os.getenv("HERE_API_KEY", "")
    if not api_key:
        print("    [HERE Places]   API key missing")
        return []

    coords = await _geocode_here(location_str, api_key)
    quota.consume("here_places")   # geocode = 1 credit

    if not coords:
        print(f"    [HERE Places]   Geocoding failed for: {location_str}")
        return []

    lat, lon = coords
    result   = await safe_get(
        HERE_DISCOVER_URL,
        params={
            "at":     f"{lat},{lon}",
            "q":      query,
            "limit":  20,
            "in":     f"circle:{lat},{lon};r={radius_m}",
            "apiKey": api_key,
            "lang":   "en",
        }
    )
    quota.consume("here_places")   # discover = 1 credit

    if not isinstance(result, dict) or "items" not in result:
        print(f"    [HERE Places]   Bad response or no items: {str(result)[:80]}")
        return []

    leads = []
    for item in result.get("items", []):
        addr    = item.get("address", {})
        pos     = item.get("position", {})
        website = item.get("contacts", [{}])[0].get("www", [{}])[0].get("value", "") \
                  if item.get("contacts") else ""
        phone   = item.get("contacts", [{}])[0].get("phone", [{}])[0].get("value", "") \
                  if item.get("contacts") else ""
        phone   = "".join(c for c in phone if c.isdigit() or c == "+")

        leads.append({
            "name":         item.get("title", ""),
            "address":      addr.get("label", ""),
            "phone":        phone,
            "website":      website,
            "email":        "",
            "has_website":  bool(website),
            "rating":       0.0,
            "review_count": 0,
            "types":        item.get("categoryTitle", ""),
            "opening_hours": "",
            "lat":          pos.get("lat", 0),
            "lon":          pos.get("lng", 0),
            "source":       "here",
        })
    return leads
