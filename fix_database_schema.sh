#!/bin/bash
# Fix for missing criteria_type column in achievements and badges tables

echo "=========================================="
echo "Fixing Database Schema Issues"
echo "=========================================="

# Load environment variables
source backend/config/.env

echo ""
echo "Adding missing criteria_type column to achievements table..."

PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" << EOF
-- Add criteria_type column to achievements table if it doesn't exist
ALTER TABLE jeseci_academy.achievements 
ADD COLUMN IF NOT EXISTS criteria_type VARCHAR(50) NOT NULL DEFAULT 'concepts_completed';

-- Add criteria_type column to badges table if it doesn't exist  
ALTER TABLE jeseci_academy.badges
ADD COLUMN IF NOT EXISTS criteria_type VARCHAR(50) NOT NULL DEFAULT 'concepts_completed';

-- Update existing records with default values if criteria_type is missing
UPDATE jeseci_academy.achievements 
SET criteria_type = 'concepts_completed' 
WHERE criteria_type IS NULL;

UPDATE jeseci_academy.badges 
SET criteria_type = 'concepts_completed' 
WHERE criteria_type IS NULL;

-- Add default achievements if they don't exist
INSERT INTO jeseci_academy.achievements 
(achievement_id, name, description, icon, criteria_type, criteria_value, points, tier, is_active)
VALUES
('first_concept', 'First Steps', 'Complete your first concept', '🎯', 'concepts_completed', 1, 10, 'bronze', TRUE),
('concept_master', 'Concept Master', 'Complete 10 concepts', '📚', 'concepts_completed', 10, 25, 'silver', TRUE),
('knowledge_seeker', 'Knowledge Seeker', 'Complete 25 concepts', '🧠', 'concepts_completed', 25, 50, 'gold', TRUE),
('concept_champion', 'Concept Champion', 'Complete 50 concepts', '🏆', 'concepts_completed', 50, 100, 'platinum', TRUE),
('first_quiz', 'Quiz Beginner', 'Pass your first quiz', '✅', 'quizzes_passed', 1, 10, 'bronze', TRUE),
('quiz_master', 'Quiz Master', 'Pass 10 quizzes', '🎓', 'quizzes_passed', 10, 30, 'silver', TRUE),
('quiz_champion', 'Quiz Champion', 'Pass 25 quizzes', '🥇', 'quizzes_passed', 25, 60, 'gold', TRUE),
('perfect_score', 'Perfect Score', 'Score 100% on a quiz', '💯', 'quizzes_passed', 1, 50, 'gold', TRUE),
('week_warrior', 'Week Warrior', 'Maintain a 7-day streak', '🔥', 'streak_days', 7, 20, 'bronze', TRUE),
('month_master', 'Month Master', 'Maintain a 30-day streak', '🌟', 'streak_days', 30, 75, 'silver', TRUE),
('dedication', 'Dedicated Learner', 'Maintain a 100-day streak', '💎', 'streak_days', 100, 200, 'platinum', TRUE),
('first_course', 'Course Starter', 'Complete your first course', '🚀', 'courses_completed', 1, 15, 'bronze', TRUE),
('course_explorer', 'Course Explorer', 'Complete 5 courses', '🌍', 'courses_completed', 5, 40, 'silver', TRUE),
('course_conqueror', 'Course Conqueror', 'Complete 10 courses', '👑', 'courses_completed', 10, 80, 'gold', TRUE)
ON CONFLICT (achievement_id) DO NOTHING;

SELECT 'Achievements table fixed successfully!' AS status;
EOF

echo ""
echo "Schema fix completed!"
echo "=========================================="
