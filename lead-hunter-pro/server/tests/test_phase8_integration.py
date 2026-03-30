import pytest
import os
import json
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
from main import app

# Force test mode to bypass auth via verify_api_key
# Selective auth bypass per test
# os.environ["APP_ENV"] = "test"

#   Mocking Octagon Waterfall  
@pytest.fixture
def mock_waterfall():
    with patch("services.enricher.find_email_octagon") as mock:
        mock.return_value = ("test@example.com", "mock_source")
        yield mock

@pytest.fixture
def mock_wa_health():
    with patch("services.whatsapp_client.httpx.AsyncClient") as mock_cls:
        mock_instance = mock_cls.return_value
        mock_instance.__aenter__.return_value.get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"ready": True}
        )
        yield mock_cls

@pytest.mark.asyncio
async def test_api_health_endpoint(mock_wa_health):
    """Verify combined health status includes WA server status."""
    with patch.dict(os.environ, {"APP_ENV": "test"}):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    if "status" not in data:
        print(f"DEBUG: Health Response Body = {data}")
    assert data["status"] == "ok"
    assert "wa_server" in data
    assert data["wa_server"] is True

@pytest.mark.asyncio
async def test_api_quota_unauthenticated():
    """Verify quota endpoint requires API key."""
    # Ensure APP_ENV is NOT test for this one to trigger real auth check
    with patch.dict(os.environ, {"APP_ENV": "prod"}):
        # We also need to ensure a master key exists to trigger 401 instead of 403
        with patch("utils.auth.get_authoritative_key", return_value="saumya_master"):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.get("/api/quota/status")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_api_quota_with_key():
    """Verify quota returns structured list of providers."""
    with patch.dict(os.environ, {"APP_ENV": "test"}):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/quota/status", headers={"X-API-Key": "test"})
    
    assert response.status_code == 200
    data = response.json()
    assert "quotas" in data
    assert isinstance(data["quotas"], list)

@pytest.mark.asyncio
async def test_stats_overview_data_aggregation():
    """Verify stats endpoint returns consolidated metrics."""
    with patch.dict(os.environ, {"APP_ENV": "test"}):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/stats/overview", headers={"X-API-Key": "test"})
    
    assert response.status_code == 200
    data = response.json()
    assert "total_leads" in data
    assert "enriched" in data
    assert "ready" in data
    assert "emailed" in data

@pytest.mark.asyncio
async def test_enrich_leados_to_octagon_bridge(mock_waterfall):
    """Verify Octagon waterfall is triggered when web scraping fails."""
    from services.enricher import enrich_lead
    
    # Input lead with no initial email
    lead = {"name": "Test Co", "website": "https://test.com"}
    
    # Mock scrape_website to return no emails
    with patch("services.enricher.scrape_website", new_callable=AsyncMock) as mock_scrape:
        mock_scrape.return_value = {
            "is_live": True, "tech_hints": [], "social": {}, 
            "has_contact_form": False, "emails": [], "phones_from_web": []
        }
        
        result = await enrich_lead(lead)
        
        # Verify Octagon waterfall was called
        mock_waterfall.assert_called_once()
        assert result["email"] == "test@example.com"
        assert result["email_source"] == "mock_source"
        assert result["status"] == "READY"
        assert result["emailqualityscore"] == 3

@pytest.mark.asyncio
async def test_phone_normalization():
    """Verify phone numbers are cleaned for WhatsApp delivery."""
    from utils.phone_normalizer import normalize_phone
    assert normalize_phone("+91-98765-43210") == "+919876543210"
    assert normalize_phone("09876 543 210") == "+919876543210" # Assuming default prefix is +91 for India
    assert normalize_phone("invalid") == ""

@pytest.mark.asyncio
async def test_email_quality_logic():
    """Verify unified email scoring (0-3)."""
    from services.email_waterfall_adapter import score_email_quality
    assert score_email_quality("john@test.com") == 3    # Named
    assert score_email_quality("ceo@test.com") == 2     # Role
    assert score_email_quality("info@test.com") == 1    # Generic
    assert score_email_quality("") == 0                 # Empty
