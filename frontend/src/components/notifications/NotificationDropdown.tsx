// Notification Dropdown Component
// Shows a panel with recent notifications when clicking the bell icon

import React, { useEffect, useRef } from 'react';
import { Bell, Check, X, Loader } from 'lucide-react';
import { useNotifications } from '../../contexts/NotificationContext';
import { NotificationItem } from './NotificationItem';
import { Link } from 'react-router-dom';

interface NotificationDropdownProps {
  isOpen: boolean;
  onClose: () => void;
}

export const NotificationDropdown: React.FC<NotificationDropdownProps> = ({ isOpen, onClose }) => {
  const dropdownRef = useRef<HTMLDivElement>(null);
  const {
    notifications,
    unreadCount,
    isLoading,
    fetchNotifications,
    markAllAsRead
  } = useNotifications();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, onClose]);

  // Fetch notifications when dropdown opens
  useEffect(() => {
    if (isOpen) {
      fetchNotifications({ limit: 10 });
    }
  }, [isOpen, fetchNotifications]);

  // Handle mark all as read
  const handleMarkAllAsRead = async () => {
    await markAllAsRead();
  };

  if (!isOpen) return null;

  return (
    <div 
      ref={dropdownRef}
      className="absolute right-0 top-full mt-2 w-96 bg-white rounded-xl shadow-2xl 
                 border border-gray-200 z-50 overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <Bell size={18} className="text-gray-600" />
          <h3 className="font-semibold text-gray-900">Notifications</h3>
          {unreadCount > 0 && (
            <span className="px-2 py-0.5 bg-red-500 text-white text-xs font-medium rounded-full">
              {unreadCount}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {unreadCount > 0 && (
            <button
              onClick={handleMarkAllAsRead}
              className="text-xs text-blue-600 hover:text-blue-800 font-medium px-2 py-1
                       hover:bg-blue-50 rounded transition-colors"
            >
              Mark all read
            </button>
          )}
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-h-96 overflow-y-auto">
        {isLoading ? (
          // Loading state
          <div className="flex items-center justify-center py-12">
            <Loader size={24} className="animate-spin text-blue-600" />
          </div>
        ) : notifications.length === 0 ? (
          // Empty state
          <div className="flex flex-col items-center justify-center py-12 px-4">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <Bell size={24} className="text-gray-400" />
            </div>
            <p className="text-gray-600 font-medium">No notifications yet</p>
            <p className="text-sm text-gray-400 mt-1 text-center">
              We'll notify you when something important happens
            </p>
          </div>
        ) : (
          // Notification list
          <div className="divide-y divide-gray-100">
            {notifications.slice(0, 10).map((notification) => (
              <NotificationItem 
                key={notification.id} 
                notification={notification}
                compact
              />
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      {notifications.length > 0 && (
        <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
          <Link
            to="/notifications"
            onClick={onClose}
            className="block w-full text-center px-4 py-2 bg-blue-600 text-white 
                     rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm"
          >
            View all notifications
          </Link>
        </div>
      )}
    </div>
  );
};

export default NotificationDropdown;
