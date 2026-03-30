import pytest
from unittest.mock import AsyncMock, patch, MagicMock


#   WhatsApp Client  
class TestWhatsappClient:

    @pytest.mark.asyncio
    async def test_returns_offline_when_server_down(self):
        from services.whatsapp_client import send_whatsapp
        with patch("services.whatsapp_client.httpx.AsyncClient") as mock_cls:
            mock_cls.return_value.__aenter__.return_value.post\
                .side_effect = __import__("httpx").ConnectError("refused")
            result = await send_whatsapp("+919876543210", "Hello")
        assert result["status"] == "wa_server_offline"

    @pytest.mark.asyncio
    async def test_returns_sent_on_success(self):
        from services.whatsapp_client import send_whatsapp
        mock_resp             = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"status": "sent", "messageId": "abc123"}
        with patch("services.whatsapp_client.httpx.AsyncClient") as mock_cls:
            mock_cls.return_value.__aenter__.return_value.post\
                .return_value = mock_resp
            result = await send_whatsapp("+919876543210", "Hello")
        assert result["status"] == "sent"

    @pytest.mark.asyncio
    async def test_health_check_returns_bool(self):
        from services.whatsapp_client import check_wa_ready
        mock_resp             = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"ready": True}
        with patch("services.whatsapp_client.httpx.AsyncClient") as mock_cls:
            mock_cls.return_value.__aenter__.return_value.get\
                .return_value = mock_resp
            result = await check_wa_ready()
        assert result is True


#   Email Sender  
class TestEmailSender:

    @pytest.mark.asyncio
    async def test_invalid_email_skipped(self):
        from services.email_sender import send_email
        result = await send_email("notanemail", "Test", "Subject", "Body")
        assert result["status"] == "email_skipped"

    @pytest.mark.asyncio
    async def test_empty_email_skipped(self):
        from services.email_sender import send_email
        result = await send_email("", "Test", "Subject", "Body")
        assert result["status"] == "email_skipped"

    @pytest.mark.asyncio
    async def test_brevo_called_on_valid_email(self):
        from services.email_sender import send_email
        with patch("services.email_sender._send_sync",
                   return_value={"status": "sent_email", "to": "t@t.com"}) as mock_sync:
            result = await send_email("t@t.com", "Test", "Subject", "Body")
        assert result["status"] == "sent_email"
        mock_sync.assert_called_once()


#   Personalizer  
class TestPersonalizer:

    def make_lead(self):
        return {
            "name": "Ravi Cafe", "types": "cafe", "has_website": False,
            "rating": 4.5, "review_count": 180, "address": "CG Road",
            "tech_hints": "", "pain_points": ["no website"],
            "suggested_opening": "Hi Ravi, noticed your cafe...",
        }

    @pytest.mark.asyncio
    async def test_wa_message_returns_string(self):
        from services.personalizer import generate_whatsapp_message
        mock_resp      = MagicMock()
        mock_resp.text = "Hi Ravi! Love that your cafe has 180 reviews. Have you thought about an online menu?"
        with patch("services.personalizer._model") as mock_model, \
             patch("services.personalizer.asyncio.sleep", new_callable=AsyncMock):
            mock_model.generate_content.return_value = mock_resp
            result = await generate_whatsapp_message(self.make_lead())
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_wa_message_under_350_chars(self):
        from services.personalizer import generate_whatsapp_message
        mock_resp      = MagicMock()
        mock_resp.text = "A" * 500   # Simulate over-long Gemini response
        with patch("services.personalizer._model") as mock_model, \
             patch("services.personalizer.asyncio.sleep", new_callable=AsyncMock):
            mock_model.generate_content.return_value = mock_resp
            result = await generate_whatsapp_message(self.make_lead())
        assert len(result) <= 350

    @pytest.mark.asyncio
    async def test_wa_fallback_on_gemini_error(self):
        from services.personalizer import generate_whatsapp_message
        with patch("services.personalizer._model") as mock_model, \
             patch("services.personalizer.asyncio.sleep", new_callable=AsyncMock):
            mock_model.generate_content.side_effect = Exception("quota exceeded")
            result = await generate_whatsapp_message(self.make_lead())
        assert isinstance(result, str)
        assert len(result) > 0   # Fallback template used

    @pytest.mark.asyncio
    async def test_email_returns_subject_and_body(self):
        from services.personalizer import generate_email
        import json
        mock_resp      = MagicMock()
        mock_resp.text = json.dumps({
            "subject": "Your cafe is missing online orders",
            "body":    "Hi Ravi, noticed your cafe on CG Road..."
        })
        with patch("services.personalizer._model") as mock_model, \
             patch("services.personalizer.asyncio.sleep", new_callable=AsyncMock):
            mock_model.generate_content.return_value = mock_resp
            result = await generate_email(self.make_lead())
        assert "subject" in result
        assert "body"    in result
        assert len(result["subject"]) <= 80

    @pytest.mark.asyncio
    async def test_email_fallback_on_bad_json(self):
        from services.personalizer import generate_email
        mock_resp      = MagicMock()
        mock_resp.text = "Not valid JSON at all"
        with patch("services.personalizer._model") as mock_model, \
             patch("services.personalizer.asyncio.sleep", new_callable=AsyncMock):
            mock_model.generate_content.return_value = mock_resp
            result = await generate_email(self.make_lead())
        assert "subject" in result
        assert "body"    in result


#   Batch Sender  
class TestBatchSender:

    def make_leads(self, n: int) -> list[dict]:
        return [{
            "name": f"Business {i}", "phone": f"+9198765{i:05d}",
            "email": f"biz{i}@test.com", "has_website": False,
            "score": 8, "priority": "high", "pain_points": [],
            "suggested_opening": "Hi", "types": "cafe",
            "rating": 4.0, "review_count": 100,
            "address": "Test St", "tech_hints": "",
        } for i in range(n)]

    @pytest.mark.asyncio
    async def test_batch_respects_wa_limit(self):
        from services.batch_sender import run_batch
        leads = self.make_leads(10)
        with patch("services.batch_sender.check_wa_ready",          return_value=True), \
             patch("services.batch_sender.send_whatsapp",
                   return_value={"status": "sent"}), \
             patch("services.batch_sender.generate_whatsapp_message",
                   return_value="Test WA"), \
             patch("services.batch_sender.BATCH_WA_LIMIT", 3), \
             patch("services.batch_sender.BATCH_EMAIL_LIMIT", 3), \
             patch("services.batch_sender.asyncio.sleep", new_callable=AsyncMock):
            results, next_idx = await run_batch(leads, 0, 1, [])
        wa_sent = sum(1 for r in results if r["channel"] == "WhatsApp"
                      and r["status"] == "sent")
        assert wa_sent <= 3

    @pytest.mark.asyncio
    async def test_falls_back_to_email_when_wa_offline(self):
        from services.batch_sender import run_batch
        leads = self.make_leads(3)
        with patch("services.batch_sender.check_wa_ready",    return_value=False), \
             patch("services.batch_sender.send_email",
                   return_value={"status": "sent_email"}), \
             patch("services.batch_sender.generate_email",
                   return_value={"subject": "S", "body": "B"}), \
             patch("services.batch_sender.BATCH_WA_LIMIT",    50), \
             patch("services.batch_sender.BATCH_EMAIL_LIMIT", 50), \
             patch("services.batch_sender.asyncio.sleep", new_callable=AsyncMock):
            results, _ = await run_batch(leads, 0, 1, [])
        channels = [r["channel"] for r in results if r["status"] == "sent"]
        assert all(c == "Email" for c in channels)

    @pytest.mark.asyncio
    async def test_skips_lead_with_no_contact(self):
        from services.batch_sender import run_batch
        leads = [{"name": "Ghost Biz", "phone": "", "email": "",
                  "has_website": False, "score": 5, "priority": "medium",
                  "pain_points": [], "suggested_opening": "", "types": "shop",
                  "rating": 0, "review_count": 0, "address": "", "tech_hints": ""}]
        with patch("services.batch_sender.check_wa_ready", return_value=True), \
             patch("services.batch_sender.BATCH_WA_LIMIT",    50), \
             patch("services.batch_sender.BATCH_EMAIL_LIMIT", 50):
            results, _ = await run_batch(leads, 0, 1, [])
        assert results[0]["status"] == "skipped"

    @pytest.mark.asyncio
    async def test_returns_correct_next_index(self):
        from services.batch_sender import run_batch
        leads = self.make_leads(5)
        with patch("services.batch_sender.check_wa_ready",    return_value=False), \
             patch("services.batch_sender.send_email",
                   return_value={"status": "sent_email"}), \
             patch("services.batch_sender.generate_email",
                   return_value={"subject": "S", "body": "B"}), \
             patch("services.batch_sender.BATCH_WA_LIMIT",    50), \
             patch("services.batch_sender.BATCH_EMAIL_LIMIT", 50), \
             patch("services.batch_sender.asyncio.sleep", new_callable=AsyncMock):
            results, next_idx = await run_batch(leads, 0, 1, [])
        assert next_idx == 5   # All 5 processed
