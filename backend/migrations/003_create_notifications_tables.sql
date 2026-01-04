-- Migration: Create notifications and notification_preferences tables
-- Run this script to set up the notification system

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN (
        'ACHIEVEMENT',
        'COURSE_MILESTONE',
        'CONTENT_UPDATE',
        'COMMUNITY_REPLY',
        'STREAK_REMINDER',
        'AI_RESPONSE',
        'SYSTEM_ANNOUNCEMENT'
    )),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    link VARCHAR(500),
    is_read BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for efficient querying
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);

-- Create notification preferences table
CREATE TABLE IF NOT EXISTS notification_preferences (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    email_enabled BOOLEAN DEFAULT TRUE,
    push_enabled BOOLEAN DEFAULT TRUE,
    types_config JSONB DEFAULT '{
        "ACHIEVEMENT": true,
        "COURSE_MILESTONE": true,
        "CONTENT_UPDATE": true,
        "COMMUNITY_REPLY": true,
        "STREAK_REMINDER": true,
        "AI_RESPONSE": true,
        "SYSTEM_ANNOUNCEMENT": true
    }'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_notification_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for notifications table
DROP TRIGGER IF EXISTS update_notifications_timestamp ON notifications;
CREATE TRIGGER update_notifications_timestamp
    BEFORE UPDATE ON notifications
    FOR EACH ROW
    EXECUTE FUNCTION update_notification_timestamp();

-- Create trigger for notification_preferences table
DROP TRIGGER IF EXISTS update_notification_preferences_timestamp ON notification_preferences;
CREATE TRIGGER update_notification_preferences_timestamp
    BEFORE UPDATE ON notification_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_notification_timestamp();

-- Add comments
COMMENT ON TABLE notifications IS 'Stores in-app notifications for users';
COMMENT ON TABLE notification_preferences IS 'Stores user notification preferences';
COMMENT ON COLUMN notifications.type IS 'Notification type: ACHIEVEMENT, COURSE_MILESTONE, CONTENT_UPDATE, COMMUNITY_REPLY, STREAK_REMINDER, AI_RESPONSE, SYSTEM_ANNOUNCEMENT';
COMMENT ON COLUMN notifications.metadata IS 'Additional context data as JSON (e.g., badge_id, course_id, author_name)';
