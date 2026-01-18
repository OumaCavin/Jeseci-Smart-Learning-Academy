-- Migration: Create testimonials and contact_messages tables
-- Run this in PostgreSQL to add support for testimonials and contact messages

-- Create contact_messages table if it doesn't exist
CREATE TABLE IF NOT EXISTS jeseci_academy.contact_messages (
    message_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(255) NOT NULL,
    subject VARCHAR(500),
    message TEXT NOT NULL,
    phone VARCHAR(50),
    contact_reason VARCHAR(50) DEFAULT 'general',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'pending',
    ip_address VARCHAR(50),
    user_agent VARCHAR(500)
);

-- Create testimonials table if it doesn't exist
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
CREATE INDEX IF NOT EXISTS idx_contact_status ON jeseci_academy.contact_messages(status);

-- Insert sample testimonials (only if table is empty)
INSERT INTO jeseci_academy.testimonials (name, role, company, content, rating, is_approved, is_active)
SELECT 'Sarah Johnson', 'Software Engineer', 'Tech Corp', 
       'Jeseci Smart Learning Academy transformed my career. The interactive lessons on Jac programming and graph-based concepts helped me land my dream job as a backend developer.', 
       5, true, true
WHERE NOT EXISTS (SELECT 1 FROM jeseci_academy.testimonials WHERE name = 'Sarah Johnson');

INSERT INTO jeseci_academy.testimonials (name, role, company, content, rating, is_approved, is_active)
SELECT 'Michael Chen', 'Data Scientist', 'Analytics Inc',
       'The platform''s approach to teaching complex topics like Object-Spatial Programming through visual graphs is exceptional.',
       5, true, true
WHERE NOT EXISTS (SELECT 1 FROM jeseci_academy.testimonials WHERE name = 'Michael Chen');

INSERT INTO jeseci_academy.testimonials (name, role, company, content, rating, is_approved, is_active)
SELECT 'Emily Rodriguez', 'Student', 'University of Computer Science',
       'As a computer science student, I found the learning paths here complement my coursework perfectly.',
       5, true, true
WHERE NOT EXISTS (SELECT 1 FROM jeseci_academy.testimonials WHERE name = 'Emily Rodriguez');

INSERT INTO jeseci_academy.testimonials (name, role, company, content, rating, is_approved, is_active)
SELECT 'David Park', 'Full Stack Developer', 'StartupXYZ',
       'The gamification elements keep me motivated. Earning badges and tracking my progress makes studying feel rewarding.',
       4, true, true
WHERE NOT EXISTS (SELECT 1 FROM jeseci_academy.testimonials WHERE name = 'David Park');

INSERT INTO jeseci_academy.testimonials (name, role, company, content, rating, is_approved, is_active)
SELECT 'Amanda Foster', 'Self-Taught Programmer', 'Freelancer',
       'I tried many online learning platforms, but Jeseci is different. The AI-generated content is always up-to-date.',
       5, true, true
WHERE NOT EXISTS (SELECT 1 FROM jeseci_academy.testimonials WHERE name = 'Amanda Foster');
