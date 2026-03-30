import pytest
from httpx import AsyncClient, ASGITransport
from main import app
import io, csv

def make_csv(rows: list[dict]) -> bytes:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")

@pytest.mark.anyio
async def test_upload_csv_success():
    csv_data = make_csv([
        {"company_name": "Test Cafe", "phone": "9876543210",
         "email": "test@testcafe.com", "website": "testcafe.com"},
        {"company_name": "Clinic One", "phone": "9988776655",
         "email": "info@clinicone.com", "website": ""},
    ])
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post(
            "/api/leads/upload",
            files={"file": ("leads.csv", csv_data, "text/csv")},
            data={"target_service": "website design", "score_with_ai": "false"},
            headers={"X-API-Key": os.getenv("INTERNAL_API_KEY")}
        )
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    assert body["with_email"] == 2
    assert "session_id" in body
    assert body["session_id"].startswith("upload_")

@pytest.mark.anyio
async def test_upload_rejects_empty_file():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post(
            "/api/leads/upload",
            files={"file": ("empty.csv", b"name,email\n", "text/csv")},
            data={"target_service": "website design", "score_with_ai": "false"},
            headers={"X-API-Key": os.getenv("INTERNAL_API_KEY")}
        )
    assert r.status_code == 422

@pytest.mark.anyio
async def test_upload_rejects_unsupported_format():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post(
            "/api/leads/upload",
            files={"file": ("leads.pdf", b"garbage", "application/pdf")},
            data={"target_service": "website design", "score_with_ai": "false"},
            headers={"X-API-Key": os.getenv("INTERNAL_API_KEY")}
        )
    assert r.status_code == 422

@pytest.mark.anyio
async def test_phone_normalization():
    csv_data = make_csv([
        {"name": "Biz A", "phone": "9876543210", "email": "a@biz.com"},  # 10 digit
        {"name": "Biz B", "phone": "+919988776655", "email": "b@biz.com"},  # already normalized
        {"name": "Biz C", "phone": "919988776655", "email": "c@biz.com"},  # 12 digit with 91
    ])
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post(
            "/api/leads/upload",
            files={"file": ("test.csv", csv_data, "text/csv")},
            data={"target_service": "automation", "score_with_ai": "false"},
            headers={"X-API-Key": "leadoskey123"}
        )
    assert r.status_code == 200
    leads = r.json()["leads_preview"]
    assert leads[0]["phone"] == "+919876543210"
