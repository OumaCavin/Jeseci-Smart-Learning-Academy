// Notification Item Component
// Displays a single notification in the dropdown or notification center

import React from 'react';
import { 
  Trophy, 
  GraduationCap, 
  BookOpen, 
  MessageCircle, 
  Flame, 
  Bot, 
  Bell,
  Check,
  Trash2,
  ExternalLink
} from 'lucide-react';
import { Notification, NOTIFICATION_TYPE_CONFIG } from '../services/notificationService';
import { useNotifications } from '../contexts/NotificationContext';

interface NotificationItemProps {
  notification: Notification;
  compact?: boolean;
  onClick?: () => void;
}

const typeIcons: Record<string, React.ReactNode> = {
  trophy: <Trophy size={18} />,
  'graduation-cap': <GraduationCap size={18} />,
  'book-open': <BookOpen size={18} />,
  'message-circle': <MessageCircle size={18} />,
  flame: <Flame size={18} />,
  bot: <Bot size={18} />,
  bell: <Bell size={18} />,
};

export const NotificationItem: React.FC<NotificationItemProps> = ({ 
  notification, 
  compact = false,
  onClick 
}) => {
  const { deleteNotification, markAsRead } = useNotifications();
  
  const typeConfig = NOTIFICATION_TYPE_CONFIG[notification.type as keyof typeof NOTIFICATION_TYPE_CONFIG] || 
    NOTIFICATION_TYPE_CONFIG.SYSTEM_ANNOUNCEMENT;
  const icon = typeIcons[typeConfig.icon] || <Bell size={18} />;

  const formatTime = (createdAt: string) => {
    const now = new Date();
    const created = new Date(createdAt);
    const diffMs = now.getTime() - created.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffSecs < 60) return 'Just now';
    if (diffMins < 60) return `${diffMins}m`;
    if (diffHours < 24) return `${diffHours}h`;
    if (diffDays < 7) return `${diffDays}d`;
    return created.toLocaleDateString();
  };

  const handleItemClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onClick?.();
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    await deleteNotification(notification.id);
  };

  const handleMarkRead = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!notification.is_read) {
      await markAsRead([notification.id]);
    }
  };

  if (compact) {
    // Compact version for dropdown
    return (
      <div 
        onClick={handleItemClick}
        className={`flex items-start gap-3 p-3 cursor-pointer transition-colors
                   ${notification.is_read ? 'bg-white hover:bg-gray-50' : 'bg-blue-50 hover:bg-blue-100'}
                   ${!notification.is_read ? 'border-l-4 border-blue-500' : ''}`}
      >
        {/* Icon */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${typeConfig.color}`}>
          {icon}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <p className={`text-sm font-medium ${notification.is_read ? 'text-gray-700' : 'text-gray-900'}`}>
              {notification.title}
            </p>
            {!notification.is_read && (
              <span className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-1.5"></span>
            )}
          </div>
          <p className="text-xs text-gray-500 mt-0.5 truncate">
            {notification.message}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            {formatTime(notification.created_at)}
          </p>
        </div>
      </div>
    );
  }

  // Full version for notification center
  return (
    <div 
      onClick={handleItemClick}
      className={`flex items-start gap-4 p-4 cursor-pointer transition-colors border-b border-gray-100
                 ${notification.is_read ? 'bg-white hover:bg-gray-50' : 'bg-blue-50/50 hover:bg-blue-100'}`}
    >
      {/* Icon */}
      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${typeConfig.color}`}>
        {icon}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className={`text-sm font-medium ${notification.is_read ? 'text-gray-700' : 'text-gray-900'}`}>
              {notification.title}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              {notification.message}
            </p>
          </div>
          {!notification.is_read && (
            <span className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-2"></span>
          )}
        </div>

        {/* Meta info */}
        <div className="flex items-center gap-4 mt-2">
          <span className="text-xs text-gray-400">
            {formatTime(notification.created_at)}
          </span>
          {notification.link && (
            <a 
              href={notification.link}
              className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1"
              onClick={(e) => e.stopPropagation()}
            >
              <ExternalLink size={12} />
              View details
            </a>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex-shrink-0 flex items-center gap-1">
        {!notification.is_read && (
          <button
            onClick={handleMarkRead}
            className="p-1.5 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded transition-colors"
            title="Mark as read"
          >
            <Check size={16} />
          </button>
        )}
        <button
          onClick={handleDelete}
          className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
          title="Delete"
        >
          <Trash2 size={16} />
        </button>
      </div>
    </div>
  );
};

export default NotificationItem;
