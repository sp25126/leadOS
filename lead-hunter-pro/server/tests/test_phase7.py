import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, Message, User, Chat, Bot
from telegram.ext import ContextTypes


#   Factories  
def make_update(text: str, user_id: int = 12345,
                args: list[str] | None = None) -> tuple[Update, MagicMock]:
    user         = MagicMock(spec=User)
    user.id      = user_id
    user.first_name = "TestUser"

    message                  = MagicMock(spec=Message)
    message.text             = text
    message.reply_text       = AsyncMock(return_value=MagicMock(
        edit_text=AsyncMock(),
        reply_document=AsyncMock(),
    ))
    message.reply_document   = AsyncMock()

    update                   = MagicMock(spec=Update)
    update.effective_user    = user
    update.message           = message

    ctx      = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    ctx.args = args or []
    return update, ctx


#   /start  
class TestCmdStart:

    @pytest.mark.asyncio
    async def test_start_sends_message(self):
        from bot.telegram_bot import cmd_start
        update, ctx = make_update("/start")
        await cmd_start(update, ctx)
        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        assert "Lead Hunter Pro" in text
        assert "/leads"          in text
        assert "/outreach"       in text

    @pytest.mark.asyncio
    async def test_start_contains_all_commands(self):
        from bot.telegram_bot import cmd_start
        update, ctx = make_update("/start")
        await cmd_start(update, ctx)
        text = update.message.reply_text.call_args[0][0]
        for cmd in ["/leads", "/outreach", "/status", "/quota", "/help"]:
            assert cmd in text, f"Missing command: {cmd}"


#   /help  
class TestCmdHelp:

    @pytest.mark.asyncio
    async def test_help_shows_examples(self):
        from bot.telegram_bot import cmd_help
        update, ctx = make_update("/help")
        await cmd_help(update, ctx)
        text = update.message.reply_text.call_args[0][0]
        assert "cafe Ahmedabad" in text
        assert "clinic"         in text
        assert "50 WA"          in text


#   /quota  
class TestCmdQuota:

    @pytest.mark.asyncio
    async def test_quota_shows_all_sources(self):
        from bot.telegram_bot import cmd_quota
        update, ctx = make_update("/quota")
        await cmd_quota(update, ctx)
        text = update.message.reply_text.call_args[0][0]
        assert "Google Maps"  in text
        assert "Foursquare"   in text
        assert "Hunter.io"    in text
        assert "OSM"          in text


#   /status  
class TestCmdStatus:

    @pytest.mark.asyncio
    async def test_status_shows_counts(self):
        from bot.telegram_bot import cmd_status
        update, ctx = make_update("/status")
        await cmd_status(update, ctx)
        text = update.message.reply_text.call_args[0][0]
        assert "WhatsApp" in text
        assert "Email"    in text


#   /leads  
class TestCmdLeads:

    @pytest.mark.asyncio
    async def test_leads_requires_two_args(self):
        from bot.telegram_bot import cmd_leads, _active_jobs
        update, ctx = make_update("/leads", args=["cafe"])   # missing city
        _active_jobs[update.effective_user.id] = False
        await cmd_leads(update, ctx)
        text = update.message.reply_text.call_args[0][0]
        assert "Usage" in text or "usage" in text.lower()

    @pytest.mark.asyncio
    async def test_leads_blocks_concurrent_jobs(self):
        from bot.telegram_bot import cmd_leads, _active_jobs
        uid = 99991
        _active_jobs[uid] = True
        update, ctx = make_update("/leads", user_id=uid, args=["cafe", "Mumbai"])
        await cmd_leads(update, ctx)
        text = update.message.reply_text.call_args[0][0]
        assert "already" in text.lower()
        _active_jobs[uid] = False

    @pytest.mark.asyncio
    async def test_leads_full_pipeline_happy_path(self):
        from bot.telegram_bot import cmd_leads, _active_jobs, _user_sessions
        uid = 99992
        _active_jobs[uid] = False

        mock_lead = {
            "name": "Test Cafe", "phone": "+919876543210",
            "email": "t@cafe.com", "website": "", "has_website": False,
            "address": "Test St", "score": 9, "priority": "high",
            "pain_points": ["no website"], "suggested_opening": "Hi",
            "types": "cafe", "rating": 4.5, "review_count": 100,
            "source": "osm", "merged_sources": "osm",
            "tech_hints": "", "social_media": "", "website_live": False,
            "has_contact_form": False, "lat": 0.0, "lon": 0.0,
            "opening_hours": "", "reason": "no website",
        }

        update, ctx = make_update(
            "/leads cafe Ahmedabad", user_id=uid,
            args=["cafe", "Ahmedabad"]
        )
        # Mock reply_text to return object with edit_text + reply_document
        status_mock            = MagicMock()
        status_mock.edit_text  = AsyncMock()
        update.message.reply_text    = AsyncMock(return_value=status_mock)
        update.message.reply_document = AsyncMock()

        with patch("bot.telegram_bot.discover_leads",
                   new_callable=AsyncMock, return_value=[mock_lead]), \
             patch("bot.telegram_bot.enrich_all",
                   new_callable=AsyncMock, return_value=[mock_lead]), \
             patch("bot.telegram_bot.find_email_for_lead",
                   new_callable=AsyncMock, return_value="t@cafe.com"), \
             patch("bot.telegram_bot.score_leads",
                   new_callable=AsyncMock, return_value=[mock_lead]):

            await cmd_leads(update, ctx)

        # Session should be stored
        assert uid in _user_sessions
        assert "cafe"      in _user_sessions[uid]
        assert "ahmedabad" in _user_sessions[uid]

        # CSV should have been sent as document
        update.message.reply_document.assert_called_once()

        # Active job cleared
        assert _active_jobs.get(uid) == False

    @pytest.mark.asyncio
    async def test_leads_no_results_sends_apology(self):
        from bot.telegram_bot import cmd_leads, _active_jobs
        uid = 99993
        _active_jobs[uid] = False

        update, ctx = make_update(
            "/leads cafe Nowhere", user_id=uid, args=["cafe", "Nowhere"]
        )
        status_mock           = MagicMock()
        status_mock.edit_text = AsyncMock()
        update.message.reply_text = AsyncMock(return_value=status_mock)

        with patch("bot.telegram_bot.discover_leads",
                   new_callable=AsyncMock, return_value=[]):
            await cmd_leads(update, ctx)

        # edit_text should mention no leads found
        last_edit = status_mock.edit_text.call_args[0][0]
        assert "No leads" in last_edit or "no leads" in last_edit.lower()

        # Active job should be cleared even on empty result
        assert _active_jobs.get(uid) == False


#   /outreach  
class TestCmdOutreach:

    @pytest.mark.asyncio
    async def test_outreach_no_args_no_session_fails(self):
        from bot.telegram_bot import cmd_outreach, _active_jobs, _user_sessions
        uid = 88881
        _active_jobs[uid] = False
        _user_sessions.pop(uid, None)  # ensure no session stored

        update, ctx = make_update("/outreach", user_id=uid, args=[])
        await cmd_outreach(update, ctx)
        text = update.message.reply_text.call_args[0][0]
        assert "No recent session" in text or "first" in text.lower()

    @pytest.mark.asyncio
    async def test_outreach_missing_session_csv_fails(self):
        from bot.telegram_bot import cmd_outreach, _active_jobs
        uid = 88882
        _active_jobs[uid] = False

        update, ctx = make_update(
            "/outreach fake_session_xyz", user_id=uid,
            args=["fake_session_xyz_99999"]
        )
        await cmd_outreach(update, ctx)
        text = update.message.reply_text.call_args[0][0]
        assert "No leads" in text or "not found" in text.lower() \
               or " " in text


#   Helpers  
class TestHelpers:

    def test_leads_to_csv_bytes_empty(self):
        from bot.telegram_bot import _leads_to_csv_bytes
        assert _leads_to_csv_bytes([]) == b""

    def test_leads_to_csv_bytes_has_header(self):
        from bot.telegram_bot import _leads_to_csv_bytes
        leads  = [{"name": "Cafe A", "phone": "+91123", "email": "a@b.com"}]
        result = _leads_to_csv_bytes(leads).decode("utf-8")
        assert "name"   in result
        assert "Cafe A" in result

    def test_format_quota_table_has_sources(self):
        from bot.telegram_bot import _format_quota_table
        table = _format_quota_table()
        assert "Google Maps" in table
        assert "Foursquare"  in table
        assert "Hunter.io"   in table

    def test_format_lead_line_no_website(self):
        from bot.telegram_bot import _format_lead_line
        lead = {"name": "Ravi Cafe", "has_website": False, "score": 9}
        line = _format_lead_line(lead, 1)
        assert "Ravi Cafe"  in line
        assert "No website" in line
        assert "9/10"       in line

    def test_format_lead_line_has_website(self):
        from bot.telegram_bot import _format_lead_line
        lead = {"name": "Modern Co", "has_website": True, "score": 5}
        line = _format_lead_line(lead, 2)
        assert "Has website" in line

    def test_daily_stats_reset(self):
        from bot.telegram_bot import _reset_daily_if_needed, _daily_stats
        _daily_stats["reset_date"] = "2000-01-01"
        _daily_stats["wa_sent"]    = 999
        _daily_stats["email_sent"] = 999
        _reset_daily_if_needed()
        assert _daily_stats["wa_sent"]    == 0
        assert _daily_stats["email_sent"] == 0
