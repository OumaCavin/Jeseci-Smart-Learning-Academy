import React from 'react';

interface ActivityIconProps {
  type: string;
  size?: 'sm' | 'md' | 'lg';
}

const ActivityIcon: React.FC<ActivityIconProps> = ({ type, size = 'md' }) => {
  const getIconForActivity = (activityType: string): { icon: string; color: string; bgColor: string } => {
    const iconMap: Record<string, { icon: string; color: string; bgColor: string }> = {
      'lesson_completed': {
        icon: '📚',
        color: 'text-green-600',
        bgColor: 'bg-green-100',
      },
      'quiz_passed': {
        icon: '✅',
        color: 'text-blue-600',
        bgColor: 'bg-blue-100',
      },
      'achievement_unlocked': {
        icon: '🏆',
        color: 'text-yellow-600',
        bgColor: 'bg-yellow-100',
      },
      'streak_started': {
        icon: '🔥',
        color: 'text-orange-500',
        bgColor: 'bg-orange-100',
      },
      'course_enrolled': {
        icon: '📝',
        color: 'text-purple-600',
        bgColor: 'bg-purple-100',
      },
      'module_completed': {
        icon: '🎯',
        color: 'text-indigo-600',
        bgColor: 'bg-indigo-100',
      },
      'level_up': {
        icon: '⬆️',
        color: 'text-emerald-600',
        bgColor: 'bg-emerald-100',
      },
      'daily_goal_reached': {
        icon: '🎯',
        color: 'text-rose-600',
        bgColor: 'bg-rose-100',
      },
      'certificate_earned': {
        icon: '📜',
        color: 'text-amber-600',
        bgColor: 'bg-amber-100',
      },
      'friend_joined': {
        icon: '👥',
        color: 'text-cyan-600',
        bgColor: 'bg-cyan-100',
      },
      'comment_posted': {
        icon: '💬',
        color: 'text-teal-600',
        bgColor: 'bg-teal-100',
      },
      'login': {
        icon: '🔐',
        color: 'text-gray-600',
        bgColor: 'bg-gray-100',
      },
      'default': {
        icon: '✨',
        color: 'text-gray-600',
        bgColor: 'bg-gray-100',
      },
    };

    return iconMap[activityType] || iconMap['default'];
  };

  const { icon, color, bgColor } = getIconForActivity(type);

  const sizeClasses = {
    sm: 'w-8 h-8 text-sm',
    md: 'w-10 h-10 text-base',
    lg: 'w-12 h-12 text-lg',
  };

  return (
    <div
      className={`${sizeClasses[size]} ${bgColor} ${color} rounded-full flex items-center justify-center flex-shrink-0`}
      aria-label={type.replace(/_/g, ' ')}
    >
      {icon}
    </div>
  );
};

export default ActivityIcon;
