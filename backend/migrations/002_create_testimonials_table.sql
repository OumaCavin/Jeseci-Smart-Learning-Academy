-- =============================================================================
-- Testimonials Table Migration
-- Creates table for storing and managing user testimonials/reviews
-- Note: This migration creates the base table structure. The initialize_database.py
-- script will add additional columns and indexes for full functionality.
-- =============================================================================

-- Create testimonials table (without FK reference since users table may not exist yet)
CREATE TABLE IF NOT EXISTS jeseci_academy.testimonials (
    id SERIAL PRIMARY KEY,
    author_name VARCHAR(100) NOT NULL,
    author_role VARCHAR(100),
    author_avatar VARCHAR(500),
    content TEXT NOT NULL,
    rating INTEGER DEFAULT 5 CHECK (rating >= 1 AND rating <= 5),
    is_approved BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_published BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast retrieval of approved testimonials
CREATE INDEX IF NOT EXISTS idx_testimonials_approved
ON jeseci_academy.testimonials(is_approved, is_featured, created_at DESC);

-- Index for published testimonials
CREATE INDEX IF NOT EXISTS idx_testimonials_published
ON jeseci_academy.testimonials(is_published, is_approved)
WHERE is_published = TRUE AND is_approved = TRUE;

-- Verify the migration
SELECT 'Testimonials table created successfully' AS status,
       COUNT(*) AS total_testimonials
FROM jeseci_academy.testimonials;
