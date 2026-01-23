-- Migration: Create testimonials and contact_messages tables
-- Run this in PostgreSQL to add support for testimonials and contact messages

-- Create contact_messages table if it doesn't exist
CREATE TABLE IF NOT EXISTS jeseci_academy.contact_messages (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(255) NOT NULL,
    subject VARCHAR(500),
    message TEXT NOT NULL,
    phone VARCHAR(50),
    contact_reason VARCHAR(50) DEFAULT 'general',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'new',
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    responded_at TIMESTAMP,
    responded_by VARCHAR(100),
    ip_address VARCHAR(50),
    user_agent VARCHAR(500),
    meta_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create testimonials table if it doesn't exist
-- UPDATED: Added user_id and audit columns to match Python schema
CREATE TABLE IF NOT EXISTS jeseci_academy.testimonials (
    id SERIAL PRIMARY KEY,
    testimonial_id VARCHAR(64) UNIQUE,
    user_id INTEGER,
    name VARCHAR(100) NOT NULL, -- author_name in some contexts, keeping name for compatibility
    author_name VARCHAR(100),   -- Added for compatibility
    role VARCHAR(100),          -- author_role
    author_role VARCHAR(100),   -- Added for compatibility
    company VARCHAR(100),
    content TEXT NOT NULL,
    rating INTEGER DEFAULT 5 CHECK (rating >= 1 AND rating <= 5),
    avatar_url VARCHAR(500),    -- author_avatar
    author_avatar VARCHAR(500), -- Added for compatibility
    is_approved BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    is_published BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    category VARCHAR(50) DEFAULT 'general',
    meta_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(64)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_testimonial_approved ON jeseci_academy.testimonials(is_approved);
CREATE INDEX IF NOT EXISTS idx_testimonial_active ON jeseci_academy.testimonials(is_active);
CREATE INDEX IF NOT EXISTS idx_testimonial_user_id ON jeseci_academy.testimonials(user_id);
CREATE INDEX IF NOT EXISTS idx_contact_status ON jeseci_academy.contact_messages(status);

-- Insert sample testimonials (only if table is empty)
INSERT INTO jeseci_academy.testimonials (testimonial_id, name, author_name, role, author_role, company, content, rating, is_approved, is_active, category)
SELECT 'test_sarah', 'Sarah Johnson', 'Sarah Johnson', 'Software Engineer', 'Software Engineer', 'Tech Corp', 
       'Jeseci Smart Learning Academy transformed my career. The interactive lessons on Jac programming and graph-based concepts helped me land my dream job as a backend developer.', 
       5, true, true, 'career'
WHERE NOT EXISTS (SELECT 1 FROM jeseci_academy.testimonials WHERE name = 'Sarah Johnson');

INSERT INTO jeseci_academy.testimonials (testimonial_id, name, author_name, role, author_role, company, content, rating, is_approved, is_active, category)
SELECT 'test_michael', 'Michael Chen', 'Michael Chen', 'Data Scientist', 'Data Scientist', 'Analytics Inc',
       'The platform''s approach to teaching complex topics like Object-Spatial Programming through visual graphs is exceptional.',
       5, true, true, 'content'
WHERE NOT EXISTS (SELECT 1 FROM jeseci_academy.testimonials WHERE name = 'Michael Chen');

INSERT INTO jeseci_academy.testimonials (testimonial_id, name, author_name, role, author_role, company, content, rating, is_approved, is_active, category)
SELECT 'test_emily', 'Emily Rodriguez', 'Emily Rodriguez', 'Student', 'Student', 'University of Computer Science',
       'As a computer science student, I found the learning paths here complement my coursework perfectly.',
       5, true, true, 'learning'
WHERE NOT EXISTS (SELECT 1 FROM jeseci_academy.testimonials WHERE name = 'Emily Rodriguez');

INSERT INTO jeseci_academy.testimonials (testimonial_id, name, author_name, role, author_role, company, content, rating, is_approved, is_active, category)
SELECT 'test_david', 'David Park', 'David Park', 'Full Stack Developer', 'Full Stack Developer', 'StartupXYZ',
       'The gamification elements keep me motivated. Earning badges and tracking my progress makes studying feel rewarding.',
       4, true, true, 'gamification'
WHERE NOT EXISTS (SELECT 1 FROM jeseci_academy.testimonials WHERE name = 'David Park');

INSERT INTO jeseci_academy.testimonials (testimonial_id, name, author_name, role, author_role, company, content, rating, is_approved, is_active, category)
SELECT 'test_amanda', 'Amanda Foster', 'Amanda Foster', 'Self-Taught Programmer', 'Self-Taught Programmer', 'Freelancer',
       'I tried many online learning platforms, but Jeseci is different. The AI-generated content is always up-to-date.',
       5, true, true, 'ai'
WHERE NOT EXISTS (SELECT 1 FROM jeseci_academy.testimonials WHERE name = 'Amanda Foster');
