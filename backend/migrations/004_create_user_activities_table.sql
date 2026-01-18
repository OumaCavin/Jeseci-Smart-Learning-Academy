-- Migration: Create user_activities table for activity tracking
-- Run this script to set up the activity tracking system

-- Create user activities table
CREATE TABLE IF NOT EXISTS user_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL CHECK (activity_type IN (
        'LESSON_COMPLETED',
        'COURSE_STARTED',
        'COURSE_COMPLETED',
        'QUIZ_PASSED',
        'ACHIEVEMENT_EARNED',
        'STREAK_MILESTONE',
        'LOGIN',
        'CONTENT_VIEWED',
        'AI_GENERATED',
        'LEARNING_PATH_STARTED',
        'LEARNING_PATH_COMPLETED',
        'CONCEPT_MASTERED',
        'BADGE_EARNED'
    )),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    xp_earned INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_user_activities_user_id 
ON user_activities(user_id);

CREATE INDEX IF NOT EXISTS idx_user_activities_created_at 
ON user_activities(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_user_activities_type 
ON user_activities(activity_type);

CREATE INDEX IF NOT EXISTS idx_user_activities_user_type 
ON user_activities(user_id, activity_type, created_at DESC);

-- Create activity streaks table for tracking daily streaks
CREATE TABLE IF NOT EXISTS user_activity_streaks (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    streak_type VARCHAR(50) DEFAULT 'LESSON_COMPLETED',
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    streak_start_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, streak_type)
);

-- Create index for streak queries
CREATE INDEX IF NOT EXISTS idx_user_activity_streaks_user 
ON user_activity_streaks(user_id);

-- Add comments
COMMENT ON TABLE user_activities IS 'Stores all user activities for the activity feed and tracking';
COMMENT ON TABLE user_activity_streaks IS 'Stores streak data for different activity types';
COMMENT ON COLUMN user_activities.activity_type IS 'Activity type enum: LESSON_COMPLETED, COURSE_STARTED, COURSE_COMPLETED, QUIZ_PASSED, ACHIEVEMENT_EARNED, STREAK_MILESTONE, LOGIN, CONTENT_VIEWED, AI_GENERATED, LEARNING_PATH_STARTED, LEARNING_PATH_COMPLETED, CONCEPT_MASTERED, BADGE_EARNED';
COMMENT ON COLUMN user_activities.metadata IS 'Additional context data as JSON (e.g., course_id, lesson_id, quiz_score, achievement_id)';
COMMENT ON COLUMN user_activities.xp_earned IS 'XP points earned from this activity';
