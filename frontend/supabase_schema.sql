-- =============================================================================
-- SALEM (سالم) — Production Supabase Schema & Row-Level Security (RLS) Policies
-- =============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Smoking Profiles Table
CREATE TABLE IF NOT EXISTS public.smoking_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    tobacco_type TEXT NOT NULL DEFAULT 'cigarettes',
    tobacco_type_custom TEXT,
    daily_cigarettes INTEGER NOT NULL DEFAULT 15,
    pack_price_egp NUMERIC NOT NULL DEFAULT 65,
    last_smoked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    primary_triggers JSONB NOT NULL DEFAULT '[]'::jsonb,
    quit_goal TEXT NOT NULL DEFAULT 'تحسين صحتي واستعادة لياقتي',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.smoking_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own smoking profile"
    ON public.smoking_profiles FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own smoking profile"
    ON public.smoking_profiles FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own smoking profile"
    ON public.smoking_profiles FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own smoking profile"
    ON public.smoking_profiles FOR DELETE
    USING (auth.uid() = user_id);

-- 2. Conversations Table
CREATE TABLE IF NOT EXISTS public.conversations (
    id TEXT PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL DEFAULT 'محادثة مع سالم',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own conversations"
    ON public.conversations FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- 3. Messages Table
CREATE TABLE IF NOT EXISTS public.messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES public.conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    evidence JSONB,
    contract_state TEXT,
    grounded BOOLEAN DEFAULT false,
    safety_status TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can access messages of their conversations"
    ON public.messages FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.conversations c
            WHERE c.id = messages.conversation_id AND c.user_id = auth.uid()
        )
    );

-- 4. Quit Plans Table
CREATE TABLE IF NOT EXISTS public.quit_plans (
    id TEXT PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    status TEXT NOT NULL DEFAULT 'active',
    quit_start_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    daily_cigarettes_baseline INTEGER NOT NULL DEFAULT 15,
    pack_price_egp NUMERIC NOT NULL DEFAULT 65,
    tasks JSONB NOT NULL DEFAULT '[]'::jsonb,
    milestones JSONB NOT NULL DEFAULT '[]'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.quit_plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own quit plans"
    ON public.quit_plans FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- 5. Intervention Outcomes Table
CREATE TABLE IF NOT EXISTS public.intervention_outcomes (
    id TEXT PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    intervention_type TEXT NOT NULL,
    trigger TEXT,
    intensity_before INTEGER,
    intensity_after INTEGER,
    outcome TEXT,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ NOT NULL
);

ALTER TABLE public.intervention_outcomes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own intervention outcomes"
    ON public.intervention_outcomes FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- 6. User Settings & Preferences Table
CREATE TABLE IF NOT EXISTS public.user_settings (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    daily_reminders BOOLEAN DEFAULT true,
    craving_checkins BOOLEAN DEFAULT true,
    evidence_details BOOLEAN DEFAULT true,
    haptic_feedback BOOLEAN DEFAULT true,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own settings"
    ON public.user_settings FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Indexes for high-performance scoped querying
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON public.conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON public.messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_smoking_profiles_user_id ON public.smoking_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_quit_plans_user_id ON public.quit_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_interventions_user_id ON public.intervention_outcomes(user_id);
