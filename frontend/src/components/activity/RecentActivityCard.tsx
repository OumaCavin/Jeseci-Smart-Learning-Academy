import React from 'react';
import { formatDistanceToNow } from 'date-fns';
import ActivityIcon from './ActivityIcon';
import { UserActivity } from '../../services/activityService';

interface RecentActivityCardProps {
  activity: UserActivity;
  onClick?: (activity: UserActivity) => void;
  showTimestamp?: boolean;
  compact?: boolean;
}

const RecentActivityCard: React.FC<RecentActivityCardProps> = ({
  activity,
  onClick,
  showTimestamp = true,
  compact = false,
}) => {
  const formatActivityDetails = (activity: UserActivity): { title: string; description: string } => {
    switch (activity.activity_type) {
      case 'lesson_completed':
        return {
          title: 'Lesson Completed',
          description: `You completed "${activity.metadata?.lesson_title || 'a lesson'}"`,
        };
      case 'quiz_passed':
        return {
          title: 'Quiz Passed',
          description: `You passed the quiz with ${activity.metadata?.score || 0}% score`,
        };
      case 'achievement_unlocked':
        return {
          title: 'Achievement Unlocked',
          description: `You earned the "${activity.metadata?.achievement_name || 'achievement'}" badge`,
        };
      case 'streak_started':
        return {
          title: 'Streak Started',
          description: `You started a ${activity.metadata?.streak_days || 1} day learning streak!`,
        };
      case 'course_enrolled':
        return {
          title: 'Course Enrolled',
          description: `You enrolled in "${activity.metadata?.course_title || 'a course'}"`,
        };
      case 'module_completed':
        return {
          title: 'Module Completed',
          description: `You completed the module "${activity.metadata?.module_title || 'a module'}"`,
        };
      case 'level_up':
        return {
          title: 'Level Up!',
          description: `Congratulations! You've reached level ${activity.metadata?.new_level || 1}`,
        };
      case 'daily_goal_reached':
        return {
          title: 'Daily Goal Reached',
          description: `You studied for ${activity.metadata?.study_minutes || 0} minutes today`,
        };
      case 'certificate_earned':
        return {
          title: 'Certificate Earned',
          description: `You earned a certificate for "${activity.metadata?.course_title || 'course'}"`,
        };
      case 'friend_joined':
        return {
          title: 'Friend Joined',
          description: `${activity.metadata?.friend_name || 'A friend'} joined the platform`,
        };
      case 'comment_posted':
        return {
          title: 'Comment Posted',
          description: `You commented on "${activity.metadata?.lesson_title || 'a lesson'}"`,
        };
      case 'login':
        return {
          title: 'Welcome Back!',
          description: 'You logged into your account',
        };
      default:
        return {
          title: activity.activity_type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
          description: activity.description || 'You performed an activity',
        };
    }
  };

  const { title, description } = formatActivityDetails(activity);

  const getPointsBadge = (activity: UserActivity): string | null => {
    if (activity.points_earned && activity.points_earned > 0) {
      return `+${activity.points_earned} XP`;
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
      <ActivityIcon type={activity.activity_type} size={compact ? 'sm' : 'md'} />

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

        {!compact && activity.metadata && Object.keys(activity.metadata).length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {activity.metadata.course_title && (
              <span className="inline-flex items-center px-2 py-1 rounded-md bg-blue-50 text-xs text-blue-700">
                {activity.metadata.course_title}
              </span>
            )}
            {activity.metadata.lesson_title && (
              <span className="inline-flex items-center px-2 py-1 rounded-md bg-purple-50 text-xs text-purple-700">
                {activity.metadata.lesson_title}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default RecentActivityCard;
