-- =============================================================================
-- Testimonials Table Migration
-- Creates table for storing and managing user testimonials/reviews
-- Note: This migration creates the base table structure without foreign key
-- references since the users table may not exist yet during early migrations.
-- The initialize_database.py script creates the full table structure.
-- =============================================================================

-- Create testimonials table (without FK reference since users table doesn't exist yet)
CREATE TABLE IF NOT EXISTS jeseci_academy.testimonials (
    id SERIAL PRIMARY KEY,
    testimonial_id VARCHAR(64) UNIQUE NOT NULL,
    author_name VARCHAR(100) NOT NULL,
    author_role VARCHAR(100),
    author_avatar VARCHAR(500),
    content TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    is_approved BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_published BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    category VARCHAR(50) DEFAULT 'general',
    meta_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP WITH TIME ZONE
);

-- Index for fast retrieval of approved and featured testimonials
CREATE INDEX IF NOT EXISTS idx_testimonials_approved
ON jeseci_academy.testimonials(is_approved, is_featured, created_at DESC);

-- Index for published testimonials
CREATE INDEX IF NOT EXISTS idx_testimonials_published
ON jeseci_academy.testimonials(is_published, is_approved)
WHERE is_published = TRUE AND is_approved = TRUE;

-- Index for featured testimonials
CREATE INDEX IF NOT EXISTS idx_testimonials_featured
ON jeseci_academy.testimonials(is_featured, is_published)
WHERE is_featured = TRUE AND is_published = TRUE;

-- Index for rating ordering
CREATE INDEX IF NOT EXISTS idx_testimonials_rating
ON jeseci_academy.testimonials(rating DESC);

-- Index for created_at ordering
CREATE INDEX IF NOT EXISTS idx_testimonials_created
ON jeseci_academy.testimonials(created_at DESC);

-- Verify the migration
SELECT 'Testimonials table created successfully' AS status,
       COUNT(*) AS total_testimonials
FROM jeseci_academy.testimonials;
