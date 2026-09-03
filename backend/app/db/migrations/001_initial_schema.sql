-- ================================================================
-- AI Tutor — Initial Database Schema
-- Migration: 001_initial_schema.sql
-- 
-- Creates all 9 core tables matching the architecture document
-- (Part 7: Database Schema). This migration is forward-only.
-- NEVER modify this file after deployment.
-- ================================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ────────────────────────────────────────────────────
-- 1. Students
-- ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    phone TEXT UNIQUE,
    class_level INTEGER NOT NULL DEFAULT 10,
    board TEXT NOT NULL DEFAULT 'punjab',
    group_type TEXT NOT NULL DEFAULT 'science',
    preferred_language TEXT NOT NULL DEFAULT 'ur',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ────────────────────────────────────────────────────
-- 2. Subjects
-- ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS subjects (
    id TEXT PRIMARY KEY,
    name_en TEXT NOT NULL,
    name_ur TEXT NOT NULL,
    pedagogy_config JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ────────────────────────────────────────────────────
-- 3. Concepts (Curriculum Model)
-- ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS concepts (
    concept_id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL REFERENCES subjects(id),
    chapter INTEGER NOT NULL,
    chapter_name TEXT NOT NULL,
    name_en TEXT NOT NULL,
    name_ur TEXT NOT NULL,
    difficulty INTEGER NOT NULL CHECK (difficulty BETWEEN 1 AND 5),
    textbook_page TEXT,
    pedagogy_type TEXT NOT NULL CHECK (pedagogy_type IN ('conceptual', 'procedural', 'application')),
    learning_objectives JSONB NOT NULL DEFAULT '[]'::jsonb,
    formulas JSONB NOT NULL DEFAULT '[]'::jsonb,
    explanation_ur TEXT NOT NULL,
    key_terms JSONB NOT NULL DEFAULT '[]'::jsonb,
    worked_examples JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ────────────────────────────────────────────────────
-- 4. Concept Prerequisites (DAG edges)
-- ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS concept_prerequisites (
    concept_id TEXT NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    prerequisite_id TEXT NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    PRIMARY KEY (concept_id, prerequisite_id),
    CHECK (concept_id != prerequisite_id)
);

-- ────────────────────────────────────────────────────
-- 5. Questions (Question Bank)
-- ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS questions (
    question_id TEXT PRIMARY KEY,
    concept_id TEXT NOT NULL REFERENCES concepts(concept_id),
    difficulty INTEGER NOT NULL CHECK (difficulty BETWEEN 1 AND 6),
    question_type TEXT NOT NULL,
    question_text_ur TEXT NOT NULL,
    question_text_en TEXT NOT NULL,
    expected_answer TEXT NOT NULL,
    answer_tolerance REAL,
    expected_answer_unit TEXT,
    solution_steps JSONB NOT NULL DEFAULT '[]'::jsonb,
    hints JSONB NOT NULL DEFAULT '[]'::jsonb,
    tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ────────────────────────────────────────────────────
-- 6. Misconceptions
-- ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS misconceptions (
    misconception_id TEXT PRIMARY KEY,
    concept_id TEXT NOT NULL REFERENCES concepts(concept_id),
    subject_key TEXT NOT NULL DEFAULT 'mathematics',
    description_en TEXT NOT NULL,
    description_ur TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    error_patterns JSONB NOT NULL DEFAULT '[]'::jsonb,
    prerequisite_gap TEXT REFERENCES concepts(concept_id),
    remediation_strategy TEXT NOT NULL,
    remediation_explanation_ur TEXT NOT NULL,
    diagnostic_question_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    practice_question_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ────────────────────────────────────────────────────
-- 7. Student Mastery (Student Model state)
-- ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS student_mastery (
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    concept_id TEXT NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
    mastery_state TEXT NOT NULL DEFAULT 'unknown'
        CHECK (mastery_state IN (
            'unknown', 'assessed_weak', 'introduced', 'practicing',
            'struggling', 'partial', 'mastered', 'needs_review'
        )),
    consecutive_correct INTEGER NOT NULL DEFAULT 0,
    consecutive_wrong INTEGER NOT NULL DEFAULT 0,
    total_attempts INTEGER NOT NULL DEFAULT 0,
    total_correct INTEGER NOT NULL DEFAULT 0,
    last_attempt_at TIMESTAMPTZ,
    mastered_at TIMESTAMPTZ,
    misconception_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (student_id, concept_id)
);

-- ────────────────────────────────────────────────────
-- 8. Sessions (Tutoring session state)
-- ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    subject_key TEXT NOT NULL REFERENCES subjects(id),
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at TIMESTAMPTZ,
    current_concept_id TEXT REFERENCES concepts(concept_id),
    current_question_id TEXT,
    session_state JSONB NOT NULL DEFAULT '{}'::jsonb,
    hint_level INTEGER NOT NULL DEFAULT 0,
    scaffold_step INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    summary TEXT,
    total_exchanges INTEGER NOT NULL DEFAULT 0
);

-- ────────────────────────────────────────────────────
-- 9. Attempts (Question attempt log)
-- ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    question_id TEXT NOT NULL REFERENCES questions(question_id),
    concept_id TEXT NOT NULL REFERENCES concepts(concept_id),
    student_answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    is_partial BOOLEAN NOT NULL DEFAULT false,
    error_type TEXT,
    misconception_id TEXT,
    hint_level_used INTEGER NOT NULL DEFAULT 0,
    time_taken_seconds INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ────────────────────────────────────────────────────
-- Indexes for query performance
-- ────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_student_mastery_student ON student_mastery(student_id);
CREATE INDEX IF NOT EXISTS idx_student_mastery_concept ON student_mastery(concept_id);
CREATE INDEX IF NOT EXISTS idx_sessions_student ON sessions(student_id);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON sessions(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_attempts_session ON attempts(session_id);
CREATE INDEX IF NOT EXISTS idx_attempts_student ON attempts(student_id);
CREATE INDEX IF NOT EXISTS idx_questions_concept ON questions(concept_id);
CREATE INDEX IF NOT EXISTS idx_concepts_subject ON concepts(subject_id);
CREATE INDEX IF NOT EXISTS idx_concepts_chapter ON concepts(chapter);
