-- =============================================================================
-- Testimonials Table Migration
-- Creates table for storing and managing user testimonials/reviews
-- =============================================================================

-- Create testimonials table
CREATE TABLE IF NOT EXISTS jeseci_academy.testimonials (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES jeseci_academy.users(id) ON DELETE CASCADE,
    author_name VARCHAR(100) NOT NULL,
    role VARCHAR(100),
    company VARCHAR(100),
    avatar_url TEXT,
    content TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
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

-- Index for user-specific queries
CREATE INDEX IF NOT EXISTS idx_testimonials_user_id
ON jeseci_academy.testimonials(user_id);

-- Index for published testimonials
CREATE INDEX IF NOT EXISTS idx_testimonials_published
ON jeseci_academy.testimonials(is_published, is_approved)
WHERE is_published = TRUE AND is_approved = TRUE;

-- Create view for public testimonials (approved and published only)
CREATE OR REPLACE VIEW jeseci_academy.approved_testimonials AS
SELECT id, author_name, role, company, avatar_url, content, rating, is_featured, created_at
FROM jeseci_academy.testimonials
WHERE is_approved = true AND is_published = true
ORDER BY is_featured DESC, created_at DESC;

-- Insert sample testimonials for demonstration
INSERT INTO jeseci_academy.testimonials (author_name, role, company, content, rating, is_approved, is_featured, is_published) VALUES
('Sarah Chen', 'Software Developer', 'Tech Corp', 'The AI-powered content generation helped me learn complex concepts faster than any traditional course. The personalized learning paths adapted perfectly to my skill level.', 5, true, true, true),
('Marcus Johnson', 'Data Scientist', 'Analytics Inc', 'Jeseci Academy transformed my understanding of Object-Spatial Programming. The interactive AI tutor provides instant feedback that accelerated my learning journey significantly.', 5, true, true, true),
('Emily Rodriguez', 'Computer Science Student', 'University of CS', 'I love the achievement system - it keeps me motivated to complete my learning goals. The graph-based learning paths make complex topics easy to understand.', 5, true, true, true),
('David Kim', 'Full Stack Developer', 'StartupXYZ', 'The adaptive learning technology is impressive. It identified my weak areas and suggested targeted content that helped me master Jac programming in weeks.', 5, true, false, true),
('Lisa Thompson', 'Product Manager', 'Innovation Labs', 'As someone transitioning into tech, the structured learning paths and AI assistance made complex programming concepts accessible and engaging.', 4, true, false, true),
('James Wilson', 'Backend Engineer', 'Cloud Systems', 'The quality of AI-generated content is outstanding. It feels like having a personal tutor available 24/7. Highly recommend for any developer wanting to level up.', 5, true, false, true);

-- Verify the migration
SELECT 'Testimonials table created successfully' AS status,
       COUNT(*) AS total_testimonials,
       COUNT(*) FILTER (WHERE is_approved = true) AS approved_count
FROM jeseci_academy.testimonials;
