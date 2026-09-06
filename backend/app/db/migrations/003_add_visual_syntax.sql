-- ================================================================
-- AI Tutor — Add visual_syntax
-- Migration: 003_add_visual_syntax.sql
-- ================================================================

ALTER TABLE concepts ADD COLUMN IF NOT EXISTS visual_syntax TEXT;
