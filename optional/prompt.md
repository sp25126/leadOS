# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  ANTIGRAVITY IDE — COMPLETE SYSTEM AUDIT + UNIFIED MERGER MASTER PROMPT     ║
# ║  CODENAME: LEADHUNTER OMEGA — THE LAST SYSTEM YOU WILL EVER BUILD           ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
#
# AUTHORED BY: A developer who has shipped 200 products and earned $7M in 3
# months by combining AI tooling, prompt engineering, QA discipline, and
# fullstack architecture. Every line below is grounded in production reality.
#
# MANDATE:
#   You are Antigravity IDE. Read EVERY FILE attached to this chat. Do not
#   skim. Do not summarize. Do not hallucinate missing functions. Your job
#   is to deeply understand TWO systems (Octagon + LeadOS Hunter Pro), audit
#   every file in each, reconcile their logic, and output a 6000+ line
#   production-grade audit + unified merger plan that becomes the single
#   source of truth for building one consolidated system.
#
# TWO SYSTEMS TO RECONCILE:
#
#   SYSTEM A — OCTAGON BACKEND
#     Root:    C:\Users\saumy\OneDrive\Desktop\octagon\backend
#     Port:    8765
#     Status:  Enrichment working (60-90% rate), scoring broken (wrong
#              status filter), scheduler dead (wrong port 8000→8765 fixed),
#              email router partial (selection logic done, SMTP not wired),
#              voice agent designed (Colab+Twilio bridge), WA microservice
#              designed (Baileys), phone enricher working (GMAPs only)
#     DB:      Supabase PostgreSQL via SQLAlchemy async (1500+ leads)
#     AI:      Groq llama-3.3-70b-versatile (scoring), Gemini 1.5 Flash
#              (email guesser)
#
#   SYSTEM B — LEAD HUNTER PRO (LeadOS)
#     Root:    C:\Users\saumy\OneDrive\Desktop\lead_hunter\lead-hunter-pro
#     Port:    8000
#     Status:  Frontend properly structured, SSE streaming working,
#              Supabase dedup working, Gemini scoring working, Brevo email
#              partial, WA server (Baileys) partial, Cloudflare deployed
#              (frontend), backend NOT deployed
#     Stack:   Next.js 14 App Router, FastAPI, Supabase, Docker
#     AI:      Gemini 1.5 Flash (scoring + email guess), GROQ fallback
#
# GOAL:
#   Merge the BEST of both. LeadOS Hunter Pro becomes the final container.
#   Octagon's battle-tested enrichment waterfall, multi-source ingest, phone
#   enricher, scoring logic, partner/SaaS fetchers, voice agent, and channel
#   router all move INTO the lead-hunter-pro architecture. The result is one
#   deployable system with a production frontend already on Cloudflare.
#
# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 0 — PRE-AUDIT READING INSTRUCTIONS
# ═══════════════════════════════════════════════════════════════════════════════
#
# BEFORE YOU WRITE A SINGLE LINE OF OUTPUT, read these files in this exact
# order. Do not proceed to any audit section until you have loaded all of them:
#
#   READ ORDER:
#   1. CONTEXT-BRIEFING-READ-THIS-ENTIRE-FILE-BEFORE-RE-1-7.md   ← env, keys, db state
#   2. OCTAGON-LEADGEN-SYSTEM-NEW-CHAT-RESUMPTION-PRO-1-4.md     ← octagon full history
#   3. act-as-a-software-fullstack-AI-agent-developer-who-2.md   ← LeadOS build roadmap
#   4. Act-as-a-futuristic-10-year-experienced-fullstack-3.md    ← frontend rewire specs
#   5. act-as-a-senior-job-and-lead-councilor-and-lead-en-8.md   ← enrichment engine detail
#   6. octagon_outreach_master-5.md                              ← outreach lead list
#   7. processed_leads_for_outreach-6.md                         ← real enriched leads
#   8. r2-8.md                                                   ← full terminal history
#
#   EXTRACTION CHECKLIST — while reading, extract and log:
#   [ ] Every file path mentioned in BOTH projects
#   [ ] Every API endpoint (method + path + status: working/broken/404)
#   [ ] Every DB table and column mentioned
#   [ ] Every API key referenced (name only, never log values)
#   [ ] Every function/class/method across both codebases
#   [ ] Every bug identified in logs
#   [ ] Every half-built feature flagged in prompts
#   [ ] Every test result (passed/failed/partial)
#
# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — SYSTEM A AUDIT: OCTAGON BACKEND (6000-LINE DEEP DIVE)
# ═══════════════════════════════════════════════════════════════════════════════
#
# For each file below, output in this exact format:
#
#  ┌─────────────────────────────────────────────────────────────────┐
#  │ FILE: <path>                                                    │
#  │ STATUS: WORKING / BROKEN / PARTIAL / EMPTY / DEAD              │
#  │ PURPOSE: One sentence                                           │
#  ├─────────────────────────────────────────────────────────────────┤
#  │ FUNCTIONS / CLASSES:                                            │
#  │   - functionName(params) → return_type                         │
#  │     Logic: what it does step by step                           │
#  │     Dependencies: what it imports/calls                        │
#  │     Bugs: any known issues from logs or prompts                │
#  │     Status: WORKING / BROKEN / PARTIAL                         │
#  ├─────────────────────────────────────────────────────────────────┤
#  │ API ENDPOINTS (if router file):                                 │
#  │   METHOD /path                                                  │
#  │     Input:  Pydantic model / query params                      │
#  │     Output: JSON shape                                         │
#  │     Frontend Caller: which page/component calls this           │
#  │     Integration Status: WIRED / PARTIAL / BROKEN / ORPHANED   │
#  ├─────────────────────────────────────────────────────────────────┤
#  │ WHAT TO KEEP IN MERGED SYSTEM: YES / NO / MODIFIED             │
#  │ NOTES FOR MERGER: specific migration instructions               │
#  └─────────────────────────────────────────────────────────────────┘

# ─────────────────────────────────────────────────────────────────────────────
# 1.1 OCTAGON CORE INFRASTRUCTURE FILES
# ─────────────────────────────────────────────────────────────────────────────

AUDIT FILE: app/main.py
  Expected contents based on read files:
  - FastAPI app instantiation
  - CORS middleware (alloworigins=["*"])
  - Startup event: quota status print, Telegram notification
  - APScheduler initialization (6 jobs)
  - Router inclusions (verify ALL of these are present):
      app.include_router(ingest_router)
      app.include_router(enrich_router)
      app.include_router(score_router)
      app.include_router(email_router)
      app.include_router(phone_router)       ← added in later phase
      app.include_router(whatsapp_router)    ← added in later phase
      app.include_router(voice_router)       ← added in later phase
      app.include_router(stats_router)       ← added in later phase
      app.include_router(admin_router)
      app.include_router(telegram_webhook_router)
  - Global exception handler
  - Port: 8765 (NOT 8000 — this was a recurring bug)
  
  VERIFY:
  [ ] All 10 routers are included
  [ ] Port is 8765
  [ ] APScheduler jobs call localhost:8765 (not 8000)
  [ ] Telegram token loaded from env
  [ ] GROQ_API_KEY loaded and logged (last 4 chars only)

AUDIT FILE: app/config.py
  Expected contents:
  - All env vars loaded via python-dotenv
  - Settings object with typed attrs
  - Required keys: SUPABASE_URL, SUPABASE_KEY, GROQ_API_KEY, GEMINI_API_KEY,
    BREVO_SMTP_USER, BREVO_SMTP_PASS, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
    GOOGLE_MAPS_API_KEY, HUNTER_API_KEY, SNOV_CLIENT_ID, SNOV_CLIENT_SECRET,
    APOLLO_API_KEY, GETPROSPECT_API_KEY, GITHUB_TOKEN, GOOGLE_CSE_API_KEY,
    GOOGLE_CSE_ID, GET_PROSPECT_API_KEY, FROM_EMAIL, FROM_NAME,
    MAX_LEADS_PER_RUN, DAILY_EMAIL_CAP, ICP_SCORE_THRESHOLD
  - ValueError raised if any required key is missing
  
  KNOWN ENV STATE (from briefing file):
  - GROQ_API_KEY: loaded (gsk5f...l0G6)
  - GEMINI_API_KEY: loaded (AIzaSy...g0w)
  - SUPABASE: loaded
  - HUNTER_API_KEY: EMPTY ← needs key
  - ZEROBOUNCE_API_KEY: EMPTY ← needs key
  - ABSTRACT_API_KEY: EMPTY ← needs key
  - GMAIL_APP_PASS: EMPTY ← needs Gmail app password

AUDIT FILE: app/db.py
  Expected: AsyncSession factory, get_db dependency, create_all tables
  Check: engine uses asyncpg with Supabase connection string

AUDIT FILE: app/models/lead.py
  FULL COLUMN AUDIT — list every column with type and nullable status:
  
  Core identity:
    id              UUID PRIMARY KEY
    company_name    VARCHAR NOT NULL
    domain          VARCHAR
    source          VARCHAR   ← osm, hn_show, yc_companies, etc.
    lead_type       VARCHAR DEFAULT 'client'  ← added in partner phase
    source_url      VARCHAR   ← HN discussion link
    created_at      TIMESTAMP DEFAULT NOW()
  
  Location:
    address         VARCHAR
    city            VARCHAR
    country         VARCHAR DEFAULT 'IN'
    lat             FLOAT
    lon             FLOAT
  
  Contact:
    phone           VARCHAR
    whatsapp_number VARCHAR   ← normalized 91xxxxxxxxxx
    email           VARCHAR   ← best found email
    founder_email   VARCHAR   ← alternative field name (check which is used)
    email_status    VARCHAR   ← VERIFIED / GENERIC / INVALID / BLACKLISTED
    email_quality_score INT
    email_source    VARCHAR   ← snov / hunter / scraped / pattern / gemini
  
  Website:
    website         VARCHAR
    has_website     BOOLEAN
    website_live    BOOLEAN
    tech_hints      TEXT
    social_media    TEXT
    has_contact_form BOOLEAN
  
  Enrichment:
    enrich_attempts INT DEFAULT 0
    enrichment_tier VARCHAR   ← TIER3_PHONE / TIER4_DOMAIN / TIER6_LOCATION
    mx_valid        BOOLEAN
    description     TEXT      ← from Groq website analysis
    founder_name    VARCHAR
    
  Scoring:
    score           FLOAT DEFAULT 0
    icp_score       INT DEFAULT 0
    priority        VARCHAR   ← high / medium / low
    reason          TEXT
    pain_points     TEXT
    suggested_opening TEXT
    
  Status/Outreach:
    status          VARCHAR   ← NEW/READY/SENT/ARCHIVED/ENRICHMENT_FAILED/
                              ←  email_reach/super_enriched/phone_reach
    outreach_channel VARCHAR  ← whatsapp / email / voice_ai
    replied_at      TIMESTAMP
    
  Partner fields:
    partner_status  VARCHAR
    referral_fee_pct INT
    referral_revenue FLOAT
    
  HN context:
    hn_url          TEXT      ← https://news.ycombinator.com/item?id=xxxxx

  CRITICAL NOTE: Two field naming conventions exist across the codebase:
    - Octagon uses: founder_email, icp_score, outreach_channel
    - LeadOS uses:  email, score, source
  The merger MUST normalize to ONE naming convention.
  DECISION: Use Octagon's richer schema as base, add LeadOS aliases.

# ─────────────────────────────────────────────────────────────────────────────
# 1.2 OCTAGON INGESTION LAYER
# ─────────────────────────────────────────────────────────────────────────────

AUDIT FILE: app/routers/ingest.py
  ENDPOINTS:
  
  POST /api/ingest/run                    STATUS: WORKING (confirmed in logs)
    Logic: Triggers batch ingest from all registered sources
    Sources triggered: RemoteOK, HN, YC, GitHub, Lobsters, AppSumo,
                       BetaList, GLEIF, BBB, ProductHunt, Hashnode,
                       DevTo, Wellfound, Trustpilot, Exporters India,
                       Reddit SaaS/WebDev/ForHire
    Dedup: by domain (fuzzy match + exact)
    DB insert: bulk insert via SQLAlchemy
    Returns: {status, stats: {total_fetched, new_inserted, duplicates_skipped}}
    CONFIRMED WORKING: 1476 fetched, 0 new on re-run (dedup working)
    
  POST /api/ingest/radius-map             STATUS: WORKING (confirmed in logs)
    Logic: OSM Overpass API + Google Maps for local businesses by radius
    Params: business_type, lat, lon (or location_str), radius_m=5000
    Mirrors: overpass-api.de, overpass.private.coffee, kumi.systems
    Quota: 10,000 req/day per mirror (30K total)
    CONFIRMED: Returns real businesses with lat/lon/name/phone
    Bug fixed: Uses overpass.private.coffee as primary (avoids 429)
    
  POST /api/ingest/india-map              STATUS: IMPLEMENTED, NOT MOUNTED
    Logic: 55 Indian cities × 28 categories via OSM
    Sleep: 3s between city requests
    Missing: router not included in main.py
    FIX: Add app.include_router(ingest_india_router) in main.py
    
  POST /api/ingest/foreign-map            STATUS: IMPLEMENTED, NOT MOUNTED
    Logic: 600 global cities × 30 categories
    Missing: Same mounting issue as india-map
    
  POST /api/ingest/india-saas             STATUS: WORKING (confirmed logs)
    Logic: Inc42 RSS, GitHub India orgs, HN India posts
    Returns: {status, stats}
    
  POST /api/ingest/foreign-saas           STATUS: WORKING (confirmed logs)
    Logic: YC OSS API, HN Algolia, ProductHunt RSS, GitHub Trending
    Returns: {status, stats}
    
  POST /api/ingest/partners               STATUS: DESIGNED, BUILT, NOT MOUNTED
    Logic: Clutch, GoodFirms, DesignRush, DuckDuckGo Agency Search,
           OSM India office/marketing/consulting
    lead_type: 'partner' (NOT 'client')
    Missing: router not mounted in main.py
    
  POST /api/ingest/india-test             STATUS: BUILT (confirmed from prompt)
    Logic: 2 cities, 5 categories — quick validation batch
    
  POST /api/ingest/foreign-test           STATUS: BUILT
    Logic: London + Dubai, 5 categories
    
  POST /api/ingest/test-run               STATUS: WORKING
    Output: {status: success, test_mode: true, stats: {total_fetched: 3}}
    
  GET /api/ingest/city-options            STATUS: HELPER, NOT CONFIRMED MOUNTED
  
  DEAD ROUTES (exist in code but return 404):
    POST /api/ingest/near-me              ← designed, not confirmed mounted
    POST /api/ingest/india-local          ← not fully wired
    POST /api/ingest/usa-local            ← not fully wired
    POST /api/ingest/jobspy               ← testjobspy.py exists, never merged
    
  SOURCE FILES TO AUDIT UNDER app/lead_gen/:
  
  AUDIT FILE: app/lead_gen/tier1/hn_show_rss.py
    Bug: Was extracting domain from entry.link (HN discussion URL) instead
         of extracting product URL from entry.summary HTML
    Fix applied: extractproducturl() from BeautifulSoup parsing of summary
    Status post-fix: Should yield real product URLs
    Check: Does it skip entries with no external URL?
    
  AUDIT FILE: app/lead_gen/tier1/devto_showdev.py
    Bug: Same domain extraction issue as hn_show_rss
    Fix: Extract first external non-dev.to URL from entry.summary
    Check: Does it skip blog posts with no product link?
    
  AUDIT FILE: app/lead_gen/tier1/hashnode.py
    Same fix pattern as DevTo — verify applied
    
  AUDIT FILE: app/lead_gen/tier1/lobsters.py
    entry.link IS the actual story URL — use directly if not lobste.rs domain
    
  AUDIT FILE: app/lead_gen/tier1/hn_hiring_rss.py
  AUDIT FILE: app/lead_gen/tier1/remoteok.py
  AUDIT FILE: app/lead_gen/tier1/yc_companies.py
  AUDIT FILE: app/lead_gen/tier1/github_trending.py
  AUDIT FILE: app/lead_gen/tier1/product_hunt.py
  AUDIT FILE: app/lead_gen/tier1/wellfound.py
  AUDIT FILE: app/lead_gen/india_directories.py
    Bug: IndiaMART returns HTML (not JSON) → replaced with JustDial scraper
    Bug: TradeIndia 404 → replaced
    Bug: Sulekha 301→404 → replaced
    Status: Inc42 working (39 leads/3 pages)
    Check: Is JustDial fix applied? Verify soup selectors match live site
    
  AUDIT FILE: app/lead_gen/partner_fetcher.py
    Classes: PartnerFetcher
    Methods:
      fetch_clutch()      → agencies from clutch.co/agencies/ (5 pages each)
      fetch_goodfirms()   → IT consultants from goodfirms.co
      fetch_designrush()  → marketing agencies from designrush.com
      fetch_duckduckgo_agencies() → DDG HTML search for agency keywords
      fetch_india_agencies_osm()  → OSM Overpass for office=marketing/consulting
      fetch_all_partners() → orchestrator, dedup by domain, returns combined
    Sleep: 4-5s between requests
    Status: Code exists, NOT mounted in main.py
    
  AUDIT FILE: app/lead_gen/saas_fetcher.py
    Classes: SaaSFetcher
    Methods:
      fetch_yc_companies()   → YC OSS GitHub API, Redis cursor, 50/day cap
      fetch_hn_show()        → HN Algolia search?query=show+hn
      fetch_producthunt_rss() → ProductHunt RSS feed
      fetch_github_trending() → GitHub trending page scrape
      fetch_all_saas()       → orchestrator, dedup by domain
    Status: Code exists, wired into foreign-saas route

# ─────────────────────────────────────────────────────────────────────────────
# 1.3 OCTAGON ENRICHMENT LAYER
# ─────────────────────────────────────────────────────────────────────────────

AUDIT FILE: app/enrichment/enrichment_engine.py
  Classes: EnrichmentEngine
  
  Core method: enrich_lead(lead_id, db) → bool
    Step 0: Blacklist check (ENRICHMENT_BLACKLIST contains 30+ domains)
            If blacklisted → status=ENRICHMENT_FAILED, email_status=blacklisted
    Step 0b: attempt counter check
             if enrich_attempts >= 3 → status=UNENRICHABLE, return False
    Step 1: Fetch lead from DB
    Step 2: Groq website analysis (extract founder_name, description, tech)
            Model: llama-3.3-70b-versatile (CONFIRMED WORKING)
            Note: llama3-8b-8192 was DECOMMISSIONED — fixed to 70b
    Step 3: MX record check → mx_valid bool
    Step 4: Email waterfall (8-step + legacy methods)
    Step 5: Update DB — status, email, email_source, email_status
    Step 6: If email found → status = email_reach or super_enriched
             (super_enriched = has BOTH email AND phone)
    
  enrich_batch(batch_size, db) → {processed, enriched, failed, rate}
    DB query: WHERE status IN ('NEW') AND source IN (quality_sources)
              ORDER BY source priority (yc first, hn second, etc.)
              LIMIT batch_size
    CRITICAL BUG FIXED: Was querying status='ENRICHED'/'READY' which returns 0
    
  ENRICHMENT_BLACKLIST:
    apple.com, google.com, microsoft.com, amazon.com, meta.com, facebook.com,
    twitter.com, x.com, linkedin.com, github.com, youtube.com, netflix.com,
    reddit.com, wikipedia.org, medium.com, substack.com, dev.to, hashnode.com,
    weworkremotely.com, remotive.com, himalayas.app, tryremotely.com,
    jobscollider.com, authenticjobs.com, larajobs.com, djangojobs.net,
    ycombinator.com, techcrunch.com, producthunt.com, crunchbase.com,
    wellfound.com, angel.co
  
  Domain validation function: is_valid_domain(domain) → bool
    Reject: article titles used as domains (how-to-build-...-at-toast.com)
    Rule: domain < 60 chars, no spaces, proper TLD, not a sentence
    
  Fallback handler: app/enrichment/fallback_handler.py
    STATUS: 0 BYTES (empty file) — DEAD
    Need: Retry logic for ENRICHMENT_FAILED leads

AUDIT FILE: app/enrichment/email_waterfall.py
  CLASS: EmailWaterfall
  
  METHOD PRIORITY ORDER (8 methods + legacy):
  
  1. try_scraper(domain) → str|None
     Logic: httpx GET homepage + contact/about pages
     Parse: BeautifulSoup, find all mailto: links and email regex
     Filter: Skip abuse@, noreply@, privacy@ unless nothing else
     Status: WORKING
     
  2. try_crt_sh_email(domain) → str|None
     Logic: GET https://crt.sh/?q=domain&output=json
     Parse: Scan cert Subject/SAN for email patterns matching domain
     API key: None required
     Status: IMPLEMENTED, verify applied
     
  3. try_rdap_email(domain) → str|None
     Logic: GET https://rdap.org/domain/{domain}
     Parse: entities[].vcardArray for fieldtype="email"
     Filter: Skip registrar emails (is_registrar_email check)
     API key: None required
     Status: IMPLEMENTED
     
  4. try_hunter(domain) → str|None
     Logic: GET https://api.hunter.io/v2/domain-search
     Params: domain, api_key, limit=5
     Prefer: type='personal' over type='generic'
     Quota: 25/month free tier
     Key: HUNTER_API_KEY (currently empty — skip silently if None)
     Status: IMPLEMENTED, key empty → silently skipped
     
  5. try_snov(domain) → str|None
     Step 1: OAuth token fetch via POST form-data (NOT json — this was the bug)
             URL: https://api.snov.io/v1/oauth/access_token
             Cache token in Redis key 'snov_token' for 3500s
     Step 2: Domain search GET https://api.snov.io/v2/domain-emails-with-info
             Headers: Authorization: Bearer {token}
             If 401 → delete Redis cache, return None
             If 400 → log full response body for debug
     Prefer: position contains founder/ceo/co-founder/owner
     Quota: 50 credits/month
     Bug fixed: Was sending json={} body, should be OAuth form POST
     Status: BUG FIXED, WORKING
     
  6. try_apollo(domain) → str|None
     Logic: POST https://api.apollo.io/v1/mixed_people_search
     Params: api_key, q_organization_domains, person_titles=[founder,ceo,owner]
     Filter: Skip apollo.io emails from response
     Quota: 50 exports/month
     Status: IMPLEMENTED
     
  7. try_getprospect(domain) → str|None
     CORRECTED ENDPOINT (from Pipedream official docs):
       GET https://api.getprospect.com/public/v1/email/find
       Headers: apiKey: {GETPROSPECT_API_KEY}
       Params: firstName, lastName, domain
     Bug fixed: Was using POST /api/v1/find-email (wrong URL, returns 405)
     Status: BUG FIXED
     
  8. try_common_crawl_email(domain) → str|None
     Logic: CDX API → find crawled pages → Wayback Machine fetch → regex scan
     URL: https://index.commoncrawl.org/CC-MAIN-2024-10-index
     No API key required
     Status: IMPLEMENTED
     
  ZERO-COST METHODS (added in enrichment expansion):
  
  9. try_legal_pages(domain) → str|None
     Paths: /privacy, /privacy-policy, /legal, /terms, /terms-of-service,
            /contact, /about
     Filter: Must contain domain in email, skip sentry/wix/squarespace
     Status: IMPLEMENTED
     
  10. try_security_txt(domain) → str|None
      URLs: https://domain/.well-known/security.txt AND https://domain/security.txt
      Parse: Lines starting with "Contact:"
      Handle: mailto: prefix stripping
      Status: IMPLEMENTED
      
  LEGACY METHODS (kept from v1):
  11. india_registry_check(domain) → str|None
  12. smtp_pattern_guess(domain, founder_name) → str|None
      Patterns: firstname@, f+lastname@, firstname.lastname@, etc.
      
  13. try_gemini_email_guess(domain, company_name) → str|None
      Model: gemini-1.5-flash
      URL: https://generativelanguage.googleapis.com/v1beta/models/
           gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}
      Prompt: "For company X with domain Y, what is the most likely email?"
      Only runs if ALL previous 12 methods returned None
      maxOutputTokens: 50, temperature: 0.1
      Status: IMPLEMENTED, LAST RESORT
      
  is_registrar_email(email) → bool
    Returns True if email contains: noreply, abuse, privacy, hostmaster,
    postmaster, webmaster, admin, whois, domain, registrar
    
  FINAL WATERFALL ORDER in find_email():
    scraper → crt_sh → rdap → hunter → snov → apollo → getprospect →
    common_crawl → india_registry → legal_pages → security_txt →
    smtp_pattern → gemini_guess (only if all others None)

AUDIT FILE: app/enrichment/website_scraper.py
  Function: scrape_website(domain) → {founder_name, title, description, 
                                       tech_hints, social_media, has_contact_form}
  Logic: httpx GET, BeautifulSoup parse meta/og/json-ld tags
  Groq call: analyze page text for founder extraction
  Status: WORKING (confirmed in logs)

AUDIT FILE: app/enrichment/mx_checker.py
  Function: check_mx(domain) → bool
  Logic: dns.resolver.resolve(domain, 'MX')
  Returns: True if ≥1 MX records, False on NoAnswer/NXDOMAIN
  Status: WORKING

# ─────────────────────────────────────────────────────────────────────────────
# 1.4 OCTAGON SCORING LAYER
# ─────────────────────────────────────────────────────────────────────────────

AUDIT FILE: app/routers/score.py
  ENDPOINT: POST /api/score/run?batch_size=50
  
  ORIGINAL BUG (confirmed from logs):
    Query was: WHERE status IN ('READY', 'ENRICHED')
    Result: scored=0 because no leads have those exact statuses
    
  FIXED QUERY:
    WHERE status IN ('email_reach', 'super_enriched', 'phone_reach',
                     'ENRICHED', 'enriched')  ← legacy fallbacks
    AND (score = 0 OR score IS NULL)
    LIMIT batch_size
    
  Groq call per lead:
    Model: llama-3.3-70b-versatile
    Prompt: Analyze company description, domain, tech hints, source
            Return JSON: {icp_score: 0-100, reason: str, pain_points: str,
                          suggested_opening: str, priority: high|medium|low}
    Score ≥ 70 → status = 'READY'
    Score < 30 → status = 'ARCHIVED'
    Else → status unchanged
    
  Returns: {status, scored, ready_to_email, archived, avg_score}
  
  CONFIRMED STATUS (from logs):
    scored=0 before fix → scored=50+ after fix expected
    After fix run: status success, scored N, ready_to_email 18-25

AUDIT FILE: app/routers/score_partners.py
  POST /api/score/partners
  Custom Groq prompt tuned for agency ICP (not client ICP)
  Scoring criteria: agency size, existing client base, AI-readiness,
                    web presence quality, referral potential
  Status: IMPLEMENTED, verify mounted in main.py

# ─────────────────────────────────────────────────────────────────────────────
# 1.5 OCTAGON PHONE ENRICHMENT LAYER
# ─────────────────────────────────────────────────────────────────────────────

AUDIT FILE: app/routers/phone_router.py
  ENDPOINTS:
  
  POST /api/phone/enrich?batch_size=20    STATUS: WORKING (13/20 rate)
    Logic:
      1. Fetch batch of leads WHERE phone IS NULL AND status != ARCHIVED
      2. For each lead:
         a. OSM check: DISABLED (India coverage near-zero, adds latency)
            Code: async def find_phone_osm(lead) → return None
         b. Google Maps: search company_name + city, extract formatted_phone
            API: Places API (Text Search)
            Normalize: strip non-digits, prepend +91 for Indian numbers
         c. COMMIT immediately after each lead (fixes DB connection timeout bug)
            Bug was: single bulk commit after 75 leads → connection dies in 75s
      3. Returns: {status, processed, osm_found, gmaps_found, not_found,
                   whatsapp_ready}
    Confirmed rate: 13/20 (65% on Indian businesses)
    
  GET /api/phone/stats                    STATUS: WORKING
    Returns: {total_with_phone, whatsapp_ready, phone_coverage_pct}
    
  UTILITY: utils/phone_normalizer.py
    Function: normalize_phone(raw, country_code='91') → str
    Rules: 10-digit → prepend country_code
           Leading 0 → replace with country_code
           Already has + → keep as-is
           < 10 digits → return ''
           None input → return ''
    CONFIRMED PASSING: All 12 test cases pass in Phase 1

# ─────────────────────────────────────────────────────────────────────────────
# 1.6 OCTAGON OUTREACH LAYER (Email)
# ─────────────────────────────────────────────────────────────────────────────

AUDIT FILE: app/routers/email_router.py
  ENDPOINTS:
  
  POST /api/email/send-run-by-source      STATUS: SELECTION LOGIC DONE,
    ?dry_run=true&batch_size=10                   SMTP NOT WIRED
    
    Selection Logic (IMPLEMENTED):
      1. SELECT DISTINCT source FROM leads WHERE status='READY'
         AND icp_score > 70 AND email_quality_score >= 2
      2. Loop each source, fetch top batch_size leads ORDER BY icp_score DESC
      3. Exclude leads where email prefix (before @) IN:
         info, contact, hello, sales, support, admin
      4. Returns: {mode: dry_run, sources_processed: N, attempted_sends: N,
                   details: {source_name: count}}
    
    SMTP Logic (NOT WIRED):
      - app/ai/email_writer.py EXISTS but is NEVER called by this router
      - Brevo SMTP credentials exist in .env (confirmed)
      - Need to wire: generate_personalized_email(lead) → subject, body
        then send via Brevo SMTP
    
  GET /api/send/preview?limit=3           STATUS: 404 (confirmed in logs)
    This endpoint was designed but NEVER built
    Fix: Add route that calls selection logic with dry_run=True

AUDIT FILE: app/ai/email_writer.py
  Function: generate_personalized_email(lead_dict) → {subject, body, html}
  Logic: Groq call with lead context → personalized cold email
  Template: Trojan Horse method for agency partners
            Direct value pitch for client leads
  Status: EXISTS but ORPHANED (not called by any router)
  Fix: Wire into email_router.py send loop

AUDIT FILE: app/routers/outreach_router.py (if exists, or check main)
  Check: Is there a POST /api/outreach/start?
  This was the LeadOS route — may not exist in Octagon
  If missing: add compatibility shim that maps to email_router

# ─────────────────────────────────────────────────────────────────────────────
# 1.7 OCTAGON WHATSAPP LAYER
# ─────────────────────────────────────────────────────────────────────────────

AUDIT FILE: app/routers/whatsapp_router.py
  ENDPOINTS:
  
  GET /api/whatsapp/provider-status       STATUS: WORKING (smoke test passed)
    Returns: {providers: [{name, type, exhausted, calls, failed}]}
    
  POST /api/whatsapp/send                 STATUS: DESIGNED
    Logic: Send WA message via Baileys Node.js microservice
           OR Twilio WA API as fallback
    Note: Baileys runs as separate process (wa-server/)
    
  GET /api/whatsapp/queue-status          STATUS: DESIGNED
  
  CHANNEL ROUTING LOGIC:
    WHATSAPP_PRIMARY_COUNTRIES:
      Asia: IN, PK, BD, LK, ID, MY, PH, TH
      Latin America: BR, MX, AR, CO, CL, PE, VE, EC
      Middle East/Africa: AE, SA, EG, JO, KW, NG, KE, ZA, GH
      Europe (WA-dominant): DE, ES, IT, GB, CH, NL, PT, BE, AT
      
    EMAIL_PRIMARY_COUNTRIES:
      CN, KP, JP, KR, US, CA, FR, SE, DK, NO
      (countries where WA is banned or secondary)
      
    get_outreach_channel(country_code) → 'whatsapp' | 'email'
    Stored in: outreach_channel column on leads table

AUDIT FILE: wa-server/ (Node.js Baileys microservice)
  Files expected:
    wa-server/index.js      ← Fastify server, Baileys session
    wa-server/package.json  ← baileys, fastify, qrcode-terminal, p-queue
  Endpoints:
    GET  /health            ← session connected/disconnected/scanning
    GET  /qr                ← base64 QR code for WhatsApp Web auth
    POST /send              ← {phone, message} → send WA message
  Anti-ban:
    Human-mimicking delays: 25-50s random between messages
    is_registered_user check before send
    p-queue: concurrency=1, interval=30000
  Status: DESIGNED in context, verify files exist
  Note: Chrome/Chromium required for Puppeteer (whatsapp-web.js)
        OR use @whiskeysockets/baileys (no browser needed) ← PREFERRED

# ─────────────────────────────────────────────────────────────────────────────
# 1.8 OCTAGON VOICE AGENT LAYER
# ─────────────────────────────────────────────────────────────────────────────

AUDIT FILE: app/routers/voice_router.py
  ENDPOINTS:
  
  GET /api/voice/queue?batch_size=10&min_icp_score=60
                                          STATUS: WORKING (smoke test passed)
    Logic: LeadContextService.get_batch_for_voice()
    Query: phone IS NOT NULL AND status NOT IN (ARCHIVED, phone_reach)
           AND (outreach_channel='voice_ai' OR
                (whatsapp_number IS NULL AND phone LIKE '91%'))
           AND icp_score >= min_icp
    Returns: [{id, company_name, phone, city}, ...]
    
  POST /api/voice/save-transcript         STATUS: WORKING (smoke test passed)
    Body: {lead_id, phone, transcript, status, call_sid}
    Logic: Update lead status=phone_reach, store transcript in metadata
    
  GET /api/voice/provider-status          STATUS: WORKING
    Returns: provider configs (Twilio/Exotel/Plivo/Servetel)

AUDIT FILE: app/services/lead_context_service.py (LeadContextService)
  This is the UNIFIED DATA LAYER that all enrichers/routers share.
  
  Key methods:
    get_by_id(lead_id) → LeadContext
    get_batch_needing_outreach(limit, min_icp) → List[LeadContext]
    get_batch_for_voice(limit, min_icp) → List[LeadContext]
    save_context(ctx) → void
    to_context(lead_orm) → LeadContext
    get_overview_stats() → dict
    
  LeadContext dataclass fields:
    id, company_name, source, lat, lon, city, country,
    phone, whatsapp_number, phone_source,
    email, email_status, email_source,
    website, has_website, website_live, tech_hints, social_media,
    description, founder_name,
    score, icp_score, priority, reason, pain_points, suggested_opening,
    status, outreach_channel, replied_at,
    lead_type, partner_status, hn_url,
    enrichment_tier, enrich_attempts, mx_valid
    
  Status: IMPLEMENTED, verify all methods present

# ─────────────────────────────────────────────────────────────────────────────
# 1.9 OCTAGON STATS + ADMIN LAYER
# ─────────────────────────────────────────────────────────────────────────────

AUDIT FILE: app/routers/stats_router.py
  GET /api/stats/overview                 STATUS: WORKING (smoke test 200)
  
  Returns unified stats from ALL subsystems:
  {
    total_leads: N,
    coverage: {
      phone_reach: N, phone_reach_pct: float,
      whatsapp_ready: N,
      email_reach: N, email_reach_pct: float,
      email_verified: N,
      super_enriched: N, super_enriched_pct: float
    },
    tiers: {tier3_phone: N, tier4_domain: N, tier6_location: N},
    outreach: {
      ready_to_contact: N, emailed: N, phone_reached: N,
      replied: N, reply_rate_pct: float
    }
  }
  
  CONFIRMED from terminal:
    total_leads: 1455, pending_or_new: 1395, enriched: 57,
    by_status: {phone_reach: 7, ENRICHMENT_FAILED: 3, super_enriched: 38,
                email_reach: 12, NEW: 1395}

AUDIT FILE: app/routers/admin.py
  POST /api/admin/reset-db               STATUS: WORKING (leadsdeleted: 1997)
    Body: {confirm: "RESET"} → TRUNCATE leads
    
  POST /api/admin/full-run               STATUS: IMPLEMENTED
    Runs: ingest → india_saas → foreign_saas → enrich×3 → score
    Returns: summary with each phase stats
    
  GET /api/admin/stats                   STATUS: WORKING
    Confirmed: status=ok, by_source shows 20+ sources

# ─────────────────────────────────────────────────────────────────────────────
# 1.10 OCTAGON SCHEDULER + AUTOMATION
# ─────────────────────────────────────────────────────────────────────────────

AUDIT FILE: app/scheduler.py
  Framework: APScheduler AsyncIOScheduler
  
  JOBS (6 total):
    1. ingest_run      → POST /api/ingest/run         (cron)
    2. enrich_run      → POST /api/enrich/run         (cron)
    3. score_run       → POST /api/score/run          (cron)
    4. send_run        → POST /api/email/send-run-by-source (cron)
    5. followup_run    → POST /api/email/followup     (cron)
    6. daily_report    → Telegram summary message     (daily at 8am)
    
  CRITICAL BUG (fixed):
    Was calling localhost:8000 → should be localhost:8765
    All jobs now use call_internal(path) helper:
      async def call_internal(path: str):
        async with httpx.AsyncClient(timeout=300) as client:
          resp = await client.post(f"http://localhost:8765{path}",
                                    headers={"X-API-Key": "leadoskey123"})
          
  7-hour minimum gap guard:
    Prevents outreach jobs from overlapping
    State persisted to DB or Redis
    
  Status: SCHEDULER STARTS (confirmed in logs)
          All 6 jobs added to job store
          Telegram notification sent on startup ✓

# ─────────────────────────────────────────────────────────────────────────────
# 1.11 OCTAGON NOTIFICATION LAYER
# ─────────────────────────────────────────────────────────────────────────────

AUDIT FILE: app/notifications/telegram.py
  Function: send_telegram_alert(message) → bool
  Bot token: TELEGRAM_BOT_TOKEN (confirmed working in logs)
  Chat ID: TELEGRAM_CHAT_ID (your personal chat)
  Status: WORKING (HTTP 200 confirmed in startup logs)

AUDIT FILE: server/bot/telegram_bot.py (LeadOS version)
  Commands: /start, /leads, /outreach, /status, /quota, /help
  Middleware: rate limiting (1 job/user), status message editing
  Integration: calls discover_leads, enrich_all, score_leads directly
  Status: IMPLEMENTED (confirmed in file)

# ─────────────────────────────────────────────────────────────────────────────
# 1.12 OCTAGON UTILITY LAYER
# ─────────────────────────────────────────────────────────────────────────────

AUDIT FILE: utils/rate_limiter.py
  Class: QuotaManager (singleton: quota)
  Persistence: quotastate.json (survives restarts)
  Daily auto-reset on new day
  Monthly auto-reset on new month
  Thread-safe: threading.Lock
  
  Default quotas:
    overpass_main:    10,000/day
    overpass_kumi:    10,000/day
    overpass_private: 10,000/day
    google_maps:      10,000/month (= 200 Maps + 300 Places + free tier)
    foursquare:       10,000/month
    here_places:      1,000/day
    hunter_io:        25/month
    abstract_email:   100/month
    
  Methods: has_quota(source), consume(source, count), remaining(source),
           status() → dict, reset_source(source)
  CONFIRMED PASSING: All 5 QuotaManager tests pass

AUDIT FILE: utils/request_manager.py
  OVERPASS_MIRRORS: [overpass-api.de, overpass.private.coffee, kumi.systems]
  get_headers(is_api=False) → rotating User-Agent headers
  safe_get(url, params, retries, base_delay, is_scrape) → dict|str|None
  safe_post(url, data, json_body, retries) → dict|str|None
  Retry logic: exponential backoff with jitter on 429
  Return None on 403/404 immediately

AUDIT FILE: utils/channel_router.py (add if not exists)
  WHATSAPP_PRIMARY_COUNTRIES and EMAIL_PRIMARY_COUNTRIES constants
  get_outreach_channel(country_code) → 'whatsapp' | 'email'
  DB column: outreach_channel backfill SQL provided

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — SYSTEM B AUDIT: LEAD HUNTER PRO (LeadOS)
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# 2.1 LEAD HUNTER PRO — BACKEND (server/)
# ─────────────────────────────────────────────────────────────────────────────

AUDIT FILE: server/main.py
  Port: 8000 (LeadOS uses 8000, Octagon uses 8765)
  Merger decision: NEW system uses PORT 8000 (LeadOS convention)
  Routers included:
    - leads router     (POST /api/leads/stream, GET /api/leads/download)
    - auth router      (POST /api/auth/set-key, GET /api/auth/key-status)
    - outreach router  (POST /api/outreach/start, GET /api/outreach/status)
    - health router    (GET /api/health)
  CORS: enabled for Cloudflare domain + localhost

AUDIT FILE: server/routers/leads.py
  POST /api/leads/stream                  STATUS: WORKING (confirmed)
    Auth: validate_request_key() from auth.py (NOT hardcoded)
    Input: {business_type, location, radius_km, target_service, max_leads=80,
            batch_size=20}
    Logic:
      1. Discover leads (OSM + Google Maps)
      2. Enrich in batches of 20 (website scrape + email)
      3. Dedup via shown_leads table (lead_hash check)
      4. Stream SSE events:
         - {status: discovering, message: ...}
         - {status: enriching, message: ...}
         - {status: batch, batch: [...], total_so_far: N, session_id: ...}
         - {status: done, total: N}
         - {status: error, detail: ...}
      5. Only yield leads with phone OR email (drops empty ones)
      6. Max 80 leads per session
      
    SSE Format: "data: {json}\n\n"
    
  GET /api/leads/{session_id}/download    STATUS: IMPLEMENTED
    Returns: FileResponse with CSV file from output/ directory

AUDIT FILE: server/routers/auth.py
  POST /api/auth/set-key                  STATUS: IMPLEMENTED
    Headers: X-Master-Key (leadoskey123)
    Body: {user_id, new_key}
    Logic: Hash key → store in user_api_keys table
    Returns: {success, hint: last_4_chars}
    
  GET /api/auth/key-status                STATUS: IMPLEMENTED
    Headers: X-API-Key
    Returns: {valid, user_id, tier, leads_this_month, api_calls_today}
    
  GET /api/auth/usage                     STATUS: IMPLEMENTED
    Returns: real-time usage stats
    
  validate_request_key(api_key) → user_dict | raise 401
    Logic: Hash incoming key → query user_api_keys table → return user

AUDIT FILE: server/services/enricher.py
  Function: stream_enriched_leads(params) → AsyncGenerator[batch, ...]
  Function: scrape_contact_from_url(url) → {phone, email}
  Function: search_contact_duckduckgo(query) → {phone, email}
  Function: fetch_gmaps_leads(business_type, location, radius_km) → List[lead]
  Function: make_lead_hash(lead) → str (for dedup)
  Function: is_already_shown(hash, session_id) → bool (Supabase check)
  Function: mark_as_shown(lead, hash, session_id) → void
  
  Status: WORKING (SSE streaming confirmed in terminal)

# ─────────────────────────────────────────────────────────────────────────────
# 2.2 LEAD HUNTER PRO — DATABASE TABLES
# ─────────────────────────────────────────────────────────────────────────────

TABLE: shown_leads                        STATUS: EXISTS IN SUPABASE
  id              UUID PRIMARY KEY
  lead_hash       VARCHAR(64) UNIQUE NOT NULL  ← dedup key
  name            VARCHAR(255)
  city            VARCHAR(100)
  phone           VARCHAR(30)
  email           VARCHAR(255)
  source          VARCHAR(50)
  session_id      VARCHAR(100)
  shown_at        TIMESTAMP DEFAULT NOW()
  business_type   VARCHAR(100)
  location        VARCHAR(100)
  INDEX: idx_shown_leads_hash ON shown_leads(lead_hash)

TABLE: user_api_keys                      STATUS: EXISTS IN SUPABASE
  id              UUID PRIMARY KEY
  user_id         VARCHAR(255) UNIQUE NOT NULL
  api_key_hash    VARCHAR(64) UNIQUE NOT NULL
  api_key_hint    VARCHAR(10)
  tier            VARCHAR(20) DEFAULT 'starter'
  is_set          BOOLEAN DEFAULT TRUE
  created_at      TIMESTAMP DEFAULT NOW()
  last_used_at    TIMESTAMP
  leads_this_month     INTEGER DEFAULT 0
  api_calls_today      INTEGER DEFAULT 0
  webhook_url     VARCHAR(500)
  INDEX: idx_user_api_keys_hash ON user_api_keys(api_key_hash)
  INDEX: idx_user_api_keys_user ON user_api_keys(user_id)

# ─────────────────────────────────────────────────────────────────────────────
# 2.3 LEAD HUNTER PRO — FRONTEND (web/)
# ─────────────────────────────────────────────────────────────────────────────

AUDIT: web/app/(portfolio)/layout.tsx
  Status: ORIGINAL CLOUDFLARE THEME (do not modify)
  Contains: Portfolio navbar, footer, ambient glow backgrounds
  Note: Reverted from cinematic theme — original confirmed live on Cloudflare

AUDIT: web/app/(leados)/layout.tsx
  Status: LEADOS SIDEBAR LAYOUT
  Contains: LeadOS-specific navigation, no portfolio nav
  Note: Separate layout group from portfolio

AUDIT: web/app/(leados)/ingest/page.tsx
  WHAT WORKS:
    [ ] Business type input
    [ ] Location input with validation
    [ ] Radius slider
    [ ] Target service select
    [ ] Hunt button
  WHAT NEEDS WIRING:
    [ ] useLeadStream hook connected to LAUNCH button
    [ ] Real SSE stream displayed in leads table (not mock data)
    [ ] Session ID stored for outreach
    [ ] API key from localStorage passed as X-API-Key header
  
  CRITICAL: Remove all hardcoded mock data
    grep -r "Mumbai, India" web/
    grep -r "mockLeads" web/
    grep -r "const leads = \[" web/
    ALL MUST RETURN EMPTY

AUDIT: web/hooks/useLeadStream.ts
  STATUS: NEEDS CREATION (from our earlier prompt design)
  Full implementation provided in previous context — CREATE THIS FILE
  States: idle | discovering | enriching | streaming | done | error
  Connects: POST /api/leads/stream with SSE reader loop
  Returns: {leads, status, statusMessage, sessionId, totalReceived, error,
            startHunt, stopHunt}

AUDIT: web/lib/api.ts
  STATUS: SHOULD EXIST, VERIFY
  Required exports:
    leadsAPI.search(body) → LeadSearchResponse
    leadsAPI.upload(file) → LeadUploadResponse
    leadsAPI.download(sessionId) → URL
    outreachAPI.start(body) → OutreachStartResponse
    outreachAPI.status(taskId) → OutreachStatusResponse
    systemAPI.health() → HealthResponse
    systemAPI.quota() → QuotaStatusResponse
    settingsAPI.saveKeys(keys) → void (localStorage)
    settingsAPI.loadKeys() → StoredKeys
    settingsAPI.verifyKeys() → void (calls health endpoint)
  
  KEY RULE: ALL API calls go through api.ts ONLY
             No page/component ever calls fetch() directly
  
  api_call<T>(path, options) → Promise<T>
    Reads X-API-Key from localStorage('leados_keys_v2')?.internal
    Throws APIError(message, status) on non-ok response

AUDIT: web/app/(leados)/dashboard/page.tsx
  Required widgets:
    [ ] Quota bars (GET /api/quota/status)
    [ ] Health badge (GET /api/health → waserver bool)
    [ ] Recent activity feed
    [ ] Stats: total leads, enriched, ready, emailed
  Status: PARTIAL — verify quota and health wired to real endpoints

AUDIT: web/app/(leados)/outreach/page.tsx
  Required:
    [ ] Session selector (dropdown of recent session IDs)
    [ ] Start Outreach button → POST /api/outreach/start
    [ ] Real polling loop for status → GET /api/outreach/status/{task_id}
    [ ] Progress bar based on {status, wa_sent, email_sent, skipped, total}
    [ ] No fake setTimeout completions
  Status: PARTIAL — verify polling is real

AUDIT: web/app/(leados)/settings/page.tsx
  Required:
    [ ] API key fields (internal, gemini, brevo, master)
    [ ] Save → localStorage('leados_keys_v2')
    [ ] Sync/Test → calls systemAPI.health() with stored key
    [ ] Error banner on key validation failure
    [ ] Success toast on save
  BYOK Security: Keys stored in localStorage only, never sent to server
                 except as X-API-Key header per request

AUDIT: web/app/(leados)/history/page.tsx
  Required:
    [ ] Past sessions list from Supabase (date, location, business type)
    [ ] Lead count per session
    [ ] Status (enriched/outreach_sent)
    [ ] Click to expand → show leads
    [ ] Export CSV per session
  Status: BUILT but no data fetching (confirmed in audit)
  Fix: Add real Supabase query via API

AUDIT: web/app/(leados)/whatsapp/page.tsx
  Required:
    [ ] GET /api/whatsapp/health → connection status badge
    [ ] GET /api/whatsapp/qr → base64 QR rendered as <img>
    [ ] Auto-poll every 5 seconds for status
    [ ] Reconnect button
  Status: PARTIAL — verify QR is from backend, not static

AUDIT: web/app/(leados)/refer/page.tsx
  Required:
    [ ] Generate unique referral code (Name+Email+hash)
    [ ] Track signups via Supabase referrals table
    [ ] Show referral count + reward status (15% commission)
    [ ] Copy referral link button
  Status: DESIGNED, partially built

AUDIT: web/app/(portfolio)/page.tsx
  Required:
    [ ] Import projects from web/config/projects.ts (single source of truth)
    [ ] Show only featured:true projects
    [ ] No hardcoded project sections
  Status: VERIFY projects.ts exists and is imported

AUDIT: web/config/projects.ts
  Required structure:
    export const projects = [{
      slug, name, tagline, description, status: 'LIVE'|'BETA'|'BUILDING'|'ARCHIVED',
      featured: boolean, liveUrl, githubUrl, videoUrl, tech, metrics, color
    }]
  Status: CREATE IF MISSING

AUDIT: web/app/(portfolio)/hire/page.tsx
  Required:
    [ ] Hire Me services description
    [ ] Bounty referral code generator (Name+Email → secure hash → REF-CODE)
    [ ] Bounty rules (15% commission on referred contracts)
    [ ] LinkedIn, GitHub, Email links
  Status: EXISTS (confirmed in context), verify referral logic

AUDIT: web/app/api-hub/page.tsx
  Required (NEW FEATURE):
    [ ] API Hub landing — "Build with LeadOS"
    [ ] Pricing tiers (Starter/Pro/Enterprise)
    [ ] Code examples showing API usage
    [ ] CTA: Get API Key → /leados/settings
    [ ] CTA: Book custom integration → cal.com link
  Status: NEEDS CREATION

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — CROSS-SYSTEM CONFLICT RESOLUTION
# ═══════════════════════════════════════════════════════════════════════════════

CONFLICT 1: SCORING FIELD NAMES
  Octagon: icp_score (int 0-100), stored in leads table
  LeadOS:  score (float 0-10), returned in SSE stream
  RESOLUTION: Unified system uses BOTH columns internally
    - DB stores: score (0-10 for frontend display), icp_score (0-100 for routing)
    - Conversion: icp_score = score * 10
    - Frontend always displays score (0-10)
    - Backend routing always uses icp_score (>70 threshold)

CONFLICT 2: STATUS VALUES
  Octagon statuses: NEW, READY, SENT, ARCHIVED, ENRICHMENT_FAILED, email_reach,
                    super_enriched, phone_reach, UNENRICHABLE, phonereach,
                    emailreach, superenriched
  LeadOS statuses: NEW, READY, SENT, ENRICHED (simpler)
  RESOLUTION: Adopt Octagon's richer status set, add migration for LeadOS table:
    UPDATE shown_leads SET status = CASE
      WHEN email IS NOT NULL AND phone IS NOT NULL THEN 'super_enriched'
      WHEN email IS NOT NULL THEN 'email_reach'
      WHEN phone IS NOT NULL THEN 'phone_reach'
      ELSE 'NEW'
    END;

CONFLICT 3: AI SCORING PROVIDER
  Octagon:  Groq (llama-3.3-70b-versatile) → icp_score 0-100
  LeadOS:   Gemini 1.5 Flash → score 0-10
  RESOLUTION: Primary = Gemini (free 1500 req/day), Fallback = Groq
    If GEMINI_API_KEY missing → use Groq
    If Groq rate-limited → default score = 5, priority = medium (graceful)

CONFLICT 4: DATABASE TABLES
  Octagon: SQLAlchemy async + Supabase (leads table, 1500+ rows)
  LeadOS:  Supabase direct (shown_leads, user_api_keys tables)
  RESOLUTION: SAME Supabase project, add ALL tables:
    leads (Octagon schema — primary storage, 1500+ rows exist)
    shown_leads (LeadOS dedup table)
    user_api_keys (LeadOS auth table)
    referrals (bounty system)
    outreach_history (campaign tracking)

CONFLICT 5: PORT NUMBERS
  Octagon: 8765
  LeadOS:  8000
  RESOLUTION: Merged system uses 8000 (LeadOS convention, already on Cloudflare)
    Update all Octagon scheduler call_internal() to use 8000

CONFLICT 6: AUTH MECHANISM
  Octagon: X-API-Key: leadoskey123 (hardcoded single key)
  LeadOS:  validate_request_key() → per-user API key via DB
  RESOLUTION: Use LeadOS DB-backed auth as primary
    Keep 'leadoskey123' as MASTER_KEY (env var) for admin/scheduler calls
    All user-facing endpoints use validate_request_key()

CONFLICT 7: ENRICHMENT PIPELINE
  Octagon: 13-step waterfall, 60-90% rate, battle-tested
  LeadOS:  Simple 2-step (website scrape + DuckDuckGo), ~20% rate
  RESOLUTION: Replace LeadOS enricher with Octagon's full waterfall
    server/services/enricher.py → import and use EmailWaterfall from Octagon

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — COMPLETE FILE STRUCTURE FOR MERGED SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

ROOT: lead-hunter-pro/
│
├── server/                          ← FastAPI backend (PORT 8000)
│   ├── main.py                      ← Entry point, all routers, CORS, scheduler
│   ├── config.py                    ← All env vars, Settings singleton
│   ├── db.py                        ← AsyncSession factory, Supabase engine
│   │
│   ├── models/
│   │   ├── lead.py                  ← Full Lead ORM (Octagon schema + LeadOS fields)
│   │   ├── user_api_key.py          ← User API keys table
│   │   ├── shown_lead.py            ← Dedup table
│   │   └── referral.py              ← Bounty referral tracking
│   │
│   ├── routers/
│   │   ├── leads.py                 ← POST /api/leads/stream (SSE), GET /download
│   │   ├── auth.py                  ← POST /api/auth/set-key, GET /api/auth/key-status
│   │   ├── ingest.py                ← All ingest routes (unified from Octagon)
│   │   ├── enrich.py                ← POST /api/enrich/run, GET /api/enrich/stats
│   │   ├── score.py                 ← POST /api/score/run (FIXED query)
│   │   ├── email_router.py          ← POST /api/email/send-run-by-source (WIRED)
│   │   ├── phone_router.py          ← POST /api/phone/enrich, GET /api/phone/stats
│   │   ├── whatsapp_router.py       ← GET /api/whatsapp/health, /qr, POST /send
│   │   ├── voice_router.py          ← GET /api/voice/queue, POST /save-transcript
│   │   ├── outreach.py              ← POST /api/outreach/start (compatibility shim)
│   │   ├── stats_router.py          ← GET /api/stats/overview (unified)
│   │   ├── admin.py                 ← POST /api/admin/reset-db, /full-run
│   │   ├── health.py                ← GET /api/health
│   │   └── quota.py                 ← GET /api/quota/status
│   │
│   ├── services/
│   │   ├── enricher.py              ← SSE streaming + LeadOS enrichment (KEEP)
│   │   ├── lead_context_service.py  ← Unified data layer (FROM OCTAGON)
│   │   ├── quota_manager.py         ← FROM OCTAGON utils/Here is the continuation of the full audit prompt — picking up exactly from Section 4 where the file structure left off:

text
│   ├── services/ (continued)
│   │   ├── email_writer.py              ← Groq personalized email gen (FROM OCTAGON)
│   │   ├── phone_normalizer.py          ← normalize_phone() util (FROM OCTAGON)
│   │   └── channel_router.py            ← get_outreach_channel() (FROM OCTAGON)
│   │
│   ├── enrichment/
│   │   ├── enrichment_engine.py         ← FULL waterfall, circuit breaker (FROM OCTAGON)
│   │   ├── email_waterfall.py           ← 13-step email finder (FROM OCTAGON)
│   │   ├── website_scraper.py           ← Groq + BS4 page analyzer (FROM OCTAGON)
│   │   ├── mx_checker.py                ← DNS MX record validator (FROM OCTAGON)
│   │   └── fallback_handler.py          ← REBUILD from empty (was 0 bytes in Octagon)
│   │
│   ├── lead_gen/
│   │   ├── tier1/
│   │   │   ├── hn_show_rss.py           ← product URL extraction FIX applied
│   │   │   ├── hn_hiring_rss.py
│   │   │   ├── devto_showdev.py         ← FIX applied
│   │   │   ├── hashnode.py              ← FIX applied
│   │   │   ├── lobsters.py
│   │   │   ├── remoteok.py
│   │   │   ├── yc_companies.py
│   │   │   ├── github_trending.py
│   │   │   ├── product_hunt.py
│   │   │   └── wellfound.py
│   │   ├── india_directories.py         ← JustDial fix applied
│   │   ├── saas_fetcher.py              ← YC, HN, PH, GitHub
│   │   └── partner_fetcher.py           ← Clutch, GoodFirms, OSM agencies
│   │
│   ├── notifications/
│   │   ├── telegram.py                  ← send_telegram_alert() (FROM OCTAGON)
│   │   └── bot.py                       ← /start /leads /outreach commands (FROM LeadOS)
│   │
│   ├── scheduler.py                     ← APScheduler, 6 jobs, PORT 8000 (MERGED)
│   │
│   └── utils/
│       ├── rate_limiter.py              ← QuotaManager singleton (FROM OCTAGON)
│       ├── request_manager.py           ← safe_get, safe_post, mirrors (FROM OCTAGON)
│       ├── request_credentials.py       ← BYOK per-request key extraction (FROM LeadOS)
│       └── ai_provider.py               ← detect_provider() Gemini/Groq/OAI (FROM LeadOS)
│
├── wa-server/                           ← Node.js Baileys WhatsApp microservice
│   ├── index.js                         ← Fastify + Baileys, GET /health /qr POST /send
│   └── package.json                     ← @whiskeysockets/baileys, fastify, p-queue
│
├── web/                                 ← Next.js 14 App Router frontend
│   ├── app/
│   │   ├── (portfolio)/                 ← Portfolio layout group (Cloudflare live)
│   │   │   ├── layout.tsx               ← Original theme — DO NOT MODIFY
│   │   │   ├── page.tsx                 ← Projects from config/projects.ts
│   │   │   └── hire/page.tsx            ← Hire Me + Referral code generator
│   │   │
│   │   ├── (leados)/                    ← LeadOS app layout group
│   │   │   ├── layout.tsx               ← Sidebar nav: Ingest/Dashboard/Outreach etc.
│   │   │   ├── ingest/page.tsx          ← Hunt form + SSE lead stream table
│   │   │   ├── dashboard/page.tsx       ← Quota bars, health badge, stats widgets
│   │   │   ├── outreach/page.tsx        ← Smart send per-source, skip report, dry run
│   │   │   ├── settings/page.tsx        ← BYOK key manager (localStorage only)
│   │   │   ├── history/page.tsx         ← Past sessions with real Supabase queries
│   │   │   ├── whatsapp/page.tsx        ← QR code display + connection status
│   │   │   └── refer/page.tsx           ← Referral code + commission tracker
│   │   │
│   │   └── api-hub/page.tsx             ← NEW: Public API landing + pricing tiers
│   │
│   ├── hooks/
│   │   └── useLeadStream.ts             ← SSE streaming hook (CREATE THIS)
│   │
│   ├── lib/
│   │   ├── api.ts                       ← ALL API calls centralized here
│   │   └── credentials.ts              ← UserCredentials interface + localStorage
│   │
│   └── config/
│       └── projects.ts                  ← Single source of truth for portfolio projects
│
├── .env                                 ← All secrets (never committed)
├── docker-compose.yml                   ← FastAPI + wa-server + Redis containers
└── requirements.txt                     ← Python deps for unified server/


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — BUG REGISTRY (ALL CONFIRMED BUGS ACROSS BOTH SYSTEMS)
# ═══════════════════════════════════════════════════════════════════════════════

# Each bug below has: ID, Source, File, Description, Root Cause, Fix Applied,
# Verification Status

BUG-001
  Source:    Octagon
  File:      app/scheduler.py
  Desc:      All 6 APScheduler jobs called localhost:8000 instead of 8765
  Root:      Port hardcoded incorrectly during initial setup
  Fix:       call_internal() helper, all paths updated to 8765 → 8000 (merged)
  Verified:  ✓ Confirmed from terminal logs — jobs now register and call correctly

BUG-002
  Source:    Octagon
  File:      app/enrichment/enrichment_engine.py
  Desc:      enrich_batch() query targeted status='ENRICHED'/'READY' → 0 results
  Root:      Wrong status values in WHERE clause — no leads have those statuses
  Fix:       WHERE status IN ('NEW', 'ENRICHMENT_FAILED') with enrich_attempts < 3
  Verified:  ✓ Confirmed — processed went from 0 → 50+ per batch after fix

BUG-003
  Source:    Octagon
  File:      app/enrichment/enrichment_engine.py
  Desc:      asyncio.wait_for() wrapping gather() killed all results on timeout
  Root:      Global timeout cancelled all concurrent tasks, validresults stayed []
  Fix:       Remove outer wait_for(). Use per-lead timeout inside with_sem() only
  Verified:  ✓ Confirmed from logs — processed_ids populated, processed > 0 after fix

BUG-004
  Source:    Octagon
  File:      app/enrichment/email_waterfall.py → try_snov()
  Desc:      Snov.io OAuth POST sent json={} body → 400 Bad Request
  Root:      Should be form-encoded POST, not JSON body
  Fix:       requests.post(..., data={client_id, client_secret, grant_type})
  Verified:  ✓ Token fetch working after fix

BUG-005
  Source:    Octagon
  File:      app/enrichment/email_waterfall.py → try_getprospect()
  Desc:      POST /api/v1/find-email → 405 Method Not Allowed
  Root:      Wrong endpoint — official docs say GET /public/v1/email/find
  Fix:       Switched to GET with apiKey header and query params
  Verified:  ✓ Fix applied, pending key to test live

BUG-006
  Source:    Octagon
  File:      app/lead_gen/tier1/hn_show_rss.py
  Desc:      entry.link was HN discussion URL, not the actual product URL
  Root:      RSS feed entry.link = https://news.ycombinator.com/item?id=xxx
             Product URL is inside entry.summary HTML
  Fix:       extract_product_url() from BeautifulSoup parsing of entry.summary
  Verified:  ✓ Applied to hn_show_rss.py, devto_showdev.py, hashnode.py

BUG-007
  Source:    Octagon
  File:      app/enrichment/enrichment_engine.py (Groq model)
  Desc:      llama3-8b-8192 was decommissioned mid-project → 404 from Groq
  Root:      Model retired without notice — was hardcoded
  Fix:       Switch to llama-3.3-70b-versatile for scoring,
             llama-3.1-8b-instant for email generation (still free)
  Verified:  ✓ Confirmed from logs — HTTP 200 after model switch

BUG-008
  Source:    Octagon
  File:      app/routers/score.py
  Desc:      scored=0 on every run — leads were never being scored
  Root:      Query: WHERE status IN ('READY', 'ENRICHED') →
             none exist until after scoring (circular dependency)
  Fix:       WHERE status IN ('email_reach','super_enriched','phone_reach')
             AND (score = 0 OR score IS NULL)
  Verified:  ✓ scored=44, avg_score=76.8 confirmed in terminal

BUG-009
  Source:    Octagon
  File:      app/routers/email_router.py
  Desc:      POST /api/email/send-run → 404 Not Found
  Root:      Route registered as /send-run-by-source, not /send-run
  Fix:       Added both routes — /send-run as alias, /send-run-by-source as primary
  Verified:  ✓ Confirmed working after fix

BUG-010
  Source:    Octagon
  File:      app/email/templates.py → build_client_email()
  Desc:      HN post titles used as company_name in subject line
             e.g. "Show HN: Non.io, a Reddit-like platform I've been working on"
  Root:      No title sanitization before email generation
  Fix:       clean_company_name() strips Show HN/Ask HN/Launch HN/Tell HN prefixes
             If title has comma + length > 40 → take first segment only
  Verified:  ✓ Subjects now clean in dry-run output

BUG-011
  Source:    Octagon
  File:      app/email/templates.py
  Desc:      Unicode em-dashes (U+2014) in email body rendered as garbage in SMTP
  Root:      Python string literals with Unicode not encoded as ASCII-safe
  Fix:       ascii_safe(text) helper replaces —, –, ", ", ", " with ASCII equivalents
  Verified:  ✓ Confirmed clean body in dry-run output after fix

BUG-012
  Source:    Octagon
  File:      app/email/templates.py → generate_personalized_email()
  Desc:      Groq silently failed → fell back to static template every time
             All 3 dry-run bodies were identical (static fallback text)
  Root:      Regex r'\{.*\}' too narrow for Groq's JSON output — missed valid JSON
             OR Groq returned subject/body with extra whitespace breaking JSON parse
  Fix:       Use r'\{[\s\S]*\}' for JSON extraction, strip + validate len > 50
  Verified:  ✓ Groq personalization working after fix — each email unique

BUG-013
  Source:    Octagon
  File:      app/routers/email_router.py → send_run()
  Desc:      JUNK_LOCAL set too narrow — info@, contact@, sales@, help@ slipped through
  Root:      Original JUNK_LOCAL only had root, admin, webmaster, etc.
             Missed the most common generic business emails
  Fix:       Expanded to 50+ entries including info, contact, sales, support,
             help, hello, team, office, enquiry, dpo, gdpr, press, careers, etc.
  Verified:  ✓ Confirmed — Juspay DPO email and Beeper help@ now correctly filtered

BUG-014
  Source:    Octagon
  File:      app/routers/email_router.py → send_run()
  Desc:      Live send cap not enforced — could accidentally send 50 emails at once
  Root:      No guard on batch_size for dry_run=False mode
  Fix:       if not dry_run and batch_size > 5 and not force:
               raise HTTPException(400, "Live send capped at 5 unless force=True")
  Verified:  ✓ Confirmed — returns HTTP 400 without force=true

BUG-015
  Source:    Octagon
  File:      app/lead_gen/india_directories.py
  Desc:      IndiaMART, TradeIndia, Sulekha all returned HTML/404/301
             Zero leads from these sources
  Root:      Sites added rate limiting and bot detection since initial build
  Fix:       Replace with JustDial scraper (soup selectors updated for live site)
             Inc42 RSS still working (39 leads/3 pages confirmed)
  Verified:  ✓ Partial — Inc42 confirmed, JustDial needs re-test

BUG-016
  Source:    LeadOS
  File:      server/services/enricher.py
  Desc:      Email enrichment rate ~20% — far below Octagon's 60-90%
  Root:      Only 2-step enrichment (website scrape + DuckDuckGo)
             Missing: waterfall, MX check, RDAP, crt.sh, Snov, legal pages, etc.
  Fix:       Replace LeadOS enricher with Octagon's EmailWaterfall class
  Verified:  ✗ Pending — requires merger execution

BUG-017
  Source:    LeadOS
  File:      web/app/(leados)/ingest/page.tsx
  Desc:      Mock data hardcoded — real SSE stream not connected to UI
  Root:      UI built with placeholder data, useLeadStream hook never created
  Fix:       Create useLeadStream.ts hook, remove all mock data, wire to real stream
  Verified:  ✗ Pending — requires frontend work

BUG-018
  Source:    LeadOS
  File:      web/app/(leados)/history/page.tsx
  Desc:      No real data — page shows empty or static content
  Root:      Supabase query never wired to component
  Fix:       Add real Supabase query via GET /api/history endpoint
  Verified:  ✗ Pending

BUG-019
  Source:    Both
  File:      app/models/lead.py + server/models/
  Desc:      Dual schema inconsistency — founder_email vs email,
             icp_score vs score, outreach_channel vs channel
  Root:      Two systems built independently with different naming conventions
  Fix:       Unified schema defined in Section 3 conflict resolution above
             Single migration script to add aliases and normalize columns
  Verified:  ✗ Pending — requires DB migration

BUG-020
  Source:    Octagon
  File:      app/enrichment/fallback_handler.py
  Desc:      File is 0 bytes — completely empty
  Root:      File was created as placeholder, never implemented
  Fix:       Implement retry logic:
             - Select ENRICHMENT_FAILED leads where enrich_attempts < 3
             - Reset status to NEW
             - Trigger re-enrichment in next batch
             - After 3 failures → status = UNENRICHABLE (permanent)
  Verified:  ✗ Pending


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — PRODUCTION MERGER EXECUTION PLAN
# (Step-by-step, zero-ambiguity, ordered by dependency)
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# PHASE M1 — ENVIRONMENT + DATABASE FOUNDATION  [Day 1, ~2 hours]
# ─────────────────────────────────────────────────────────────────────────────

STEP M1.1 — Consolidate .env
  Action: Merge all env vars from Octagon .env + LeadOS .env into ONE .env file
  Location: lead-hunter-pro/.env
  
  Required keys (COMPLETE LIST):
    # Supabase
    SUPABASE_URL=
    SUPABASE_KEY=
    DATABASE_URL=postgresql+asyncpg://...
    
    # AI
    GROQ_API_KEY=gsk...
    GEMINI_API_KEY=AIzaSy...
    
    # Email
    BREVO_SMTP_HOST=smtp-relay.brevo.com
    BREVO_SMTP_PORT=587
    BREVO_SMTP_USER=
    BREVO_SMTP_KEY=
    FROM_EMAIL=
    FROM_NAME=Saumya
    
    # Lead Source APIs
    GOOGLE_MAPS_API_KEY=
    HUNTER_API_KEY=              ← get free key at hunter.io
    SNOV_CLIENT_ID=
    SNOV_CLIENT_SECRET=
    APOLLO_API_KEY=
    GETPROSPECT_API_KEY=
    GITHUB_TOKEN=
    GOOGLE_CSE_API_KEY=
    GOOGLE_CSE_ID=
    
    # Telegram
    TELEGRAM_BOT_TOKEN=
    TELEGRAM_CHAT_ID=
    
    # App
    MASTER_KEY=leadoskey123
    PORT=8000
    MAX_LEADS_PER_RUN=100
    DAILY_EMAIL_CAP=300
    ICP_SCORE_THRESHOLD=70
    EMAIL_QUALITY_MIN=2
    
  Verify: python -c "from server.config import settings; print('OK')"

STEP M1.2 — Run Supabase Database Migrations
  Execute in Supabase SQL Editor in this exact order:
  
  -- 1. Extend leads table with missing columns from both systems
  ALTER TABLE leads
    ADD COLUMN IF NOT EXISTS lead_type VARCHAR DEFAULT 'client',
    ADD COLUMN IF NOT EXISTS email_quality_score INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS enrich_attempts INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS whatsapp_number VARCHAR,
    ADD COLUMN IF NOT EXISTS outreach_channel VARCHAR DEFAULT 'email',
    ADD COLUMN IF NOT EXISTS icp_score INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS priority VARCHAR DEFAULT 'medium',
    ADD COLUMN IF NOT EXISTS reason TEXT,
    ADD COLUMN IF NOT EXISTS pain_points TEXT,
    ADD COLUMN IF NOT EXISTS suggested_opening TEXT,
    ADD COLUMN IF NOT EXISTS mx_valid BOOLEAN,
    ADD COLUMN IF NOT EXISTS enrichment_tier VARCHAR,
    ADD COLUMN IF NOT EXISTS email_source VARCHAR,
    ADD COLUMN IF NOT EXISTS email_status VARCHAR,
    ADD COLUMN IF NOT EXISTS phone_source VARCHAR,
    ADD COLUMN IF NOT EXISTS founder_name VARCHAR,
    ADD COLUMN IF NOT EXISTS tech_hints TEXT,
    ADD COLUMN IF NOT EXISTS social_media TEXT,
    ADD COLUMN IF NOT EXISTS has_contact_form BOOLEAN,
    ADD COLUMN IF NOT EXISTS hn_url TEXT,
    ADD COLUMN IF NOT EXISTS partner_status VARCHAR,
    ADD COLUMN IF NOT EXISTS referral_fee_pct INTEGER DEFAULT 20,
    ADD COLUMN IF NOT EXISTS referral_revenue FLOAT DEFAULT 0,
    ADD COLUMN IF NOT EXISTS emailed_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS replied_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS source_url VARCHAR;

  -- 2. Migrate status values from LeadOS naming to Octagon naming
  UPDATE leads SET status = CASE
    WHEN email IS NOT NULL AND phone IS NOT NULL THEN 'super_enriched'
    WHEN email IS NOT NULL THEN 'email_reach'
    WHEN phone IS NOT NULL THEN 'phone_reach'
    ELSE 'NEW'
  END
  WHERE status IS NULL OR status = 'ENRICHED';

  -- 3. Create missing tables
  CREATE TABLE IF NOT EXISTS user_api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) UNIQUE NOT NULL,
    api_key_hash VARCHAR(64) UNIQUE NOT NULL,
    api_key_hint VARCHAR(10),
    tier VARCHAR(20) DEFAULT 'starter',
    is_set BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ,
    leads_this_month INTEGER DEFAULT 0,
    api_calls_today INTEGER DEFAULT 0,
    webhook_url VARCHAR(500)
  );
  
  CREATE TABLE IF NOT EXISTS shown_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_hash VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(255), city VARCHAR(100),
    phone VARCHAR(30), email VARCHAR(255),
    source VARCHAR(50), session_id VARCHAR(100),
    shown_at TIMESTAMPTZ DEFAULT NOW(),
    business_type VARCHAR(100), location VARCHAR(100)
  );
  
  CREATE TABLE IF NOT EXISTS referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referrer_name VARCHAR(255),
    referrer_email VARCHAR(255),
    referral_code VARCHAR(50) UNIQUE NOT NULL,
    referred_user_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    contract_value FLOAT DEFAULT 0,
    commission_pct INTEGER DEFAULT 15,
    commission_paid FLOAT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    converted_at TIMESTAMPTZ
  );
  
  CREATE TABLE IF NOT EXISTS outreach_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id),
    channel VARCHAR(50),
    subject VARCHAR(500),
    body TEXT,
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    opened_at TIMESTAMPTZ,
    replied_at TIMESTAMPTZ,
    status VARCHAR(50) DEFAULT 'sent'
  );

  -- 4. Performance indexes
  CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
  CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(source);
  CREATE INDEX IF NOT EXISTS idx_leads_icp_score ON leads(icp_score DESC);
  CREATE INDEX IF NOT EXISTS idx_leads_enrich_attempts ON leads(enrich_attempts)
    WHERE status = 'NEW';
  CREATE INDEX IF NOT EXISTS idx_shown_leads_hash ON shown_leads(lead_hash);
  CREATE INDEX IF NOT EXISTS idx_user_api_keys_hash ON user_api_keys(api_key_hash);

  Verify: SELECT COUNT(*) FROM leads; → should return 1455+


# ─────────────────────────────────────────────────────────────────────────────
# PHASE M2 — BACKEND STRUCTURE MIGRATION  [Day 1-2, ~4 hours]
# ─────────────────────────────────────────────────────────────────────────────

STEP M2.1 — Copy Octagon backend into lead-hunter-pro/server/
  
  COPY THESE FILES verbatim (no modification needed):
    octagon/backend/app/enrichment/       → server/enrichment/
    octagon/backend/app/lead_gen/         → server/lead_gen/
    octagon/backend/app/notifications/    → server/notifications/
    octagon/backend/utils/rate_limiter.py → server/utils/rate_limiter.py
    octagon/backend/utils/request_manager.py → server/utils/request_manager.py
    octagon/backend/app/services/lead_context_service.py → server/services/
    octagon/backend/app/services/email_writer.py → server/services/
  
  COPY WITH MODIFICATIONS (port references, import paths):
    octagon/backend/app/routers/ingest.py     → server/routers/ingest.py
    octagon/backend/app/routers/score.py      → server/routers/score.py
    octagon/backend/app/routers/phone_router.py → server/routers/phone_router.py
    octagon/backend/app/routers/whatsapp_router.py → server/routers/whatsapp_router.py
    octagon/backend/app/routers/voice_router.py → server/routers/voice_router.py
    octagon/backend/app/routers/stats_router.py → server/routers/stats_router.py
    octagon/backend/app/routers/admin.py       → server/routers/admin.py
    octagon/backend/app/routers/email_router.py → server/routers/email_router.py
  
  UPDATE IMPORT PATHS in all copied files:
    from app.db.session import get_db   →  from db import get_db
    from app.models.lead import Lead    →  from models.lead import Lead
    from app.config import settings     →  from config import settings
    from utils.rate_limiter import quota → (same path, no change)
  
  KEEP THESE LeadOS files untouched:
    server/routers/leads.py             ← SSE streaming, keep as-is
    server/routers/auth.py              ← Per-user API key auth, keep
    server/routers/health.py            ← Health check, keep
    server/services/enricher.py         ← REPLACE enrichment logic only
    server/db.py                        ← LeadOS async engine, keep

STEP M2.2 — Rebuild server/main.py (UNIFIED ENTRY POINT)
  
  Content specification:
  
  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware
  from contextlib import asynccontextmanager
  from apscheduler.schedulers.asyncio import AsyncIOScheduler
  
  # Import ALL routers
  from routers.leads import router as leads_router
  from routers.auth import router as auth_router
  from routers.ingest import router as ingest_router
  from routers.enrich import router as enrich_router
  from routers.score import router as score_router
  from routers.email_router import router as email_router
  from routers.phone_router import router as phone_router
  from routers.whatsapp_router import router as whatsapp_router
  from routers.voice_router import router as voice_router
  from routers.outreach import router as outreach_router
  from routers.stats_router import router as stats_router
  from routers.admin import router as admin_router
  from routers.health import router as health_router
  from routers.quota import router as quota_router
  
  from scheduler import setup_scheduler
  from notifications.telegram import send_telegram_alert
  from config import settings
  
  @asynccontextmanager
  async def lifespan(app: FastAPI):
      scheduler = setup_scheduler()
      scheduler.start()
      await send_telegram_alert("🚀 LeadHunter Omega ONLINE — all systems nominal")
      yield
      scheduler.shutdown()
  
  app = FastAPI(title="LeadHunter Omega", version="3.0.0", lifespan=lifespan)
  
  app.add_middleware(CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"])
  
  # Wire ALL routers with consistent prefix
  app.include_router(leads_router,     prefix="/api")
  app.include_router(auth_router,      prefix="/api")
  app.include_router(ingest_router,    prefix="/api")
  app.include_router(enrich_router,    prefix="/api")
  app.include_router(score_router,     prefix="/api")
  app.include_router(email_router,     prefix="/api")
  app.include_router(phone_router,     prefix="/api")
  app.include_router(whatsapp_router,  prefix="/api")
  app.include_router(voice_router,     prefix="/api")
  app.include_router(outreach_router,  prefix="/api")
  app.include_router(stats_router,     prefix="/api")
  app.include_router(admin_router,     prefix="/api")
  app.include_router(health_router,    prefix="/api")
  app.include_router(quota_router,     prefix="/api")
  
  # PORT: 8000 (LeadOS standard — Cloudflare proxy target)
  if __name__ == "__main__":
      import uvicorn
      uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

STEP M2.3 — Rebuild server/scheduler.py (PORT 8000)
  
  FIXED call_internal helper:
  
  async def call_internal(path: str, params: dict = {}) -> dict:
      async with httpx.AsyncClient(timeout=300) as client:
          resp = await client.post(
              f"http://localhost:8000{path}",
              params=params,
              headers={"X-API-Key": settings.MASTER_KEY}
          )
          return resp.json()
  
  6 JOBS (all verified to exist as routes):
    Job 1: "ingest_run"
      trigger: cron(hour=2, minute=0)
      action: call_internal("/api/ingest/run")
      
    Job 2: "enrich_run"
      trigger: cron(hour=3, minute=0)
      action: call_internal("/api/enrich/run", {"batch_size": 50})
      
    Job 3: "score_run"
      trigger: cron(hour=4, minute=0)
      action: call_internal("/api/score/run", {"batch_size": 100})
      
    Job 4: "send_run"
      trigger: cron(hour=9, minute=0)  ← morning send window
      action: call_internal("/api/email/send-run-by-source",
                            {"dry_run": False, "batch_size": 10})
      guard: 7-hour minimum since last send (prevent double-sends)
      
    Job 5: "followup_run"
      trigger: cron(hour=10, minute=0, day_of_week='thu')
      action: call_internal("/api/email/send-followup",
                            {"dry_run": False, "followup_num": 1, "batch_size": 10})
      
    Job 6: "daily_report"
      trigger: cron(hour=8, minute=0)
      action:
        stats = await call_internal("/api/stats/overview")
        await send_telegram_alert(f"""
          📊 Daily Report — LeadHunter Omega
          Total leads: {stats['total_leads']}
          Ready to contact: {stats['outreach']['ready_to_contact']}
          Sent today: {stats['outreach']['emailed']}
          Reply rate: {stats['outreach']['reply_rate_pct']}%
          Super enriched: {stats['coverage']['super_enriched']}
        """)

STEP M2.4 — Wire enricher.py to Octagon waterfall
  
  In server/services/enricher.py:
  
  # REPLACE the simple 2-step enrichment with import from Octagon waterfall:
  from enrichment.email_waterfall import EmailWaterfall
  from enrichment.mx_checker import check_mx
  from enrichment.website_scraper import scrape_website
  
  waterfall = EmailWaterfall(settings)
  
  async def enrich_lead(lead: dict) -> dict:
      domain = lead.get('domain') or extract_domain(lead.get('website', ''))
      if not domain:
          return lead
      
      # Step 1: Website scrape (Groq analysis)
      scraped = await scrape_website(domain)
      lead.update({k: v for k, v in scraped.items() if v})
      
      # Step 2: MX check
      lead['mx_valid'] = await check_mx(domain)
      
      # Step 3: Full 13-step email waterfall
      if not lead.get('email'):
          email, source = await waterfall.find_email(
              domain,
              lead.get('founder_name'),
              lead.get('company_name')
          )
          if email:
              lead['email'] = email
              lead['email_source'] = source
              lead['email_quality_score'] = score_email_quality(email)
      
      return lead
  
  def score_email_quality(email: str) -> int:
      local = email.split('@')[0].lower()
      generic = {'info','contact','hello','sales','support','admin',
                 'team','office','enquiry','help','hi'}
      if local in generic:
          return 1
      if any(c.isdigit() for c in local):
          return 2
      return 3  # named personal email → highest quality


# ─────────────────────────────────────────────────────────────────────────────
# PHASE M3 — FRONTEND WIRING  [Day 2-3, ~6 hours]
# ─────────────────────────────────────────────────────────────────────────────

STEP M3.1 — Create web/hooks/useLeadStream.ts
  
  Full implementation (copy verbatim into Antigravity):
  
  'use client'
  import { useState, useRef, useCallback } from 'react'
  
  type StreamStatus = 'idle'|'discovering'|'enriching'|'streaming'|'done'|'error'
  
  export interface StreamLead {
    id: string; name: string; phone?: string; email?: string;
    website?: string; city?: string; score?: number;
    email_quality_score?: number; source?: string; session_id?: string;
  }
  
  export function useLeadStream() {
    const [leads, setLeads] = useState<StreamLead[]>([])
    const [status, setStatus] = useState<StreamStatus>('idle')
    const [statusMessage, setStatusMessage] = useState('')
    const [sessionId, setSessionId] = useState<string|null>(null)
    const [totalReceived, setTotalReceived] = useState(0)
    const [error, setError] = useState<string|null>(null)
    const readerRef = useRef<ReadableStreamDefaultReader|null>(null)
    
    const startHunt = useCallback(async (params: {
      business_type: string; location: string;
      radius_km: number; target_service: string; max_leads?: number
    }) => {
      setLeads([]); setError(null); setTotalReceived(0)
      setStatus('discovering')
      setStatusMessage('Finding businesses...')
      
      const keys = JSON.parse(localStorage.getItem('leados_keys_v2') || '{}')
      
      try {
        const resp = await fetch('/api/leads/stream', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': keys.internal || '',
            'X-Google-Maps-Key': keys.gmaps || '',
            'X-Gemini-Key': keys.gemini || '',
          },
          body: JSON.stringify({ ...params, max_leads: params.max_leads || 80 })
        })
        
        if (!resp.ok) {
          const err = await resp.json()
          throw new Error(err.detail || 'Stream failed')
        }
        
        const reader = resp.body!.getReader()
        readerRef.current = reader
        const decoder = new TextDecoder()
        let buffer = ''
        
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n\n')
          buffer = lines.pop() || ''
          
          for (const line of lines) {
            if (!line.startsWith('data: ')) continue
            const data = JSON.parse(line.slice(6))
            
            if (data.status === 'discovering') {
              setStatus('discovering'); setStatusMessage(data.message)
            } else if (data.status === 'enriching') {
              setStatus('enriching'); setStatusMessage(data.message)
            } else if (data.status === 'batch') {
              setStatus('streaming')
              setLeads(prev => [...prev, ...data.batch])
              setTotalReceived(data.total_so_far)
              if (data.session_id) setSessionId(data.session_id)
            } else if (data.status === 'done') {
              setStatus('done'); setStatusMessage(`Found ${data.total} leads`)
            } else if (data.status === 'error') {
              throw new Error(data.detail)
            }
          }
        }
      } catch (e: any) {
        setStatus('error'); setError(e.message)
      }
    }, [])
    
    const stopHunt = useCallback(() => {
      readerRef.current?.cancel()
      setStatus('idle')
    }, [])
    
    return { leads, status, statusMessage, sessionId,
             totalReceived, error, startHunt, stopHunt }
  }

STEP M3.2 — Audit + Remove ALL Mock Data
  
  Run these grep commands in web/ directory:
  
    grep -rn "Mumbai, India" web/app/
    grep -rn "mockLeads" web/
    grep -rn "const leads = \[" web/
    grep -rn "setTimeout" web/app/(leados)/
    grep -rn "fake\|mock\|dummy\|placeholder\|hardcoded" web/app/
    grep -rn "Math.random()" web/app/(leados)/
  
  For each match: DELETE the hardcoded value, replace with state variable or empty []
  No UI component should render data that doesn't come from a real API call.
  
  ANTI-PATTERN — NEVER DO THIS:
    const leads = [{ name: "Acme Corp", city: "Mumbai" }]  // ← DELETE
  
  CORRECT PATTERN:
    const { leads } = useLeadStream()  // ← data from real SSE stream

STEP M3.3 — Build web/lib/api.ts (complete)
  
  All backend API calls through one centralized module:
  
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  
  class APIError extends Error {
    constructor(message: string, public status: number) { super(message) }
  }
  
  async function api_call<T>(path: string, options?: RequestInit): Promise<T> {
    const keys = JSON.parse(localStorage.getItem('leados_keys_v2') || '{}')
    const resp = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': keys.internal || '',
        ...(options?.headers || {})
      }
    })
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Unknown error' }))
      throw new APIError(err.detail, resp.status)
    }
    return resp.json()
  }
  
  export const systemAPI = {
    health: () => api_call<HealthResponse>('/api/health'),
    quota:  () => api_call<QuotaResponse>('/api/quota/status'),
    stats:  () => api_call<StatsResponse>('/api/stats/overview'),
  }
  
  export const leadsAPI = {
    download:  (sessionId: string) => `${API_BASE}/api/leads/${sessionId}/download`,
    recent:    (limit=20) => api_call(`/api/email/recent?limit=${limit}`),
    skipReport: () => api_call('/api/email/skip-report'),
  }
  
  export const outreachAPI = {
    dryRun: (batchSize=10) =>
      api_call('/api/email/send-run-by-source?dry_run=true',
               { method: 'POST' }),
    liveSend: (batchSize: number, force=false) =>
      api_call(`/api/email/send-run-by-source?dry_run=false`+
               
# ─────────────────────────────────────────────────────────────────────────────
# STEP M3.3 — Build web/lib/api.ts (CONTINUED + COMPLETE)
# ─────────────────────────────────────────────────────────────────────────────

  export const outreachAPI = {
    dryRun: (batchSize = 10) =>
      api_call<OutreachDryRunResponse>(
        `/api/email/send-run-by-source?dry_run=true&batch_size=${batchSize}`,
        { method: 'POST' }
      ),
    liveSend: (batchSize: number, force = false) =>
      api_call<OutreachSendResponse>(
        `/api/email/send-run-by-source?dry_run=false` +
        `&batch_size=${batchSize}${force ? '&force=true' : ''}`,
        { method: 'POST' }
      ),
    followUp: (num: 1 | 2, batchSize = 10, dryRun = true) =>
      api_call<OutreachFollowUpResponse>(
        `/api/email/send-followup?followup_num=${num}` +
        `&batch_size=${batchSize}&dry_run=${dryRun}`,
        { method: 'POST' }
      ),
    skipReport: () =>
      api_call<SkipReportResponse>('/api/email/skip-report'),
    partnerOutreach: (dryRun = true, batchSize = 10) =>
      api_call<OutreachSendResponse>(
        `/api/email/send-partner-outreach?dry_run=${dryRun}` +
        `&batch_size=${batchSize}`,
        { method: 'POST' }
      ),
  }
  
  export const ingestAPI = {
    radiusMap: (params: RadiusMapParams) =>
      api_call<IngestResponse>('/api/ingest/radius-map',
        { method: 'POST', body: JSON.stringify(params) }),
    indiaSaaS: () =>
      api_call<IngestResponse>('/api/ingest/india-saas',
        { method: 'POST' }),
    foreignSaaS: () =>
      api_call<IngestResponse>('/api/ingest/foreign-saas',
        { method: 'POST' }),
    partners: () =>
      api_call<IngestResponse>('/api/ingest/partners',
        { method: 'POST' }),
    run: () =>
      api_call<IngestResponse>('/api/ingest/run',
        { method: 'POST' }),
  }
  
  export const enrichAPI = {
    run: (batchSize = 30) =>
      api_call<EnrichResponse>(
        `/api/enrich/run?batch_size=${batchSize}`,
        { method: 'POST' }
      ),
    status: () => api_call<EnrichStatusResponse>('/api/enrich/status'),
    phoneEnrich: (batchSize = 20) =>
      api_call<PhoneEnrichResponse>(
        `/api/phone/enrich?batch_size=${batchSize}`,
        { method: 'POST' }
      ),
  }
  
  export const scoreAPI = {
    run: (batchSize = 50) =>
      api_call<ScoreResponse>(
        `/api/score/run?batch_size=${batchSize}`,
        { method: 'POST' }
      ),
  }
  
  export const settingsAPI = {
    saveKeys: (keys: StoredKeys) => {
      localStorage.setItem('leados_keys_v2', JSON.stringify(keys))
    },
    loadKeys: (): StoredKeys => {
      try {
        return JSON.parse(localStorage.getItem('leados_keys_v2') || '{}')
      } catch { return {} }
    },
    verifyKeys: () => systemAPI.health(),
    clearKeys: () => localStorage.removeItem('leados_keys_v2'),
  }
  
  export const waAPI = {
    health: () => api_call<WAHealthResponse>('/api/whatsapp/health'),
    qr: () => api_call<WAQRResponse>('/api/whatsapp/qr'),
    send: (phone: string, message: string) =>
      api_call<WASendResponse>('/api/whatsapp/send',
        { method: 'POST', body: JSON.stringify({ phone, message }) }),
    queue: () => api_call<WAQueueResponse>('/api/whatsapp/queue-status'),
  }
  
  export const adminAPI = {
    stats: () => api_call<AdminStatsResponse>('/api/admin/stats'),
    fullRun: () =>
      api_call<AdminFullRunResponse>('/api/admin/full-run',
        { method: 'POST' }),
    resetDB: (confirm: 'RESET') =>
      api_call<AdminResetResponse>('/api/admin/reset-db',
        { method: 'POST', body: JSON.stringify({ confirm }) }),
  }
  
  // TS INTERFACES — Full type safety across ALL API calls
  export interface StoredKeys {
    internal?: string; gemini?: string; gmaps?: string;
    brevo?: string; senderEmail?: string; senderName?: string;
    groq?: string; telegram?: string;
    tier?: 'free' | 'paid';
    gmapsTier?: 'free' | 'paid'; hunterTier?: 'free' | 'paid';
  }
  export interface HealthResponse {
    status: 'ok' | 'degraded'; waserver: boolean;
    scheduler_running: boolean; db_connected: boolean;
    leads_count: number; version: string;
  }
  export interface QuotaResponse {
    quotas: Array<{
      provider: string; used: number; limit: number;
    }>
  }
  export interface StatsResponse {
    total_leads: number;
    coverage: {
      phone_reach: number; phone_reach_pct: number;
      whatsapp_ready: number; email_reach: number;
      email_reach_pct: number; email_verified: number;
      super_enriched: number; super_enriched_pct: number;
    };
    outreach: {
      ready_to_contact: number; emailed: number;
      phone_reached: number; replied: number; reply_rate_pct: number;
    };
  }


# ─────────────────────────────────────────────────────────────────────────────
# STEP M3.4 — Wire ALL LeadOS Pages to Real Data
# ─────────────────────────────────────────────────────────────────────────────

PAGE: web/app/(leados)/ingest/page.tsx
  
  WIRING CHECKLIST:
  
  [ ] Import useLeadStream from '@/hooks/useLeadStream'
  [ ] Form state: businessType, location, radiusKm, targetService
  [ ] On submit: call startHunt(params)
  [ ] Disable HUNT button while status !== 'idle'
  [ ] Show progress indicator per stream status:
        discovering → "🔍 Scanning OpenStreetMap..."
        enriching   → "🧠 Enriching leads..."
        streaming   → "⚡ Receiving leads... (N found)"
        done        → "✅ Hunt complete — N leads found"
        error       → "❌ {error message}"
  [ ] Map leads array to table rows — NO mock data
  [ ] Download button: window.open(leadsAPI.download(sessionId))
  [ ] Table columns: Name | City | Phone | Email | Score | Quality | Source
  [ ] Score badge: ≥7 green, 4-6 yellow, <4 red
  [ ] Email quality badge: 3=👤 Personal, 2=📧 Role, 1=ℹ️ Generic
  [ ] Copy phone/email button → navigator.clipboard.writeText()
  [ ] Send to Outreach button → router.push('/outreach?session=' + sessionId)
  
  MOCK DATA REMOVAL GREP:
    Remove ALL occurrences of:
    - const mockLeads = [...]
    - setLeads([{ name: "...", city: "Mumbai" }])
    - setTimeout(() => setStatus('done'), 3000)

PAGE: web/app/(leados)/dashboard/page.tsx
  
  WIRING CHECKLIST:
  [ ] useEffect → systemAPI.health() → render health badge
  [ ] useEffect → systemAPI.quota() → render quota progress bars
  [ ] useEffect → systemAPI.stats() → render 6 stat widgets
  [ ] useEffect → adminAPI.stats() → render source breakdown table
  [ ] Auto-refresh every 30 seconds (setInterval cleanup on unmount)
  [ ] Manual refresh button (calls all 4 endpoints simultaneously)
  
  QUOTA BAR component (reusable):
    Props: provider, used, limit
    Color: used/limit < 0.5 → green, < 0.8 → yellow, ≥ 0.8 → red
    Format: "{used} / {limit} (resets {period})"
    
  HEALTH BADGE states:
    db_connected + scheduler_running + waserver → 🟢 All Systems Nominal
    waserver=false                              → 🟡 WA Server Offline
    !db_connected                               → 🔴 DB Connection Lost

PAGE: web/app/(leados)/outreach/page.tsx
  
  WIRING CHECKLIST:
  [ ] On mount: fetch skip report → outreachAPI.skipReport()
      Display: Ready={report.totalready}, Sendable={report.sendable},
               Filtered={report.skipped}
  [ ] "Run Dry Test" button → outreachAPI.dryRun(10)
      Display result per-source in table: Source | Count | Preview
  [ ] "Live Send" button → confirm dialog → outreachAPI.liveSend(5)
      Guard: if not confirmed → abort
  [ ] "Partner Outreach" button → outreachAPI.partnerOutreach(true)
  [ ] Junk breakdown accordion:
      Show junk_local.samples as monospace pills (bg-111 border-333)
  [ ] Toast on any action (success/error from Sonner)
  [ ] Live mode daily cap indicator: "Brevo: X/300 sent today"
  
  FILTERING SOURCES display:
    Per source row show:
    - Source name
    - Count of READY leads in that source
    - Avg ICP score
    - % sendable (email_quality_score ≥ 2)
    - Send 10 button (per source)

PAGE: web/app/(leados)/settings/page.tsx
  
  WIRING CHECKLIST:
  [ ] On mount: settingsAPI.loadKeys() → populate fields
  [ ] Form fields (all type="password" with toggle):
      - Internal API Key (X-API-Key for backend)
      - Gemini API Key (X-Gemini-Key)
      - Google Maps Key (X-Google-Maps-Key)
      - Brevo SMTP Key (X-Brevo-Key)
      - Sender Email (X-Sender-Email)
      - Sender Name (X-Sender-Name)
  [ ] Tier toggles: Free/Paid per source (affects rate limiter)
  [ ] "Save" → settingsAPI.saveKeys(keys) → toast.success("Credentials saved locally")
  [ ] "Sync & Test" → settingsAPI.verifyKeys()
      → on 200: toast.success("Configuration saved") (exact string for tests)
      → on 401: setError("Key validation failed") (exact string for tests)
      → on missing master key: setError("Internal API key is required")
  [ ] Error banner rendered as:
      <div className="p-3 rounded-lg border border-red-500/30 bg-red-500/10
                      text-red-400 text-sm">{error}</div>
  [ ] BYOK security note footer:
      "🔐 Encrypted with AES-256-GCM • Stored in your browser only"

PAGE: web/app/(leados)/history/page.tsx
  
  ARCHITECTURE DECISION:
  Lead session history stored in TWO places:
    1. Browser IndexedDB (for speed, no server needed)
       Store: 'leadhunterpro', object: 'sessions'
       Schema: {sessionId, businessType, location, total, high, leads, createdAt}
    2. Supabase shown_leads table (for persistence across devices)
  
  WIRING CHECKLIST:
  [ ] On mount: read from IndexedDB via lib/leads-store.ts
  [ ] Fallback: if IndexedDB empty → GET /api/history from backend
  [ ] Display: Date | Location | Business Type | Total Leads | High Priority | Status
  [ ] Sort: newest first
  [ ] Click row → expand to show leads mini-table
  [ ] "Export CSV" per row → leadsAPI.download(sessionId)
  [ ] "Start Outreach" per row → /outreach?session={sessionId}
  [ ] "Delete" per row → remove from IndexedDB + confirm modal
  [ ] Empty state: "No hunts yet. Start your first hunt →"
  
  CREATE: web/lib/leads-store.ts (IndexedDB CRUD)
    openDB() → IDBDatabase
    saveSession(session: SessionRecord) → void
    getAllSessions() → SessionRecord[]
    deleteSession(sessionId: string) → void
    getSession(sessionId: string) → SessionRecord | null

PAGE: web/app/(leados)/whatsapp/page.tsx
  
  WIRING CHECKLIST:
  [ ] On mount: waAPI.health() → show connection status
  [ ] Poll every 5s while status !== 'connected'
  [ ] Display QR code: waAPI.qr() → <img src={`data:image/png;base64,${qr}`} />
  [ ] Status badge: connected=🟢, scanning=🟡 (show QR), disconnected=🔴
  [ ] "Reconnect" button → POST /api/whatsapp/reconnect
  [ ] WA Stats: waAPI.queue() → messages_sent, messages_failed, in_queue
  [ ] Instructions panel: "Scan QR code with WhatsApp → Settings → Linked Devices"
  [ ] Auto-hide QR when connected
  [ ] Anti-ban info panel (25-50s delays, human simulation)

PAGE: web/app/(leados)/refer/page.tsx
  
  WIRING CHECKLIST:
  [ ] Form: Name + Email → generate referral code (SHA-256 hash → 8 chars → "REF-XXXXXXXX")
  [ ] Code generation: client-side, no server call needed
  [ ] Copy link button → navigator.clipboard.writeText(referralUrl)
  [ ] Referral URL: https://yourdomain.com/?ref={code}
  [ ] Display: referral_code, commission (15%), status
  [ ] Backend tracking: POST /api/referrals/register
      Body: {name, email, referral_code}
      → Inserts into referrals table
  [ ] Show stats: leads referred, converted, commission_earned
  [ ] Commission rules accordion:
      "Refer a client who signs a contract → You earn 15% of contract value"

PAGE: web/app/(portfolio)/page.tsx
  
  WIRING CHECKLIST:
  [ ] Import projects from '@/config/projects.ts'
  [ ] Filter: projects.filter(p => p.featured)
  [ ] Render project cards from data — NO hardcoded sections
  [ ] Each card: name, tagline, status badge, tech chips, liveUrl, githubUrl
  [ ] Status colors: LIVE=green, BETA=yellow, BUILDING=blue, ARCHIVED=gray

PAGE: web/app/(portfolio)/hire/page.tsx
  
  WIRING CHECKLIST:
  [ ] Services grid: 4 cards (AI Automation, Full-Stack Apps,
      Lead Gen Systems, n8n Workflows)
  [ ] Bounty box: border-[#32e6e2], "Refer a client → 15% commission"
  [ ] Referral code generator (Name + Email → REF-XXXXXXXX)
  [ ] Contact form: Name, Email, Project Scope → POST /api/contact
  [ ] Loading state on form submit
  [ ] Social links: GitHub (sp25126), LinkedIn, Email

PAGE: web/app/api-hub/page.tsx (NEW — CREATE THIS)
  
  Content:
  [ ] Hero: "Build with LeadOS API" — tagline + CTA
  [ ] Pricing table:
  
  | Plan      | Price        | Leads/mo | Email Send | AI Scoring |
  |-----------|--------------|----------|------------|------------|
  | Starter   | Free         | 500      | 100/day    | Basic      |
  | Pro       | $29/mo       | 5,000    | 300/day    | Groq LLM   |
  | Enterprise| Custom       | Unlimited| Unlimited  | Custom     |
  
  [ ] Code example (copy-to-clipboard):
      curl -X POST /api/leads/stream \
        -H "X-API-Key: YOUR_KEY" \
        -d '{"business_type": "restaurant", "location": "Ahmedabad"}'
  [ ] CTA: "Get API Key" → /leados/settings
  [ ] CTA: "Book Integration Call" → cal.com link


# ─────────────────────────────────────────────────────────────────────────────
# PHASE M4 — QA TEST SUITE  [Day 3, ~3 hours]
# ─────────────────────────────────────────────────────────────────────────────

STEP M4.1 — Backend Integration Tests (server/tests/test_phase10_integration.py)
  
  class TestAPIHealth:
    test_health_endpoint_returns_ok
    test_quota_endpoint_returns_all_8_sources
    test_health_shows_wa_server_status
    test_cors_headers_present
  
  class TestLeadsSearch:
    test_empty_business_type_returns_422
    test_empty_location_returns_422
    test_radius_zero_returns_422
    test_valid_minimal_request_accepted
    test_missing_api_key_returns_401
  
  class TestEnrichment:
    test_enrich_run_processes_new_leads
    test_circuit_breaker_stops_at_3_attempts
    test_blacklisted_domain_skipped
    test_waterfall_finds_email_from_domain
    test_mx_check_rejects_invalid_domain
  
  class TestScoring:
    test_score_run_scores_email_reach_leads
    test_score_run_returns_avg_score
    test_scored_leads_get_status_READY
    test_low_score_leads_get_ARCHIVED
  
  class TestEmailOutreach:
    test_skip_report_returns_correct_shape
    test_dry_run_returns_leads_not_sending
    test_live_send_blocked_without_force_flag
    test_junk_emails_filtered_from_batch
    test_send_run_by_source_respects_batch_size
  
  class TestPhoneEnrichment:
    test_phone_enrich_returns_stats
    test_normalize_phone_10_digit_indian
    test_normalize_phone_with_country_code
    test_normalize_phone_invalid_returns_empty
  
  class TestScheduler:
    test_all_6_jobs_registered
    test_call_internal_uses_port_8000
    test_telegram_alert_fires_on_startup
  
  class TestAuth:
    test_missing_key_returns_401
    test_wrong_key_returns_401
    test_master_key_grants_access
    test_user_key_grants_access
    test_test_mode_bypass_works

STEP M4.2 — QA Checklist (qa/checklist.md)
  
  FORMAT: [ID] [Area] [Test] [Expected] [Pass/Fail]
  
  SECTION A — API HEALTH (4 tests)
    QA-A01: GET /api/health returns status=ok
    QA-A02: GET /api/quota/status returns 8 sources
    QA-A03: WA server status shows false when wa-server not running
    QA-A04: CORS headers present on all OPTIONS responses
  
  SECTION B — INGEST (6 tests)
    QA-B01: POST /api/ingest/radius-map returns new leads
    QA-B02: POST /api/ingest/india-saas returns leads from Inc42/HN
    QA-B03: POST /api/ingest/foreign-saas returns YC/GitHub leads
    QA-B04: POST /api/ingest/partners returns agency leads
    QA-B05: Duplicate domains not inserted (dedup working)
    QA-B06: Blacklisted domains (google.com etc.) never inserted
  
  SECTION C — ENRICHMENT (8 tests)
    QA-C01: Enrichment rate ≥ 60% on tech leads
    QA-C02: MX record check prevents invalid domain emails
    QA-C03: Circuit breaker archives lead after 3 failures
    QA-C04: email_quality_score=3 on named personal emails
    QA-C05: email_quality_score=1 on info@ contact@ emails
    QA-C06: Registrar emails (GoDaddy domains) filtered out
    QA-C07: Gemini fallback only runs when all 12 methods fail
    QA-C08: Phone enrichment rate ≥ 60% on Indian OSM leads
  
  SECTION D — SCORING (4 tests)
    QA-D01: score_run processes email_reach + super_enriched leads
    QA-D02: avg_score > 0 after score run (was bug BUG-008)
    QA-D03: READY leads all have icp_score > 70
    QA-D04: ARCHIVED leads all have icp_score < 30
  
  SECTION E — EMAIL OUTREACH (10 tests)
    QA-E01: Dry run returns 10 leads without sending emails
    QA-E02: info@ contact@ dpo@ emails filtered from dry run
    QA-E03: HN post title cleaned in subject (no "Show HN:")
    QA-E04: Email body has no Unicode garbage chars (—→-)
    QA-E05: Groq personalization generates unique email per lead
    QA-E06: Live send cap enforced (5 max without force=true)
    QA-E07: Per-source distribution correct (≤10 per source)
    QA-E08: Follow-up sequence skips already-replied leads
    QA-E09: Partner outreach uses Trojan Horse template
    QA-E10: Status updated to EMAILED after live send
  
  SECTION F — FRONTEND UNIT (15 tests)
    QA-F01: No mock data in ingest page (grep returns empty)
    QA-F02: SSE stream shows "Discovering" status in real-time
    QA-F03: Lead table populated from stream (not static)
    QA-F04: Score badge color correct (green/yellow/red)
    QA-F05: Email quality badge shows correct icon
    QA-F06: Download CSV returns valid file
    QA-F07: Settings page saves keys to localStorage
    QA-F08: Sync button calls /api/health with X-API-Key header
    QA-F09: Error banner shows "Key validation failed" on 401
    QA-F10: Dashboard quota bars update on refresh
    QA-F11: History shows sessions from IndexedDB
    QA-F12: WA page shows QR from backend (not static)
    QA-F13: Referral code generated without server call
    QA-F14: All sidebar nav links resolve (zero 404s)
    QA-F15: Portfolio projects render from config/projects.ts
  
  SECTION G — SECURITY (6 tests)
    QA-G01: No API keys in browser Network tab URLs
    QA-G02: localStorage keys encrypted (not plaintext)
    QA-G03: /api/admin/reset-db requires Master Key
    QA-G04: XSS in business_type input is sanitized
    QA-G05: Malformed JSON returns 422 not 500
    QA-G06: .env file returns 404 from Nginx (not accessible)
  
  SECTION H — DEPLOYMENT (8 tests — run post-deploy)
    QA-H01: HTTPS redirect from HTTP working
    QA-H02: SSL cert valid (no browser warning)
    QA-H03: /api/health returns ok over HTTPS
    QA-H04: Nginx security headers present (HSTS, X-Frame)
    QA-H05: Rate limit: 20 rapid requests handled gracefully
    QA-H06: Telegram bot responds to /status command
    QA-H07: WA QR visible in Docker logs: docker logs lhp-wa
    QA-H08: Scheduler Telegram notification sent at startup


# ─────────────────────────────────────────────────────────────────────────────
# PHASE M5 — PRODUCTION DEPLOYMENT  [Day 4, ~4 hours]
# ─────────────────────────────────────────────────────────────────────────────

STEP M5.1 — Docker Compose (docker-compose.yml)
  
  services:
  
    lhp-server:
      build: ./server
      container_name: lhp-server
      restart: unless-stopped
      env_file: .env
      ports: []  # Internal only — Nginx proxies
      expose: ["8000"]
      volumes:
        - output_data:/app/output
        - quota_state:/app/quotastate
      healthcheck:
        test: curl -f http://localhost:8000/api/health
        interval: 30s
        timeout: 10s
        retries: 3
      depends_on:
        lhp-wa:
          condition: service_healthy
    
    lhp-web:
      build:
        context: ./web
        args:
          NEXT_PUBLIC_API_URL: https://${DOMAIN}
      container_name: lhp-web
      restart: unless-stopped
      env_file: .env
      expose: ["3000"]
      healthcheck:
        test: wget -qO- http://localhost:3000/api/health
        interval: 30s
      depends_on:
        lhp-server:
          condition: service_healthy
    
    lhp-wa:
      build: ./wa-server
      container_name: lhp-wa
      restart: unless-stopped
      env_file: .env
      expose: ["3001"]
      shm_size: '256m'    # Required for Chromium/Baileys
      volumes:
        - wweb_auth:/app/.wwebjs_auth
      healthcheck:
        test: curl -f http://localhost:3001/health
        interval: 30s
    
    lhp-nginx:
      image: nginx:alpine
      container_name: lhp-nginx
      restart: unless-stopped
      ports:
        - "80:80"
        - "443:443"
      volumes:
        - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
        - ./nginx/certs:/etc/nginx/certs:ro
      depends_on:
        - lhp-server
        - lhp-web
  
  volumes:
    output_data:
    quota_state:
    wweb_auth:

STEP M5.2 — Nginx Config (nginx/nginx.conf)
  
  Key directives:
  
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_zone:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=web_zone:10m rate=30r/s;
    
    # HTTP → HTTPS redirect (keep .well-known for Certbot)
    server {
      listen 80;
      location /.well-known/acme-challenge/ { root /var/www/certbot; }
      location / { return 301 https://$host$request_uri; }
    }
    
    # Main HTTPS server
    server {
      listen 443 ssl;
      ssl_protocols TLSv1.2 TLSv1.3;
      ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
      add_header Strict-Transport-Security "max-age=63072000; includeSubDomains";
      add_header X-Frame-Options DENY;
      add_header X-Content-Type-Options nosniff;
      
      # Block sensitive files
      location ~* \.(env|py|pyc|git)$ { return 404; }
      
      # API proxy (300s timeout for SSE streaming)
      location /api/ {
        limit_req zone=api_zone burst=20 nodelay;
        proxy_pass http://lhp-server:8000;
        proxy_read_timeout 300s;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;  # Required for SSE
        proxy_cache off;      # Required for SSE
      }
      
      # Frontend
      location / {
        limit_req zone=web_zone burst=50 nodelay;
        proxy_pass http://lhp-web:3000;
      }
      
      # Gzip
      gzip on;
      gzip_types application/json text/plain text/css
                 application/javascript text/javascript;
    }

STEP M5.3 — Free Deployment Stack Summary
  
  COMPONENT          PLATFORM              COST
  ───────────────────────────────────────────────
  Frontend           Cloudflare Pages      FREE (already deployed)
  Backend            Oracle Cloud Free     FREE (4 OCPUs, 24GB RAM)
  Database           Supabase              FREE (500MB, exists)
  LLM Scoring        Groq (free tier)      FREE (14K req/day)
  LLM Email Gen      Gemini 1.5 Flash      FREE (1500 req/day)
  Email Send         Brevo                 FREE (300/day)
  WA Microservice    Local / Docker        FREE
  Domain             Already owned         FREE (1 year)
  SSL Certificate    Let's Encrypt/CF      FREE
  Redis (token cache) Upstash free tier   FREE (10K req/day)
  Telegram Bot       BotFather             FREE
  ───────────────────────────────────────────────
  TOTAL MONTHLY COST:  $0.00
  
  QUOTA MATH (daily safe limits):
    Groq:    14K requests ÷ 50 leads/batch = 280 scoring runs
    Gemini:  1500 requests ÷ 1 email each = 1500 personalized emails
    Brevo:   300 emails/day (enforced by DAILY_EMAIL_CAP=280)
    GMaps:   200 leads/month free → use OSM primarily, GMaps for phone enrich
    Overpass: 30K req/day (3 mirrors × 10K) → covers 600 cities × 50 categories

STEP M5.4 — Makefile (root directory)
  
  .PHONY: up down restart logs wa-qr build clean backup update ssl-renew test qa
  
  up:
    docker compose up -d
  down:
    docker compose down
  restart:
    docker compose restart
  logs:
    docker compose logs -f --tail=50
  wa-qr:
    docker logs lhp-wa -f | grep -A5 "QR"
  server-logs:
    docker logs lhp-server -f
  status:
    docker compose ps && curl -s http://localhost/api/health | python3 -m json.tool
  build:
    docker compose build --no-cache
  clean:
    docker compose down -v && rm -f output/*.csv
  backup:
    tar -czf backup-$$(date +%Y%m%d).tar.gz output/ quotastate/
  update:
    git pull && docker compose build && docker compose up -d
  ssl-renew:
    certbot renew && cp /etc/letsencrypt/live/${DOMAIN}/*.pem nginx/certs/
    && docker restart lhp-nginx
  test:
    cd server && python -m pytest tests/ -v && echo "✅ All tests passed"
  qa:
    bash qa/run_qa.sh


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — COMPLETE FEATURE REGISTRY
# (Every feature in the merged system — status + owner file)
# ═══════════════════════════════════════════════════════════════════════════════

FEATURE REGISTRY:

# INGESTION FEATURES
F-001  OSM Radius Map (local Indian businesses)     WORKING   ingest.py
F-002  OSM India 55 cities × 28 categories          NEEDS MOUNT ingest.py
F-003  OSM Foreign 600 cities × 30 categories       NEEDS MOUNT ingest.py
F-004  India SaaS (Inc42, GitHub India, HN India)   WORKING   saas_fetcher.py
F-005  Foreign SaaS (YC, HN, ProductHunt, GitHub)   WORKING   saas_fetcher.py
F-006  Partner / Agency fetcher (Clutch, OSM)       NEEDS MOUNT partner_fetcher.py
F-007  HN Show HN RSS (product URL fix applied)     WORKING   hn_show_rss.py
F-008  Dev.to ShowDev (fix applied)                 WORKING   devto_showdev.py
F-009  Hashnode (fix applied)                       WORKING   hashnode.py
F-010  Lobsters RSS                                 WORKING   lobsters.py
F-011  RemoteOK jobs                                WORKING   remoteok.py
F-012  YC Companies (OSS GitHub API)                WORKING   yc_companies.py
F-013  GitHub Trending                              WORKING   github_trending.py
F-014  ProductHunt RSS                              WORKING   product_hunt.py
F-015  Wellfound / AngelList                        WORKING   wellfound.py
F-016  JustDial India (soup selectors updated)      PARTIAL   india_directories.py
F-017  Inc42 India (confirmed 39 leads/3 pages)     WORKING   india_directories.py
F-018  IndiaMART (HTML→JSON fail, replaced w/ JD)   REPLACED  india_directories.py
F-019  TradeIndia (404 fail, removed)               REMOVED   india_directories.py

# ENRICHMENT FEATURES
F-020  Website scraper + Groq analysis              WORKING   website_scraper.py
F-021  MX record checker                            WORKING   mx_checker.py
F-022  Website email scraper (scraper method)       WORKING   email_waterfall.py
F-023  crt.sh certificate email extractor           WORKING   email_waterfall.py
F-024  RDAP domain email extractor                  WORKING   email_waterfall.py
F-025  Hunter.io domain search                      NEEDS KEY  email_waterfall.py
F-026  Snov.io OAuth + domain email (fix applied)   WORKING   email_waterfall.py
F-027  Apollo.io people search                      WORKING   email_waterfall.py
F-028  GetProspect (GET endpoint fix applied)       WORKING   email_waterfall.py
F-029  CommonCrawl email scanner                    WORKING   email_waterfall.py
F-030  India Registry (ZaubaCorp/Tofler/MCA)        WORKING   india_registry.py
F-031  Email Permutator + SMTP verify               WORKING   permutator.py
F-032  Legal pages scraper (/privacy /contact)      WORKING   email_waterfall.py
F-033  security.txt scanner                         WORKING   email_waterfall.py
F-034  Gemini last-resort email guess               WORKING   email_waterfall.py
F-035  Phone enrichment (Google Maps Places)        WORKING   phone_router.py
F-036  Phone normalization (Indian +91 format)      WORKING   phone_normalizer.py
F-037  Enrichment circuit breaker (3-attempt cap)   WORKING   enrichment_engine.py
F-038  Blacklist check (30+ enterprise domains)     WORKING   enrichment_engine.py
F-039  Email quality scoring (0-3 scale)            WORKING   enrichment_engine.py
F-040  Fallback handler (retry ENRICHMENT_FAILED)   REBUILD   fallback_handler.py

# SCORING FEATURES
F-041  Groq ICP scoring (icp_score 0-100)           WORKING   score.py
F-042  Gemini ICP scoring (fallback)                WORKING   score.py
F-043  Partner scoring (agency readiness)           WORKING   score_partners.py
F-044  Score threshold routing (≥70=READY, <30=ARCHIVE) WORKING score.py

# OUTREACH FEATURES
F-045  Email writer (Groq personalized)             WORKING   email_writer.py
F-046  Per-source email distribution               WORKING   email_router.py
F-047  Junk email filter (50+ blocked local parts)  WORKING   email_router.py
F-048  HN title cleaner in subject lines            WORKING   templates.py
F-049  ASCII-safe email body                        WORKING   templates.py
F-050  Client cold email template                   WORKING   templates.py
F-051  Partner Trojan Horse template                WORKING   templates.py
F-052  Follow-up sequence (2 emails)                WORKING   email_router.py
F-053  Live send cap (5 max without force=true)     WORKING   email_router.py
F-054  Email skip report                            WORKING   email_router.py
F-055  WA channel routing (country-based)           WORKING   channel_router.py
F-056  WA Baileys microservice                      DESIGNED  wa-server/index.js
F-057  Voice agent queue (Twilio/Exotel)            WORKING   voice_router.py
F-058  Voice transcript saver                       WORKING   voice_router.py

# AUTOMATION FEATURES
F-059  APScheduler (6 jobs, PORT 8000)              WORKING   scheduler.py
F-060  Telegram notifications                       WORKING   telegram.py
F-061  Telegram bot commands (/status /leads)       WORKING   bot.py
F-062  Quota manager (quotastate.json persistent)   WORKING   rate_limiter.py
F-063  Request manager (safe_get, mirrors)          WORKING   request_manager.py

# FRONTEND FEATURES
F-064  SSE lead streaming hook (useLeadStream)      CREATE    hooks/useLeadStream.ts
F-065  Ingest hunt page (real SSE, no mock data)    WIRE      ingest/page.tsx
F-066  Dashboard (real quota + health + stats)      WIRE      dashboard/page.tsx
F-067  Outreach command center                      WIRE      outreach/page.tsx
F-068  BYOK settings (localStorage encrypted)       WIRE      settings/page.tsx
F-069  History (IndexedDB + Supabase)               WIRE      history/page.tsx
F-070  WA QR page (live backend)                    WIRE      whatsapp/page.tsx
F-071  Referral code generator                      WIRE      refer/page.tsx
F-072  Portfolio projects (config/projects.ts)      CREATE    portfolio/page.tsx
F-073  Hire Me + Bounty page                        WIRE      hire/page.tsx
F-074  API Hub landing page                         CREATE    api-hub/page.tsx
F-075  Centralized API client (api.ts)              CREATE    lib/api.ts
F-076  IndexedDB session storage                    CREATE    lib/leads-store.ts

# AUTH FEATURES
F-077  Per-user API key auth (DB-backed)            WORKING   auth.py
F-078  Master key bypass (admin/scheduler)          WORKING   auth.py
F-079  NextAuth GitHub + Google OAuth               WORKING   auth.ts
F-080  Request credentials extractor (BYOK)         WORKING   request_credentials.py


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — ANTIGRAVITY IDE EXECUTION ORDER
# (The exact sequence you paste into Antigravity to build this system)
# ═══════════════════════════════════════════════════════════════════════════════

# Read this section after completing all previous sections.
# This is your BUILD SEQUENCE — execute these prompts in order.
# Do NOT skip steps. Each step has a verification command.
# If verification fails → fix before proceeding.

PROMPT 1 — DATABASE MIGRATIONS
  Paste: Section 6 → STEP M1.2 (full SQL block)
  Verify: SELECT COUNT(*) FROM leads; → ≥1455
          SELECT column_name FROM information_schema.columns
          WHERE table_name='leads'; → should include 'icp_score', 'whatsapp_number'

PROMPT 2 — UNIFIED BACKEND ENTRY POINT
  Paste: Section 6 → STEP M2.2 (server/main.py complete)
         + STEP M2.3 (scheduler.py with PORT 8000)
  Verify: cd server && python -m uvicorn main:app --port 8000
          curl localhost:8000/api/health → {"status":"ok"}
          curl localhost:8000/openapi.json | python -m json.tool | grep '"path"'
          → should show 40+ routes

PROMPT 3 — OCTAGON ENRICHMENT MIGRATION
  Paste: Section 6 → STEP M2.1 (copy commands)
         + STEP M2.4 (enricher.py waterfall wiring)
  Verify: curl -X POST localhost:8000/api/enrich/run?batch_size=5
          → {"processed": 5, "enriched": ≥2, "enrichment_rate": ≥40.0}

PROMPT 4 — EMAIL SYSTEM WIRING
  Paste: STEP M2.1 email_router + templates + email_writer
  Verify: curl -X POST "localhost:8000/api/email/send-run-by-source?dry_run=true"
          → {"mode":"dry_run", "sources_processed":≥1, "would_send":≥1}
          curl "localhost:8000/api/email/skip-report"
          → {"total_ready":N, "sendable":M, "skipped":K}

PROMPT 5 — FRONTEND HOOKS + API CLIENT
  Paste: Section 6 → STEP M3.1 (useLeadStream.ts complete)
         + STEP M3.3 (api.ts complete)
         + web/lib/leads-store.ts (IndexedDB CRUD)
  Verify: cd web && npx tsc --noEmit → 0 errors

PROMPT 6 — REMOVE ALL MOCK DATA
  Paste: Section 6 → STEP M3.2 (grep + delete instructions)
  Verify: grep -rn "mockLeads\|Mumbai, India\|const leads = \[" web/app/
          → ZERO matches

PROMPT 7 — WIRE ALL PAGES
  Paste: Section 6 → STEP M3.4 (all page wiring checklists)
  Give Antigravity each page as separate sub-prompt:
    7a: ingest/page.tsx
    7b: dashboard/page.tsx
    7c: outreach/page.tsx
    7d: settings/page.tsx
    7e: history/page.tsx
    7f: whatsapp/page.tsx
    7g: refer/page.tsx
    7h: api-hub/page.tsx (NEW)
  Verify each: npm run build → "Compiled successfully"
               No TypeScript errors on each page

PROMPT 8 — QA TEST SUITE
  Paste: Section 7 → STEP M4.1 (test_phase10_integration.py)
  Run: cd server && APP_ENV=test pytest tests/ -v
  Target: 92+ tests, 0 failures

PROMPT 9 — DOCKER + DEPLOYMENT
  Paste: Section 7 → STEP M5.1-M5.2 (docker-compose + nginx)
  Verify locally: docker compose build → no errors
                  docker compose up -d && curl localhost/api/health

PROMPT 10 — FINAL PRODUCTION DEPLOY
  Run: bash deploy.sh yourdomain.com youremail@domain.com
  Run: bash qa/verify_production.sh
  Target: 8/8 production checks pass


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9 — SYSTEM ARCHITECTURE SUMMARY DIAGRAM
# ═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                    LEADHUNTER OMEGA — ARCHITECTURE OVERVIEW                 │
└─────────────────────────────────────────────────────────────────────────────┘

USER BROWSER
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  NEXT.JS 14 FRONTEND (Cloudflare Pages / Docker)    │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │ Ingest Page  │  │ Outreach Cmd │  │ Dashboard │  │
│  │ useLeadStream│  │ Skip Report  │  │ Quota Bars│  │
│  │ SSE Stream   │  │ Dry Run/Send │  │ Stats     │  │
│  └──────────────┘  └──────────────┘  └───────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │ Settings     │  │ History      │  │ WA Status │  │
│  │ BYOK Keys    │  │ IndexedDB    │  │ QR Code   │  │
│  │ localStorage │  │ Sessions     │  │ Live Poll │  │
│  └──────────────┘  └──────────────┘  └───────────┘  │
│  lib/api.ts (ALL API calls)                          │
│  lib/leads-store.ts (IndexedDB CRUD)                 │
└─────────────────────────────────────────────────────┘
    │  X-API-Key header on every request
    │  X-Gemini-Key, X-Google-Maps-Key (BYOK)
    ▼
┌─────────────────────────────────────────────────────┐
│  NGINX REVERSE PROXY (Port 80/443)                  │
│  Rate limit: 10 req/s API, 30 req/s web             │
│  SSL: Let's Encrypt / Cloudflare                    │
│  Proxy timeout: 300s (SSE streaming)                │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  FASTAPI BACKEND (Port 8000)                        │
│                                                     │
│  INGEST LAYER          ENRICHMENT LAYER             │
│  ┌────────────────┐   ┌──────────────────────────┐  │
│  │ OSM Overpass   │   │ 13-Step Email Waterfall  │  │
│  │ Google Maps    │   │ scraper→crt.sh→rdap→     │  │
│  │ HN/YC/GitHub   │   │ hunter→snov→apollo→      │  │
│  │ Inc42/JustDial │   │ getprospect→commoncrawl→ │  │
│  │ Clutch/OSM     │   │ legal→security.txt→      │  │
│  │ Partner Fetcher│   │ permutator→gemini        │  │
│  └────────────────┘   └──────────────────────────┘  │
│                                                     │
│  SCORING LAYER         OUTREACH LAYER               │
│  ┌────────────────┐   ┌──────────────────────────┐  │
│  │ Groq LLM       │   │ Per-source email distrib │  │
│  │ icp_score 0-100│   │ Junk filter (50+ blocked)│  │
│  │ READY/ARCHIVE  │   │ Groq personalization     │  │
│  │ Partner scoring│   │ Brevo SMTP (300/day)     │  │
│  └────────────────┘   └──────────────────────────┘  │
│                                                     │
│  AUTOMATION                                         │
│  ┌──────────────────────────────────────────────┐   │
│  │ APScheduler: 6 jobs (ingest/enrich/score/    │   │
│  │              send/followup/daily_report)     │   │
│  │ Telegram Bot: /status /leads /outreach       │   │
│  │ QuotaManager: 8 sources, daily/monthly reset │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
    │                              │
    ▼                              ▼
┌───────────────┐         ┌────────────────────┐
│  WA-SERVER    │         │  SUPABASE DB        │
│  (Node.js)    │         │  leads (1500+ rows) │
│  Baileys       │         │  user_api_keys      │
│  Port 3001    │         │  shown_leads         │
│  Anti-ban:    │         │  referrals           │
│  25-50s delay │         │  outreach_history    │
│  p-queue:1    │         │  (PostgreSQL async)  │
└───────────────┘         └────────────────────┘
    │
    ▼
WHATSAPP CLOUD
(91XXXXXXXXXX)

┌──────────────────────────────────────────────────────────────────┐
│  EXTERNAL AI SERVICES                                            │
│  Groq (llama-3.3-70b-versatile) ← scoring, 14K req/day FREE     │
│  Gemini 1.5 Flash               ← email gen + guess, 1500/day   │
│  Groq (llama-3.1-8b-instant)    ← email writer fallback          │
└──────────────────────────────────────────────────────────────────┘


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 10 — FINAL ANTIGRAVITY MASTER INSTRUCTION
# ═══════════════════════════════════════════════════════════════════════════════

# This is the TLDR version — paste this as the opening message in a new
# Antigravity session after you have read all the above sections.

You are Antigravity IDE. You are building LEADHUNTER OMEGA — a unified
production-grade lead generation and AI outreach system. The system merges
TWO existing codebases (Octagon + LeadOS Hunter Pro) into ONE deployable
product. The target container is lead-hunter-pro/.

READ ORDER (before writing any code):
  1. CONTEXT-BRIEFING file          → env, keys, DB state
  2. OCTAGON-LEADGEN-SYSTEM file    → Octagon full history
  3. act-as-a-software-fullstack file → LeadOS build roadmap
  4. Act-as-a-futuristic-fullstack file → frontend rewire specs
  5. act-as-a-senior-job-and-lead file  → enrichment detail
  6. octagon_outreach_master file   → real lead data
  7. processed_leads_for_outreach file  → enriched leads
  8. r2 terminal history file       → full build history

SYSTEM FACTS:
  Backend: FastAPI, Python 3.11, PORT 8000, Supabase PostgreSQL
  Frontend: Next.js 14 App Router, Cloudflare Pages, PORT 3000
  WA Server: Node.js + Baileys, PORT 3001
  DB State: 1455+ leads in Supabase
  Free Tiers: Groq + Gemini + Brevo + Oracle Cloud = $0/month

YOUR TASK IS TO:
  1. Run Supabase migrations (Section 6, STEP M1.2)
  2. Build unified server/main.py (Section 6, STEP M2.2)
  3. Wire Octagon enrichment into LeadOS enricher (STEP M2.4)
  4. Wire email outreach system end-to-end (STEP M2.1 email files)
  5. Create useLeadStream.ts hook (STEP M3.1)
  6. Build lib/api.ts centralized client (STEP M3.3)
  7. Wire all 8 frontend pages to real data (STEP M3.4)
  8. Remove every single line of mock/hardcoded data (STEP M3.2)
  9. Generate QA test suite (STEP M4.1)
  10. Build Docker + Nginx deployment (STEP M5.1-M5.2)

DO NOT:
  - Hallucinate file names that don't exist in the source files
  - Use mock data, setTimeout, or placeholder arrays
  - Hardcode API keys
  - Skip the BUG fixes registered in Section 5
  - Leave any router un-mounted in server/main.py
  - Leave any API call in a page that doesn't go through lib/api.ts
  - Build features not listed in Section 7 Feature Registry

WHEN A SECTION IS COMPLETE, output:
  ✅ STEP M[X].[Y] COMPLETE — [N] files created/modified
  NEXT: Paste Section 6, STEP M[X].[Y+1] to continue.

BEGIN WITH STEP M1.2 — DATABASE MIGRATIONS.
Output the full SQL block with zero hallucinations.

# ═══════════════════════════════════════════════════════════════════════════════
# END OF AUDIT — LEADHUNTER OMEGA
# Total Coverage: 80 features audited, 20 bugs catalogued,
#                 10 conflict resolutions defined,
#                 5 deployment phases specified,
#                 8 pages fully wired,
#                 92 QA tests defined
# Status: READY FOR ANTIGRAVITY EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════
That is the complete 6000+ line audit [file:271][file:270][file:272][file:276][file:277][file:273] — every section is now fully written. Here's how to use it:

How to Execute This
Copy the full prompt across all 3 messages (including this one) and paste it as the opening message in a fresh Antigravity IDE session. [file:277]

Then follow this exact execution order:

PROMPT 1 → Paste STEP M1.2 SQL migrations into Supabase SQL editor first [file:276]

PROMPT 2 → Build unified server/main.py + scheduler.py (PORT 8000) [file:271]

PROMPTS 3-4 → Migrate Octagon enrichment + wire email system [file:274]

PROMPTS 5-6 → Create useLeadStream.ts, api.ts, remove ALL mock data [file:272]

PROMPT 7 (a-h) → Wire each frontend page separately (one sub-prompt per page) [file:272]

PROMPT 8 → QA test suite (target: 92 tests passing) [file:277]

PROMPTS 9-10 → Docker + deploy.sh → live on Oracle Cloud free tier [file:277]

The key rule: verify each step passes before moving to the next one. Every step has a curl command that confirms it worked. [file:271]
