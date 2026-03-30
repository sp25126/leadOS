import pytest
from unittest.mock import AsyncMock, patch

from services.enricher     import scrape_website, is_valid_email, _extract_tech_hints
from services.deduplicator import deduplicate, normalize_name, is_duplicate
from services.email_finder import extract_domain, guess_emails


#   Enricher tests  

class TestEnricher:
    @pytest.mark.asyncio
    async def test_dead_website_returns_not_live(self):
        with patch("services.enricher.safe_get", new_callable=AsyncMock, return_value=None):
            result = await scrape_website("https://dead-site-xyz.example.com")
        assert result["is_live"] is False
        assert result["emails"] == []

    @pytest.mark.asyncio
    async def test_extracts_email_from_homepage(self):
        fake_html = (
            "<html><head><title>My Business</title></head><body>"
            "<header><nav>Home | About | Contact</nav></header>"
            "<main><p>Welcome to My Business. We are a leading provider of services.</p>"
            "<p>Contact us at hello@mybusiness.com for inquiries.</p></main>"
            "</body></html>"
        )
        with patch("services.enricher.safe_get", new_callable=AsyncMock, return_value=fake_html):
            result = await scrape_website("https://mybusiness.com")
        assert result["is_live"] is True
        assert "hello@mybusiness.com" in result["emails"]

    def test_rejects_noreply_email(self):
        assert is_valid_email("noreply@company.com") is False
        assert is_valid_email("no-reply@company.com") is False
        assert is_valid_email("contact@company.com") is True

    def test_detects_wordpress(self):
        html = "<link rel='stylesheet' href='/wp-content/themes/main.css'>"
        hints = _extract_tech_hints(html.lower())
        assert "wordpress" in hints


#   Deduplicator tests  

class TestDeduplicator:
    def _lead(self, name, phone="", address="", source="osm"):
        return {
            "name": name, "phone": phone, "address": address,
            "website": "", "email": "", "has_website": False,
            "rating": 0.0, "review_count": 0,
            "types": "", "opening_hours": "", "lat": 0, "lon": 0,
            "source": source,
        }

    def test_exact_duplicate_removed(self):
        leads = [
            self._lead("Chai Point", phone="9876543210"),
            self._lead("Chai Point", phone="9876543210"),
        ]
        result = deduplicate(leads)
        assert len(result) == 1
        assert result[0]["merged_sources"] is not None

    def test_different_businesses_kept(self):
        leads = [
            self._lead("Chai Point",   address="MG Road, Ahmedabad"),
            self._lead("Coffee House", address="CG Road, Ahmedabad"),
        ]
        result = deduplicate(leads)
        assert len(result) == 2

    def test_fuzzy_name_match_deduped(self):
        leads = [
            self._lead("Chai Point Cafe", address="MG Road, Ahmedabad"),
            self._lead("Chai Point",      address="MG Road, Ahmedabad"),
        ]
        result = deduplicate(leads)
        # "cafe" is a stopword - both normalise to "chai point" -> duplicate
        assert len(result) == 1


#   Email finder tests  

class TestEmailFinder:
    def test_extract_domain_strips_www(self):
        assert extract_domain("https://www.mybusiness.com") == "mybusiness.com"
        assert extract_domain("http://mybusiness.in/about") == "mybusiness.in"

    def test_guess_emails_includes_info_fallback(self):
        emails = guess_emails("example.com", "Ravi Sharma")
        assert any("info@" in e for e in emails)
        assert any("ravi" in e for e in emails)

    def test_guess_emails_single_name(self):
        # Single-word name - templates needing {last} are skipped gracefully
        emails = guess_emails("example.com", "Zomato")
        assert len(emails) > 0
        assert all("@example.com" in e for e in emails)
