import os
from utils.rate_limiter import quota
from utils.request_manager import safe_post

PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = ",".join([
    "places.displayName", "places.formattedAddress",
    "places.nationalPhoneNumber", "places.internationalPhoneNumber",
    "places.websiteUri", "places.rating",
    "places.userRatingCount", "places.businessStatus",
    "places.types", "places.location",
])


async def search_google_places(
    query: str, location_str: str, radius_m: int = 5000
) -> list[dict]:
    if not quota.has_quota("google_maps"):
        print("    [Google Maps] ⚠️  Monthly quota exhausted")
        return []

    api_key = os.getenv("GOOGLE_PLACES_API_KEY", "")
    if not api_key:
        print("    [Google Maps] ❌ API key missing")
        return []

    headers = {
        "X-Goog-Api-Key":   api_key,
        "X-Goog-FieldMask": FIELD_MASK,
        "Content-Type":     "application/json",
    }
    body = {
        "textQuery":      f"{query} in {location_str}",
        "maxResultCount": 20,
        "languageCode":   "en",
    }

    result = await safe_post(PLACES_URL, json_body=body)
    quota.consume("google_maps")

    if not isinstance(result, dict) or "places" not in result:
        print(f"    [Google Maps] ❌ Bad response or no places: {str(result)[:80]}")
        return []

    leads = []
    for p in result.get("places", []):
        if p.get("businessStatus") == "CLOSED_PERMANENTLY":
            continue

        phone = (
            p.get("internationalPhoneNumber") or
            p.get("nationalPhoneNumber") or ""
        )
        phone = "".join(c for c in phone if c.isdigit() or c == "+")

        website = p.get("websiteUri", "")
        loc     = p.get("location", {})

        leads.append({
            "name":         p.get("displayName", {}).get("text", ""),
            "address":      p.get("formattedAddress", ""),
            "phone":        phone,
            "website":      website,
            "email":        "",
            "has_website":  bool(website),
            "rating":       p.get("rating", 0.0),
            "review_count": p.get("userRatingCount", 0),
            "types":        ", ".join(p.get("types", [])[:3]),
            "opening_hours": "",
            "lat":          loc.get("latitude", 0),
            "lon":          loc.get("longitude", 0),
            "source":       "google_maps",
        })
    return leads
