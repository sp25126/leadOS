-- ============================================================
-- LeadHunter Omega — Migration v3
-- Run this in the Supabase SQL Editor
-- All operations are ADDITIVE (safe to re-run — uses IF NOT EXISTS)
-- ============================================================

-- 1. EXTEND leads table with missing Octagon columns
ALTER TABLE leads
  ADD COLUMN IF NOT EXISTS lead_type          VARCHAR      DEFAULT 'client',
  ADD COLUMN IF NOT EXISTS icp_score          INTEGER      DEFAULT 0,
  ADD COLUMN IF NOT EXISTS priority           VARCHAR      DEFAULT 'medium',
  ADD COLUMN IF NOT EXISTS reason             TEXT,
  ADD COLUMN IF NOT EXISTS pain_points        TEXT,
  ADD COLUMN IF NOT EXISTS suggested_opening  TEXT,
  ADD COLUMN IF NOT EXISTS whatsapp_number    VARCHAR,
  ADD COLUMN IF NOT EXISTS outreach_channel   VARCHAR      DEFAULT 'email',
  ADD COLUMN IF NOT EXISTS enrichment_tier    VARCHAR,
  ADD COLUMN IF NOT EXISTS email_quality_score INTEGER     DEFAULT 0,
  ADD COLUMN IF NOT EXISTS phone_source       VARCHAR,
  ADD COLUMN IF NOT EXISTS tech_hints         TEXT,
  ADD COLUMN IF NOT EXISTS social_media       TEXT,
  ADD COLUMN IF NOT EXISTS has_contact_form   BOOLEAN,
  ADD COLUMN IF NOT EXISTS has_website        BOOLEAN,
  ADD COLUMN IF NOT EXISTS website_live       BOOLEAN,
  ADD COLUMN IF NOT EXISTS hn_url             TEXT,
  ADD COLUMN IF NOT EXISTS partner_status     VARCHAR,
  ADD COLUMN IF NOT EXISTS referral_fee_pct   INTEGER      DEFAULT 20,
  ADD COLUMN IF NOT EXISTS referral_revenue   FLOAT        DEFAULT 0,
  ADD COLUMN IF NOT EXISTS emailed_at         TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS replied_at         TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS source_url         VARCHAR,
  ADD COLUMN IF NOT EXISTS archive_reason     VARCHAR(255),
  ADD COLUMN IF NOT EXISTS cross_check_score  INTEGER      DEFAULT 100,
  ADD COLUMN IF NOT EXISTS meta_data          JSONB        DEFAULT '{}';

-- 2. Migrate legacy status values to unified naming
UPDATE leads SET status = CASE
  WHEN email IS NOT NULL AND phone IS NOT NULL THEN 'super_enriched'
  WHEN email IS NOT NULL THEN 'email_reach'
  WHEN phone IS NOT NULL THEN 'phone_reach'
  ELSE 'NEW'
END
WHERE status IS NULL OR status NOT IN (
  'NEW', 'ENRICHING', 'ENRICHED', 'SCORED', 'PENDING_APPROVAL',
  'APPROVED', 'SENDING', 'SENT', 'EMAILED', 'REPLIED', 'CLOSED',
  'REJECTED', 'FAILED', 'BAD_EMAIL', 'NO_EMAIL', 'ENRICHMENT_FAILED',
  'email_reach', 'super_enriched', 'phone_reach', 'READY', 'ARCHIVED',
  'UNENRICHABLE'
);

-- 3. Create referrals table
CREATE TABLE IF NOT EXISTS referrals (
  id             UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
  referrer_name  VARCHAR(255),
  referrer_email VARCHAR(255),
  referral_code  VARCHAR(50)  UNIQUE NOT NULL,
  referred_user_id VARCHAR(255),
  status         VARCHAR(50)  DEFAULT 'pending',
  contract_value FLOAT        DEFAULT 0,
  commission_pct INTEGER      DEFAULT 15,
  commission_paid FLOAT       DEFAULT 0,
  created_at     TIMESTAMPTZ  DEFAULT NOW(),
  converted_at   TIMESTAMPTZ
);

-- 4. Create outreach_history table
CREATE TABLE IF NOT EXISTS outreach_history (
  id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id    UUID,
  channel    VARCHAR(50),
  subject    VARCHAR(500),
  body       TEXT,
  sent_at    TIMESTAMPTZ DEFAULT NOW(),
  opened_at  TIMESTAMPTZ,
  replied_at TIMESTAMPTZ,
  status     VARCHAR(50) DEFAULT 'sent'
);

-- 5. Create shown_leads table (LeadOS dedup)
CREATE TABLE IF NOT EXISTS shown_leads (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_hash     VARCHAR(64) UNIQUE NOT NULL,
  name          VARCHAR(255),
  city          VARCHAR(100),
  phone         VARCHAR(30),
  email         VARCHAR(255),
  source        VARCHAR(50),
  session_id    VARCHAR(100),
  shown_at      TIMESTAMPTZ DEFAULT NOW(),
  business_type VARCHAR(100),
  location      VARCHAR(100)
);

-- 6. Create user_api_keys table (LeadOS auth)
CREATE TABLE IF NOT EXISTS user_api_keys (
  id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           VARCHAR(255) UNIQUE NOT NULL,
  api_key_hash      VARCHAR(64)  UNIQUE NOT NULL,
  api_key_hint      VARCHAR(10),
  tier              VARCHAR(20)  DEFAULT 'starter',
  is_set            BOOLEAN      DEFAULT TRUE,
  created_at        TIMESTAMPTZ  DEFAULT NOW(),
  last_used_at      TIMESTAMPTZ,
  leads_this_month  INTEGER      DEFAULT 0,
  api_calls_today   INTEGER      DEFAULT 0,
  webhook_url       VARCHAR(500)
);

-- 7. Performance indexes
CREATE INDEX IF NOT EXISTS idx_leads_status        ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_source        ON leads(source);
CREATE INDEX IF NOT EXISTS idx_leads_icp_score     ON leads(icp_score DESC);
CREATE INDEX IF NOT EXISTS idx_leads_enrich        ON leads(enrich_attempts) WHERE status = 'NEW';
CREATE INDEX IF NOT EXISTS idx_shown_leads_hash    ON shown_leads(lead_hash);
CREATE INDEX IF NOT EXISTS idx_user_keys_hash      ON user_api_keys(api_key_hash);
CREATE INDEX IF NOT EXISTS idx_user_keys_user      ON user_api_keys(user_id);

-- Verify
SELECT
  COUNT(*) AS total_leads,
  COUNT(CASE WHEN icp_score > 0 THEN 1 END) AS scored,
  COUNT(CASE WHEN email IS NOT NULL THEN 1 END) AS with_email,
  COUNT(CASE WHEN phone IS NOT NULL THEN 1 END) AS with_phone
FROM leads;
