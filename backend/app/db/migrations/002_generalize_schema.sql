-- ================================================================
-- AI Tutor — Generalize Schema for Phase A
-- Migration: 002_generalize_schema.sql
--
-- Adds explicit fields to the concepts table required by the
-- generalized curriculum architecture (Phase A, V0.1).
-- ================================================================

-- Add the new columns
ALTER TABLE concepts
ADD COLUMN IF NOT EXISTS board TEXT NOT NULL DEFAULT 'punjab',
ADD COLUMN IF NOT EXISTS grade INTEGER NOT NULL DEFAULT 10,
ADD COLUMN IF NOT EXISTS visual_need TEXT NOT NULL DEFAULT 'none',
ADD COLUMN IF NOT EXISTS language_pack JSONB NOT NULL DEFAULT '["ur", "en"]'::jsonb;

DO $$
BEGIN
    IF EXISTS(SELECT 1 FROM information_schema.columns 
              WHERE table_name='concepts' AND column_name='textbook_page') THEN
        ALTER TABLE concepts RENAME COLUMN textbook_page TO textbook_sources_temp;
        ALTER TABLE concepts ADD COLUMN IF NOT EXISTS textbook_sources JSONB NOT NULL DEFAULT '[]'::jsonb;
        UPDATE concepts
        SET textbook_sources = jsonb_build_array(textbook_sources_temp)
        WHERE textbook_sources_temp IS NOT NULL;
        ALTER TABLE concepts DROP COLUMN textbook_sources_temp;
    END IF;
END $$;
