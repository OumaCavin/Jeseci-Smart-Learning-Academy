-- =============================================================================
-- Testimonials Table Migration
-- Creates table for storing and managing user testimonials/reviews
-- =============================================================================

-- Create testimonials table
CREATE TABLE IF NOT EXISTS testimonials (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    student_name VARCHAR(100) NOT NULL,
    student_role VARCHAR(100) DEFAULT 'Student',
    avatar_url TEXT,
    content TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    is_approved BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast retrieval of approved testimonials
CREATE INDEX IF NOT EXISTS idx_testimonials_approved 
ON testimonials(is_approved, is_featured, created_at DESC);

-- Index for user-specific queries
CREATE INDEX IF NOT EXISTS idx_testimonials_user_id 
ON testimonials(user_id);

-- Create view for public testimonials (approved only)
CREATE OR REPLACE VIEW approved_testimonials AS
SELECT id, student_name, student_role, avatar_url, content, rating, is_featured, created_at
FROM testimonials
WHERE is_approved = true
ORDER BY is_featured DESC, created_at DESC;

-- Insert sample testimonials for demonstration
INSERT INTO testimonials (student_name, student_role, content, rating, is_approved, is_featured) VALUES
('Sarah Chen', 'Software Developer', 'The AI-powered content generation helped me learn complex concepts faster than any traditional course. The personalized learning paths adapted perfectly to my skill level.', 5, true, true),
('Marcus Johnson', 'Data Scientist', 'Jeseci Academy transformed my understanding of Object-Spatial Programming. The interactive AI tutor provides instant feedback that accelerated my learning journey significantly.', 5, true, true),
('Emily Rodriguez', 'Computer Science Student', 'I love the achievement system - it keeps me motivated to complete my learning goals. The graph-based learning paths make complex topics easy to understand.', 5, true, true),
('David Kim', 'Full Stack Developer', 'The adaptive learning technology is impressive. It identified my weak areas and suggested targeted content that helped me master Jac programming in weeks.', 5, true, false),
('Lisa Thompson', 'Product Manager', 'As someone transitioning into tech, the structured learning paths and AI assistance made complex programming concepts accessible and engaging.', 4, true, false),
('James Wilson', 'Backend Engineer', 'The quality of AI-generated content is outstanding. It feels like having a personal tutor available 24/7. Highly recommend for any developer wanting to level up.', 5, true, false);

-- Verify the migration
SELECT 'Testimonials table created successfully' AS status, 
       COUNT(*) AS total_testimonials,
       COUNT(*) FILTER (WHERE is_approved = true) AS approved_count
FROM testimonials;
