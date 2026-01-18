-- Migration: Create testimonials table
-- Run this in PostgreSQL to add testimonials support

-- Create the testimonials table if it doesn't exist
CREATE TABLE IF NOT EXISTS jeseci_academy.testimonials (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(100),
    company VARCHAR(100),
    content TEXT NOT NULL,
    rating INTEGER DEFAULT 5,
    avatar_url VARCHAR(500),
    is_approved BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_testimonial_approved ON jeseci_academy.testimonials(is_approved);
CREATE INDEX IF NOT EXISTS idx_testimonial_active ON jeseci_academy.testimonials(is_active);

-- Add sample testimonials
INSERT INTO jeseci_academy.testimonials (name, role, company, content, rating, is_approved, is_active)
VALUES 
    ('Sarah Johnson', 'Software Engineer', 'Tech Corp', 'Jeseci Smart Learning Academy transformed my career. The interactive lessons on Jac programming and graph-based concepts helped me land my dream job as a backend developer. The AI-powered tutoring system adapted perfectly to my learning pace.', 5, true, true),
    ('Michael Chen', 'Data Scientist', 'Analytics Inc', 'The platform''s approach to teaching complex topics like Object-Spatial Programming through visual graphs is exceptional. I went from knowing nothing about Jac to building full-stack applications in just 3 months.', 5, true, true),
    ('Emily Rodriguez', 'Student', 'University of Computer Science', 'As a computer science student, I found the learning paths here complement my coursework perfectly. The concept relationships feature helped me understand how different programming concepts interconnect.', 5, true, true),
    ('David Park', 'Full Stack Developer', 'StartupXYZ', 'The gamification elements keep me motivated. Earning badges and tracking my progress through the learning paths makes studying feel rewarding. The community features also helped me find a study partner.', 4, true, true),
    ('Amanda Foster', 'Self-Taught Programmer', 'Freelancer', 'I tried many online learning platforms, but Jeseci is different. The AI-generated content is always up-to-date, and the hands-on coding exercises with immediate feedback accelerated my learning significantly.', 5, true, true)
ON CONFLICT DO NOTHING;
