// Notification Bell Component
// Displays notification bell with unread count badge in the header

import React from 'react';
import { Bell } from 'lucide-react';
import { useNotifications } from '../../contexts/NotificationContext';

interface NotificationBellProps {
  className?: string;
  size?: number;
}

export const NotificationBell: React.FC<NotificationBellProps> = ({ 
  className = '', 
  size = 24 
}) => {
  const { unreadCount, toggleDropdown } = useNotifications();

  return (
    <button
      onClick={toggleDropdown}
      className={`relative p-2 rounded-lg hover:bg-gray-100 transition-colors ${className}`}
      aria-label="Notifications"
      title="Notifications"
    >
      <Bell size={size} className="text-gray-700" />
      
      {/* Unread count badge */}
      {unreadCount > 0 && (
        <span className="absolute -top-1 -right-1 flex items-center justify-center min-w-[20px] h-[20px] 
                       px-1.5 py-0.5 bg-red-500 text-white text-xs font-bold rounded-full
                       transform transition-transform hover:scale-105">
          {unreadCount > 99 ? '99+' : unreadCount}
        </span>
      )}
    </button>
  );
};

export default NotificationBell;
