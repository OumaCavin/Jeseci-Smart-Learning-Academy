import React from 'react';
import { formatDistanceToNow } from 'date-fns';
import ActivityIcon from './ActivityIcon';
import { Activity } from '../../services/activityService';

interface RecentActivityCardProps {
  activity: Activity;
  onClick?: (activity: Activity) => void;
  showTimestamp?: boolean;
  compact?: boolean;
}

const RecentActivityCard: React.FC<RecentActivityCardProps> = ({
  activity,
  onClick,
  showTimestamp = true,
  compact = false,
}) => {
  const formatActivityDetails = (activity: Activity): { title: string; description: string } => {
    switch (activity.type) {
      case 'LESSON_COMPLETED':
        return {
          title: 'Lesson Completed',
          description: activity.description || 'You completed a lesson',
        };
      case 'COURSE_STARTED':
        return {
          title: 'Course Started',
          description: activity.description || 'You started a course',
        };
      case 'COURSE_COMPLETED':
        return {
          title: 'Course Completed',
          description: activity.description || 'You completed a course',
        };
      case 'QUIZ_PASSED':
        return {
          title: 'Quiz Passed',
          description: activity.description || 'You passed a quiz',
        };
      case 'ACHIEVEMENT_EARNED':
        return {
          title: 'Achievement Unlocked',
          description: activity.description || 'You earned an achievement',
        };
      case 'STREAK_MILESTONE':
        return {
          title: 'Streak Milestone',
          description: activity.description || 'You reached a streak milestone',
        };
      case 'LOGIN':
        return {
          title: 'Welcome Back!',
          description: 'You logged into your account',
        };
      case 'CONTENT_VIEWED':
        return {
          title: 'Content Viewed',
          description: activity.description || 'You viewed some content',
        };
      case 'AI_GENERATED':
        return {
          title: 'AI Generated',
          description: activity.description || 'AI content generated',
        };
      case 'LEARNING_PATH_STARTED':
        return {
          title: 'Learning Path Started',
          description: activity.description || 'You started a learning path',
        };
      case 'LEARNING_PATH_COMPLETED':
        return {
          title: 'Learning Path Completed',
          description: activity.description || 'You completed a learning path',
        };
      case 'CONCEPT_MASTERED':
        return {
          title: 'Concept Mastered',
          description: activity.description || 'You mastered a concept',
        };
      case 'BADGE_EARNED':
        return {
          title: 'Badge Earned',
          description: activity.description || 'You earned a badge',
        };
      default:
        {
          const activityType = activity.type as string;
          return {
            title: activityType.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
            description: activity.description || 'You performed an activity',
          };
        }
    }
  };

  const { title, description } = formatActivityDetails(activity);

  const getPointsBadge = (activity: Activity): string | null => {
    if (activity.xp_earned && activity.xp_earned > 0) {
      return `+${activity.xp_earned} XP`;
    }
    return null;
  };

  const handleClick = () => {
    if (onClick) {
      onClick(activity);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (onClick && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      onClick(activity);
    }
  };

  return (
    <div
      className={`flex items-start gap-3 p-3 rounded-lg transition-all duration-200 ${
        onClick ? 'cursor-pointer hover:bg-gray-50' : ''
      } ${compact ? 'py-2' : ''}`}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      tabIndex={onClick ? 0 : undefined}
      role={onClick ? 'button' : undefined}
      aria-label={title}
    >
      <ActivityIcon type={activity.type} size={compact ? 'sm' : 'md'} />

      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <h4 className={`font-medium text-gray-900 ${compact ? 'text-sm' : 'text-base'}`}>
              {title}
            </h4>
            {!compact && (
              <p className="text-sm text-gray-600 mt-0.5 line-clamp-2">
                {description}
              </p>
            )}
          </div>

          <div className="flex flex-col items-end gap-1 flex-shrink-0">
            {getPointsBadge(activity) && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                {getPointsBadge(activity)}
              </span>
            )}
            {showTimestamp && activity.created_at && (
              <time
                className="text-xs text-gray-500"
                dateTime={new Date(activity.created_at).toISOString()}
                title={new Date(activity.created_at).toLocaleString()}
              >
                {formatDistanceToNow(new Date(activity.created_at), { addSuffix: true })}
              </time>
            )}
          </div>
        </div>

        {compact && (
          <p className="text-sm text-gray-600 mt-1 line-clamp-1">
            {description}
          </p>
        )}
      </div>
    </div>
  );
};

export default RecentActivityCard;
