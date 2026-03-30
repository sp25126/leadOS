import asyncio
import csv
import io
import os
import time
from datetime import datetime

from telegram import (
    Bot, Update, InlineKeyboardButton,
    InlineKeyboardMarkup, BotCommand,
)
from telegram.ext import (
    Application, CommandHandler,
    ContextTypes, CallbackQueryHandler, MessageHandler, filters,
)
from telegram.constants import ParseMode
from telegram.error import TelegramError

from services.source_manager import discover_leads
from services.enricher        import enrich_all
from services.lead_scorer     import score_leads
from services.email_finder    import find_email_for_lead
from services.batch_sender    import run_all_batches
from utils.rate_limiter       import quota

from utils import config_store

def get_token():
    return config_store.telegram_token()

def get_domain():
    return config_store.get("domain", "DOMAIN")

#   Per-user active job guard (1 job per user at a time)  
_active_jobs: dict[int, bool] = {}

#   Session store { user_id: last_session_id }  
_user_sessions: dict[int, str] = {}

#   Daily counter (resets at midnight, persists in memory)  
_daily_stats: dict[str, int] = {"wa_sent": 0, "email_sent": 0, "reset_date": ""}


def _reset_daily_if_needed():
    today = str(datetime.now().date())
    if _daily_stats["reset_date"] != today:
        _daily_stats["wa_sent"]    = 0
        _daily_stats["email_sent"] = 0
        _daily_stats["reset_date"] = today


def _leads_to_csv_bytes(leads: list[dict]) -> bytes:
    if not leads:
        return b""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=leads[0].keys())
    writer.writeheader()
    writer.writerows(leads)
    return output.getvalue().encode("utf-8")


def _format_lead_line(lead: dict, rank: int) -> str:
    website_tag = "  Has website" if lead.get("has_website") else "  No website"
    score       = lead.get("score", "?")
    return f"{rank}. *{lead['name']}* | {score}/10 | {website_tag}"


def _format_quota_table() -> str:
    lines = ["  *API Credits Remaining*\n"]
    info  = {
        "OSM Overpass ( 3)": sum(
            quota.remaining(k) for k in
            ["overpass_main", "overpass_kumi", "overpass_private"]
        ),
        "Google Maps":  quota.remaining("google_maps"),
        "Foursquare":   quota.remaining("foursquare"),
        "HERE Places":  quota.remaining("here_places"),
        "Hunter.io":    quota.remaining("hunter_io"),
        "Email Verify": quota.remaining("abstract_email"),
    }
    for name, rem in info.items():
        icon = " " if rem > 100 else (" " if rem > 20 else " ")
        lines.append(f"{icon} {name:<22} `{rem}` left")
    return "\n".join(lines)


#   /start  
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (
        "  *Lead Hunter Pro*\n\n"
        "I find real local businesses, score them with AI,\n"
        "and send personalised WhatsApp + Email outreach.\n\n"
        "  *Commands:*\n"
        "`/leads [type] [city]` - Find & score leads\n"
        "  _Example: /leads cafe Ahmedabad_\n"
        "  _Example: /leads clinic Mumbai_\n\n"
        "`/outreach [session\\_id]` - Start outreach\n"
        "  _Use 'last' for most recent session_\n\n"
        "`/status` - Today's send counts\n"
        "`/quota`  - Detailed API credit table\n"
        "`/help`   - More examples\n"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


#   /help  
async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (
        "  *Usage Examples*\n\n"
        "*Find leads:*\n"
        "`/leads cafe Ahmedabad`\n"
        "`/leads clinic Surat`\n"
        "`/leads restaurant Bangalore`\n"
        "`/leads salon Pune`\n"
        "`/leads gym Mumbai`\n\n"
        "*Start outreach:*\n"
        "`/outreach last` - use last searched session\n"
        "`/outreach cafe_ahmedabad_1234` - specific session\n\n"
        "*Business types supported:*\n"
        "cafe, restaurant, clinic, hospital, shop,\n"
        "salon, gym, hotel, pharmacy, school,\n"
        "bakery, bar, supermarket, dentist, office\n\n"
        "*Outreach schedule:*\n"
        "Batch 1: 50 WA + 150 Email\n"
        "Gap: 7-8 hrs (random)\n"
        "Batch 2: 50 WA + 150 Email"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


#   /quota  
async def cmd_quota(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        _format_quota_table(), parse_mode=ParseMode.MARKDOWN
    )


#   /status  
async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    _reset_daily_if_needed()
    uid          = update.effective_user.id
    active       = _active_jobs.get(uid, False)
    last_session = _user_sessions.get(uid, "None")

    text = (
        f"  *Today's Activity*\n\n"
        f"  WhatsApp sent : `{_daily_stats['wa_sent']}`\n"
        f"  Email sent    : `{_daily_stats['email_sent']}`\n"
        f"   Active job    : {'  Running' if active else '  Free'}\n"
        f"  Last session  : `{last_session}`\n\n"
        + _format_quota_table()
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


#   /leads  
async def cmd_leads(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    args = ctx.args

    if len(args) < 2:
        await update.message.reply_text(
            "  Usage: `/leads [business_type] [city]`\n"
            "Example: `/leads cafe Ahmedabad`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if _active_jobs.get(uid):
        await update.message.reply_text(
            "  You already have an active job running. Wait for it to finish."
        )
        return

    business_type = args[0].lower()
    city          = " ".join(args[1:])
    _active_jobs[uid] = True

    status_msg = await update.message.reply_text(
        f"  Searching for *{business_type}* in *{city}*...\n"
        f"  This takes 30-60s depending on sources available.",
        parse_mode=ParseMode.MARKDOWN
    )

    try:
        # Stage 1: Discover
        await status_msg.edit_text(
            f"  *Stage 1/4* - Discovering leads from OSM + Google + Foursquare...",
            parse_mode=ParseMode.MARKDOWN
        )
        raw_leads = await discover_leads(business_type, city, radius_km=5)

        if not raw_leads:
            await status_msg.edit_text(
                f"  No leads found for *{business_type}* in *{city}*.\n"
                "Try a different city or business type.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Stage 2: Enrich
        await status_msg.edit_text(
            f"  *Stage 2/4* - Enriching {len(raw_leads)} leads "
            f"(website scan, email extraction)...",
            parse_mode=ParseMode.MARKDOWN
        )
        enriched = await enrich_all(raw_leads, concurrency=5)

        # Stage 3: Email fallback
        await status_msg.edit_text(
            f"  *Stage 3/4* - Finding missing emails...",
            parse_mode=ParseMode.MARKDOWN
        )
        for lead in enriched:
            if not lead.get("email"):
                lead["email"] = await find_email_for_lead(lead)

        # Stage 4: Score
        await status_msg.edit_text(
            f"  *Stage 4/4* - AI scoring {len(enriched)} leads...",
            parse_mode=ParseMode.MARKDOWN
        )
        scored = await score_leads(enriched, "website and AI automation")

        # Save session
        ts         = int(time.time())
        session_id = f"{business_type}_{city}_{ts}".replace(" ", "_").lower()
        _user_sessions[uid] = session_id

        # Save CSV to output/
        os.makedirs("output", exist_ok=True)
        csv_path = f"output/leads_{session_id}.csv"
        if scored:
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=scored[0].keys())
                writer.writeheader()
                writer.writerows(scored)

        # Build summary
        high  = sum(1 for l in scored if l.get("priority") == "high")
        medium = sum(1 for l in scored if l.get("priority") == "medium")
        top3  = scored[:3]

        top3_text = "\n".join(
            _format_lead_line(l, i + 1) for i, l in enumerate(top3)
        )

        summary = (
            f"  Found *{len(scored)} leads* for {business_type} in {city}\n\n"
            f"  High priority : `{high}`\n"
            f"  Medium        : `{medium}`\n\n"
            f"*Top {len(top3)} leads:*\n{top3_text}\n\n"
            f"  Session: `{session_id}`\n\n"
            f"Run `/outreach {session_id}` to start sending\n"
            f"or `/outreach last` as shortcut."
        )

        await status_msg.edit_text(summary, parse_mode=ParseMode.MARKDOWN)

        # Send CSV as file
        csv_bytes = _leads_to_csv_bytes(scored)
        if csv_bytes:
            await update.message.reply_document(
                document = io.BytesIO(csv_bytes),
                filename = f"leads_{business_type}_{city}.csv".replace(" ", "_"),
                caption  = f"  {len(scored)} leads - ready for outreach",
            )

    except Exception as e:
        await status_msg.edit_text(
            f"  Error: `{str(e)[:200]}`\n\nTry again or check /quota",
            parse_mode=ParseMode.MARKDOWN
        )
    finally:
        _active_jobs[uid] = False


#   /outreach  
async def cmd_outreach(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    args = ctx.args

    if _active_jobs.get(uid):
        await update.message.reply_text(
            "  A job is already running. Check /status for progress."
        )
        return

    # Resolve session_id
    if not args or args[0].lower() == "last":
        session_id = _user_sessions.get(uid)
        if not session_id:
            await update.message.reply_text(
                "  No recent session found. Run `/leads [type] [city]` first.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
    else:
        session_id = args[0]

    # Load leads from CSV
    leads = _load_leads_csv(session_id)
    if not leads:
        await update.message.reply_text(
            f"  No leads found for session `{session_id}`.\n"
            "Run `/leads` first to generate leads.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    _active_jobs[uid] = True
    status_msg = await update.message.reply_text(
        f"  *Starting outreach* for `{session_id}`\n\n"
        f"  Total leads : `{len(leads)}`\n"
        f"  Batch size  : 50 WA + 150 Email\n"
        f"  Schedule    : Batch 1 now -> 7-8hr gap -> Batch 2\n\n"
        f"_I'll update you after each batch._",
        parse_mode=ParseMode.MARKDOWN
    )

    # Run in background - non-blocking
    asyncio.create_task(
        _run_outreach_and_notify(
            leads, session_id, update, status_msg, uid
        )
    )


async def _run_outreach_and_notify(
    leads: list[dict],
    session_id: str,
    update: Update,
    status_msg,
    uid: int,
):
    _reset_daily_if_needed()
    last_progress_update = time.time()

    async def progress_cb(info: dict):
        nonlocal last_progress_update
        # Rate-limit Telegram edits to 1 per 5s (avoid flood limits)
        if time.time() - last_progress_update > 5:
            try:
                await status_msg.edit_text(
                    f"  *Outreach running...*\n\n"
                    f"Batch   : `{info['batch']}`\n"
                    f"Progress: `{info['current']}/{info['total']}`\n"
                    f"  WA   : `{info['wa_sent']}`\n"
                    f"  Email: `{info['email_sent']}`",
                    parse_mode=ParseMode.MARKDOWN
                )
                last_progress_update = time.time()
            except TelegramError:
                pass   # Edit conflicts are non-fatal

    try:
        results = await run_all_batches(leads, session_id, progress_cb)

        wa_sent    = sum(1 for r in results
                         if r.get("channel") == "WhatsApp"
                         and r.get("status")  == "sent")
        email_sent = sum(1 for r in results
                         if r.get("channel") == "Email"
                         and r.get("status")  == "sent")
        skipped    = sum(1 for r in results if r.get("status") == "skipped")

        _daily_stats["wa_sent"]    += wa_sent
        _daily_stats["email_sent"] += email_sent

        await update.message.reply_text(
            f"  *Outreach Complete!*\n\n"
            f"  WhatsApp sent : `{wa_sent}`\n"
            f"  Email sent    : `{email_sent}`\n"
            f"   Skipped       : `{skipped}`\n"
            f"  Session       : `{session_id}`",
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        await update.message.reply_text(
            f"  Outreach failed: `{str(e)[:200]}`",
            parse_mode=ParseMode.MARKDOWN
        )
    finally:
        _active_jobs[uid] = False


#   /import  
async def cmd_import(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Handle /import command.
    User should send a CSV/XLSX file as a document attachment.
    """
    uid = update.effective_user.id
    if _active_jobs.get(uid):
        await update.message.reply_text("  A job is already running. Wait for it to finish.")
        return

    # Check if file was sent as document
    doc = update.message.document
    if not doc:
        await update.message.reply_text(
            "  *How to import your leads:*\n\n"
            "1. Tap the   attachment button\n"
            "2. Choose your file (CSV, XLSX, XLS, or JSON)\n"
            "3. Add caption: `/import` and send\n\n"
            "  *Required columns (any of these names work):*\n"
            "`name` or `company_name` or `business_name`\n"
            "`phone` or `mobile` or `whatsapp`\n"
            "`email` or `email_address`\n"
            "`website` (optional)\n"
            "`address` or `city` (optional)\n\n"
            "After import, use `/outreach session_id` to start sending.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    allowed_ext = (".csv", ".xlsx", ".xls", ".json")
    if not any(doc.file_name.lower().endswith(ext) for ext in allowed_ext):
        await update.message.reply_text(
            f"  Unsupported file type: `{doc.file_name}`\n"
            f"Supported formats: CSV, XLSX, XLS, JSON",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    status_msg = await update.message.reply_text(f"  Reading `{doc.file_name}`...", parse_mode=ParseMode.MARKDOWN)
    _active_jobs[uid] = True

    try:
        # Download file content
        tg_file = await ctx.bot.get_file(doc.file_id)
        content = await tg_file.download_as_bytearray()

        # Parse leads
        from services.fileimporter import import_file
        leads = import_file(doc.file_name, bytes(content))

        if not leads:
            await status_msg.edit_text("  No valid leads found in file. Check column names.")
            return

        # Save to output CSV
        from datetime import datetime
        import csv, os
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        safe_name = "".join(c if c.isalnum() else "_" for c in doc.file_name.split("."))[:30]
        session_id = f"upload_{safe_name}_{timestamp}"
        out_path = os.path.join("output", f"leads_{session_id}.csv")
        os.makedirs("output", exist_ok=True)

        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=leads[0].keys())
            writer.writeheader()
            writer.writerows(leads)

        with_email = sum(1 for l in leads if l.get("email"))
        with_phone = sum(1 for l in leads if l.get("phone"))

        await status_msg.edit_text(
            f"  *{len(leads)} leads imported from `{doc.file_name}`*\n\n"
            f"  With email: {with_email}\n"
            f"  With phone: {with_phone}\n"
            f"  Session: `{session_id}`\n\n"
            f"Start outreach:\n`/outreach {session_id}`",
            parse_mode=ParseMode.MARKDOWN
        )

    except ValueError as e:
        await status_msg.edit_text(f"  Parse error: {str(e)}")
    except Exception as e:
        await status_msg.edit_text(f"  Error: {str(e)[:200]}")
    finally:
        _active_jobs[uid] = False


#   Helpers  
def _load_leads_csv(session_id: str) -> list[dict]:
    results_dir = os.getenv("RESULTS_DIR", "output")
    try:
        for fname in os.listdir(results_dir):
            if session_id in fname and fname.endswith(".csv"):
                with open(os.path.join(results_dir, fname),
                          newline="", encoding="utf-8") as f:
                    return list(csv.DictReader(f))
    except FileNotFoundError:
        pass
    return []


#   Bot builder (used by FastAPI webhook + standalone)  
def build_application() -> Application:
    app = (
        Application.builder()
        .token(TOKEN)
        .build()
    )
    app.add_handler(CommandHandler("start",    cmd_start))
    app.add_handler(CommandHandler("help",     cmd_help))
    app.add_handler(CommandHandler("leads",    cmd_leads))
    app.add_handler(CommandHandler("outreach", cmd_outreach))
    app.add_handler(CommandHandler("status",   cmd_status))
    app.add_handler(CommandHandler("quota",    cmd_quota))
    app.add_handler(MessageHandler(filters.Document.ALL, cmd_import))
    app.add_handler(CommandHandler("import",   cmd_import))
    return app


#   Webhook router for FastAPI  
def get_webhook_router():
    from fastapi import APIRouter, Request, Response

    bot_app   = build_application()
    wh_router = APIRouter(tags=["Telegram"])

    @wh_router.post("/telegram/webhook")
    async def telegram_webhook(request: Request):
        data   = await request.json()
        update = Update.de_json(data, bot_app.bot)
        await bot_app.process_update(update)
        return Response(status_code=200)

    return wh_router, bot_app
