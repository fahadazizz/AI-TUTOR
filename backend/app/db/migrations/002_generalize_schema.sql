-- ================================================================
-- AI Tutor — Generalize Schema for Phase A
-- Migration: 002_generalize_schema.sql
-- 
-- Adds explicit fields to the concepts table required by the
-- generalized curriculum architecture (Phase A, V0.1).
-- ================================================================

-- Add the new columns
ALTER TABLE concepts
ADD COLUMN board TEXT NOT NULL DEFAULT 'punjab',
ADD COLUMN grade INTEGER NOT NULL DEFAULT 10,
ADD COLUMN visual_need TEXT NOT NULL DEFAULT 'none' CHECK (visual_need IN ('none', 'equation', 'graph', 'diagram')),
ADD COLUMN language_pack JSONB NOT NULL DEFAULT '["ur", "en"]'::jsonb;

-- Rename textbook_page to textbook_sources (JSONB)
ALTER TABLE concepts RENAME COLUMN textbook_page TO textbook_sources_temp;
ALTER TABLE concepts ADD COLUMN textbook_sources JSONB NOT NULL DEFAULT '[]'::jsonb;

-- Migrate data from the old textbook_sources_temp to the new JSONB textbook_sources
UPDATE concepts
SET textbook_sources = jsonb_build_array(textbook_sources_temp)
WHERE textbook_sources_temp IS NOT NULL;

-- Drop the old temporary column
ALTER TABLE concepts DROP COLUMN textbook_sources_temp;
