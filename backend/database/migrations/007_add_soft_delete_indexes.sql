-- Migration: Add soft delete indexes for query performance
-- Run this in PostgreSQL to improve soft delete query performance

-- =============================================================================
-- Add is_deleted column to tables missing it
-- =============================================================================

-- Add is_deleted to testimonials table if missing
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'jeseci_academy'
        AND table_name = 'testimonials'
        AND column_name = 'is_deleted'
    ) THEN
        ALTER TABLE jeseci_academy.testimonials
        ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL;
    END IF;
END $$;

-- Add is_deleted to contact_messages table if missing
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'jeseci_academy'
        AND table_name = 'contact_messages'
        AND column_name = 'is_deleted'
    ) THEN
        ALTER TABLE jeseci_academy.contact_messages
        ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE NOT NULL;
    END IF;
END $$;

-- =============================================================================
-- Add indexes on is_deleted columns for performance
-- =============================================================================

-- Core user and content tables
CREATE INDEX IF NOT EXISTS idx_users_is_deleted ON jeseci_academy.users(is_deleted);
CREATE INDEX IF NOT EXISTS idx_user_profile_is_deleted ON jeseci_academy.user_profile(is_deleted);
CREATE INDEX IF NOT EXISTS idx_user_learning_preferences_is_deleted ON jeseci_academy.user_learning_preferences(is_deleted);

-- Content tables
CREATE INDEX IF NOT EXISTS idx_concepts_is_deleted ON jeseci_academy.concepts(is_deleted);
CREATE INDEX IF NOT EXISTS idx_concept_content_is_deleted ON jeseci_academy.concept_content(is_deleted);
CREATE INDEX IF NOT EXISTS idx_learning_paths_is_deleted ON jeseci_academy.learning_paths(is_deleted);
CREATE INDEX IF NOT EXISTS idx_lessons_is_deleted ON jeseci_academy.lessons(is_deleted);
CREATE INDEX IF NOT EXISTS idx_learning_path_concepts_is_deleted ON jeseci_academy.learning_path_concepts(is_deleted);
CREATE INDEX IF NOT EXISTS idx_lesson_concepts_is_deleted ON jeseci_academy.lesson_concepts(is_deleted);

-- Progress tracking tables
CREATE INDEX IF NOT EXISTS idx_user_concept_progress_is_deleted ON jeseci_academy.user_concept_progress(is_deleted);
CREATE INDEX IF NOT EXISTS idx_user_learning_paths_is_deleted ON jeseci_academy.user_learning_paths(is_deleted);
CREATE INDEX IF NOT EXISTS idx_user_lesson_progress_is_deleted ON jeseci_academy.user_lesson_progress(is_deleted);
CREATE INDEX IF NOT EXISTS idx_learning_sessions_is_deleted ON jeseci_academy.learning_sessions(is_deleted);

-- Assessment tables
CREATE INDEX IF NOT EXISTS idx_quizzes_is_deleted ON jeseci_academy.quizzes(is_deleted);
CREATE INDEX IF NOT EXISTS idx_quiz_attempts_is_deleted ON jeseci_academy.quiz_attempts(is_deleted);

-- Gamification tables
CREATE INDEX IF NOT EXISTS idx_achievements_is_deleted ON jeseci_academy.achievements(is_deleted);
CREATE INDEX IF NOT EXISTS idx_user_achievements_is_deleted ON jeseci_academy.user_achievements(is_deleted);
CREATE INDEX IF NOT EXISTS idx_badges_is_deleted ON jeseci_academy.badges(is_deleted);
CREATE INDEX IF NOT EXISTS idx_user_badges_is_deleted ON jeseci_academy.user_badges(is_deleted);

-- Testimonials and contact messages
CREATE INDEX IF NOT EXISTS idx_testimonials_is_deleted ON jeseci_academy.testimonials(is_deleted);
CREATE INDEX IF NOT EXISTS idx_contact_messages_is_deleted ON jeseci_academy.contact_messages(is_deleted);

-- Code execution tables
CREATE INDEX IF NOT EXISTS idx_code_folders_is_deleted ON jeseci_academy.code_folders(is_deleted);
CREATE INDEX IF NOT EXISTS idx_code_snippets_is_deleted ON jeseci_academy.code_snippets(is_deleted);
CREATE INDEX IF NOT EXISTS idx_execution_history_is_deleted ON jeseci_academy.execution_history(is_deleted);
CREATE INDEX IF NOT EXISTS idx_snippet_versions_is_deleted ON jeseci_academy.snippet_versions(is_deleted);
CREATE INDEX IF NOT EXISTS idx_test_cases_is_deleted ON jeseci_academy.test_cases(is_deleted);
CREATE INDEX IF NOT EXISTS idx_test_results_is_deleted ON jeseci_academy.test_results(is_deleted);
CREATE INDEX IF NOT EXISTS idx_debug_sessions_is_deleted ON jeseci_academy.debug_sessions(is_deleted);

-- =============================================================================
-- Composite indexes for common query patterns
-- =============================================================================

-- Users: active and not deleted
CREATE INDEX IF NOT EXISTS idx_users_active_not_deleted ON jeseci_academy.users(is_active, is_deleted);

-- Learning paths: published and not deleted
CREATE INDEX IF NOT EXISTS idx_learning_paths_published_not_deleted ON jeseci_academy.learning_paths(is_published, is_deleted);

-- Quizzes: published and not deleted
CREATE INDEX IF NOT EXISTS idx_quizzes_published_not_deleted ON jeseci_academy.quizzes(is_published, is_deleted);

-- Achievements: active and not deleted
CREATE INDEX IF NOT EXISTS idx_achievements_active_not_deleted ON jeseci_academy.achievements(is_active, is_deleted);

-- Badges: active and not deleted
CREATE INDEX IF NOT EXISTS idx_badges_active_not_deleted ON jeseci_academy.badges(is_active, is_deleted);

-- Concepts: published status and not deleted
CREATE INDEX IF NOT EXISTS idx_concepts_status_not_deleted ON jeseci_academy.concepts(status, is_deleted);

-- =============================================================================
-- Verification
-- =============================================================================

-- List all created indexes on is_deleted column
SELECT
    t.relname AS table_name,
    i.relname AS index_name,
    a.attname AS column_name
FROM
    pg_class t
    JOIN pg_index ix ON t.oid = ix.indrelid
    JOIN pg_class i ON i.oid = ix.indexrelid
    JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
WHERE
    a.attname = 'is_deleted'
    AND t.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'jeseci_academy')
ORDER BY t.relname;
