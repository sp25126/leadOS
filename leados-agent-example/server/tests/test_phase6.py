import pytest
import os
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport

INTERNAL_KEY = os.getenv("INTERNAL_API_KEY", "leadoskey123")

def get_app():
    """Import app fresh — avoids lifespan issues in tests."""
    from main import app
    return app


# ── Health & Quota ────────────────────────────────────────────────
@pytest.mark.anyio
async def test_health_endpoint():
    with patch("main.check_wa_ready", new_callable=AsyncMock, return_value=True):
        async with AsyncClient(
            transport=ASGITransport(app=get_app()),
            base_url="http://test"
        ) as client:
            r = await client.get("/api/health", headers={"X-API-Key": INTERNAL_KEY})
    assert r.status_code == 200
    body = r.json()
    assert body["status"]    == "ok"
    assert body["wa_server"] == True
    assert "timestamp"       in body


@pytest.mark.anyio
async def test_quota_status_returns_all_sources():
    async with AsyncClient(
        transport=ASGITransport(app=get_app()),
        base_url="http://test"
    ) as client:
        r = await client.get("/api/quota/status", headers={"X-API-Key": INTERNAL_KEY})
    assert r.status_code == 200
    data = r.json()
    required_sources = [
        "overpass_main", "overpass_kumi", "overpass_private",
        "google_maps", "foursquare", "here_places",
        "hunter_io", "abstract_email",
    ]
    for src in required_sources:
        assert src in data, f"Missing source: {src}"
    for src in required_sources:
        assert "remaining" in data[src]
        assert "used"      in data[src]


# ── Lead Search Validation ────────────────────────────────────────
@pytest.mark.anyio
async def test_leads_search_rejects_empty_business_type():
    async with AsyncClient(
        transport=ASGITransport(app=get_app()),
        base_url="http://test"
    ) as client:
        r = await client.post("/api/leads/search",
                              json={"business_type": "", "location": "Ahmedabad"},
                              headers={"X-API-Key": INTERNAL_KEY})
    assert r.status_code == 422


@pytest.mark.anyio
async def test_leads_search_rejects_empty_location():
    async with AsyncClient(
        transport=ASGITransport(app=get_app()),
        base_url="http://test"
    ) as client:
        r = await client.post("/api/leads/search",
                              json={"business_type": "cafe", "location": ""},
                              headers={"X-API-Key": INTERNAL_KEY})
    assert r.status_code == 422


@pytest.mark.anyio
async def test_leads_search_rejects_invalid_radius():
    async with AsyncClient(
        transport=ASGITransport(app=get_app()),
        base_url="http://test"
    ) as client:
        r = await client.post("/api/leads/search",
                              json={"business_type": "cafe",
                                    "location": "Mumbai", "radius_km": 0},
                              headers={"X-API-Key": INTERNAL_KEY})
    assert r.status_code == 422


# ── Lead Search Success ────────────────────────────────────────────
def _mock_lead():
    return {
        "name": "Test Cafe", "address": "Test St, Ahmedabad",
        "phone": "+919876543210", "email": "test@cafe.com",
        "website": "", "has_website": False, "rating": 4.5,
        "review_count": 120, "types": "cafe", "source": "osm",
        "merged_sources": "osm", "lat": 23.02, "lon": 72.57,
        "tech_hints": "", "social_media": "", "website_live": False,
        "has_contact_form": False, "opening_hours": "",
        "score": 9, "priority": "high", "reason": "No website, high reviews",
        "pain_points": ["no website", "no online menu"],
        "suggested_opening": "Hi Test Cafe...",
    }


@pytest.mark.anyio
async def test_leads_search_returns_structured_response():
    mock_lead = _mock_lead()
    with patch("routers.leads.discover_leads",
               new_callable=AsyncMock, return_value=[mock_lead]), \
         patch("routers.leads.enrich_all",
               new_callable=AsyncMock, return_value=[mock_lead]), \
         patch("routers.leads.find_email_for_lead",
               new_callable=AsyncMock, return_value="test@cafe.com"), \
         patch("routers.leads.score_leads",
               new_callable=AsyncMock, return_value=[mock_lead]):
        async with AsyncClient(
            transport=ASGITransport(app=get_app()),
            base_url="http://test"
        ) as client:
            r = await client.post("/api/leads/search",
                                  json={"business_type": "cafe",
                                        "location": "Ahmedabad"},
                                  headers={"X-API-Key": INTERNAL_KEY})
    assert r.status_code == 200
    body = r.json()
    assert "session_id"          in body
    assert "total"               in body
    assert "leads"               in body
    assert "high_priority_count" in body
    assert body["total"]                == 1
    assert body["high_priority_count"]  == 1
    assert body["leads"][0]["name"]     == "Test Cafe"
    assert body["leads"][0]["score"]    == 9
    assert body["leads"][0]["priority"] == "high"


@pytest.mark.anyio
async def test_leads_search_empty_returns_zero():
    with patch("routers.leads.discover_leads",
               new_callable=AsyncMock, return_value=[]):
        async with AsyncClient(
            transport=ASGITransport(app=get_app()),
            base_url="http://test"
        ) as client:
            r = await client.post("/api/leads/search",
                                  json={"business_type": "cafe",
                                        "location": "Nowhere"},
                                  headers={"X-API-Key": INTERNAL_KEY})
    assert r.status_code == 200
    assert r.json()["total"] == 0


# ── Download ──────────────────────────────────────────────────────
@pytest.mark.anyio
async def test_download_missing_session_returns_404():
    async with AsyncClient(
        transport=ASGITransport(app=get_app()),
        base_url="http://test"
    ) as client:
        r = await client.get("/api/leads/nonexistent_session_xyz/download", headers={"X-API-Key": INTERNAL_KEY})
    assert r.status_code == 404


# ── Outreach ──────────────────────────────────────────────────────
@pytest.mark.anyio
async def test_outreach_start_missing_session_returns_404():
    async with AsyncClient(
        transport=ASGITransport(app=get_app()),
        base_url="http://test"
    ) as client:
        r = await client.post("/api/outreach/start",
                              json={"session_id": "nonexistent_xyz_999"},
                              headers={"X-API-Key": INTERNAL_KEY})
    assert r.status_code == 404


@pytest.mark.anyio
async def test_outreach_status_missing_task_returns_404():
    async with AsyncClient(
        transport=ASGITransport(app=get_app()),
        base_url="http://test"
    ) as client:
        r = await client.get("/api/outreach/status/fakeid999", headers={"X-API-Key": INTERNAL_KEY})
    assert r.status_code == 404
