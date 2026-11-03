-- ====================================================================
-- GAADILELO.COM — Production Supabase / PostgreSQL Migration
-- Migration: 004_buyer_intent_and_auth.sql
-- Description: Buyer intent confirmations, auth tokens, indexes and RLS
-- ====================================================================

CREATE TABLE IF NOT EXISTS buyer_intent_confirmations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID NOT NULL REFERENCES buying_groups(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    purchase_timeline VARCHAR(50) NOT NULL,
    is_genuine_intent BOOLEAN NOT NULL DEFAULT TRUE,
    is_non_binding_acknowledged BOOLEAN NOT NULL DEFAULT TRUE,
    agreed_to_contact BOOLEAN NOT NULL DEFAULT TRUE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    confirmed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_buyer_intent_group ON buyer_intent_confirmations(group_id);
CREATE INDEX IF NOT EXISTS idx_buyer_intent_user ON buyer_intent_confirmations(user_id);

CREATE TABLE IF NOT EXISTS auth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_type VARCHAR(50) NOT NULL, -- PASSWORD_RESET, EMAIL_VERIFICATION
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_auth_tokens_user ON auth_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_type ON auth_tokens(token_type);

CREATE TABLE IF NOT EXISTS revoked_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    jti VARCHAR(64) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    revoked_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_revoked_tokens_jti ON revoked_tokens(jti);
CREATE INDEX IF NOT EXISTS idx_revoked_tokens_user ON revoked_tokens(user_id);

-- Supabase Row Level Security (RLS)
ALTER TABLE buyer_intent_confirmations ENABLE ROW LEVEL SECURITY;
ALTER TABLE auth_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE revoked_tokens ENABLE ROW LEVEL SECURITY;

-- Supabase Row Level Security (RLS) (Idempotent creation)
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'buyer_intent_user_access' AND tablename = 'buyer_intent_confirmations') THEN
        CREATE POLICY buyer_intent_user_access ON buyer_intent_confirmations
            FOR ALL USING (user_id = auth.uid());
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'auth_tokens_user_access' AND tablename = 'auth_tokens') THEN
        CREATE POLICY auth_tokens_user_access ON auth_tokens
            FOR ALL USING (user_id = auth.uid());
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'revoked_tokens_user_access' AND tablename = 'revoked_tokens') THEN
        CREATE POLICY revoked_tokens_user_access ON revoked_tokens
            FOR ALL USING (user_id = auth.uid());
    END IF;
END $$;

