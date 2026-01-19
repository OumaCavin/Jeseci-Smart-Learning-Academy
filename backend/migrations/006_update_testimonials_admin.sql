-- Migration: Update testimonials table with additional columns
-- Run this in PostgreSQL to add admin management features

-- Add missing columns to testimonials table
ALTER TABLE jeseci_academy.testimonials
ADD COLUMN IF NOT EXISTS user_id VARCHAR(100),
ADD COLUMN IF NOT EXISTS is_featured BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;

-- Update existing rows to set updated_at
UPDATE jeseci_academy.testimonials
SET updated_at = NOW()
WHERE updated_at IS NULL;

-- Create comprehensive indexes for admin queries
CREATE INDEX IF NOT EXISTS idx_testimonials_deleted ON jeseci_academy.testimonials(is_deleted);
CREATE INDEX IF NOT EXISTS idx_testimonials_featured ON jeseci_academy.testimonials(is_featured, is_deleted);
CREATE INDEX IF NOT EXISTS idx_testimonials_user ON jeseci_academy.testimonials(user_id);
CREATE INDEX IF NOT EXISTS idx_testimonials_approved_deleted ON jeseci_academy.testimonials(is_approved, is_deleted);
CREATE INDEX IF NOT EXISTS idx_testimonials_created ON jeseci_academy.testimonials(created_at DESC);

-- Composite index for common admin queries
CREATE INDEX IF NOT EXISTS idx_testimonials_admin_list ON jeseci_academy.testimonials(
    is_deleted, 
    is_approved, 
    created_at DESC
);

-- Index for search queries
CREATE INDEX IF NOT EXISTS idx_testimonials_name_search ON jeseci_academy.testimonials(author_name varchar_pattern_ops);

-- Update the migration tracking
INSERT INTO schema_migrations (migration_name, applied_at, description)
VALUES ('006_update_testimonials_admin', NOW(), 'Add admin management columns to testimonials table')
ON CONFLICT (migration_name) DO NOTHING;
