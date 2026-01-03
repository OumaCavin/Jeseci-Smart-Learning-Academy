// Notification Center Page
// Full page view of all notifications with filtering and bulk actions

import React, { useState, useEffect } from 'react';
import { 
  Bell, 
  Check, 
  CheckCheck, 
  Trash2, 
  Loader, 
  Filter,
  Search,
  X,
  Trophy,
  GraduationCap,
  BookOpen,
  MessageCircle,
  Flame,
  Bot
} from 'lucide-react';
import { useNotifications } from '../contexts/NotificationContext';
import { NotificationItem } from './NotificationItem';
import { NotificationType, NOTIFICATION_TYPE_CONFIG } from '../services/notificationService';
import { Link } from 'react-router-dom';

type FilterTab = 'all' | 'unread' | NotificationType;

const filterTabs: { id: FilterTab; label: string; icon?: React.ReactNode }[] = [
  { id: 'all', label: 'All', icon: <Bell size={16} /> },
  { id: 'unread', label: 'Unread', icon: <div className="w-2 h-2 bg-blue-500 rounded-full"></div> },
];

const typeTabs: { id: NotificationType; label: string; icon: React.ReactNode }[] = [
  { id: 'ACHIEVEMENT', label: 'Achievements', icon: <Trophy size={16} /> },
  { id: 'COURSE_MILESTONE', label: 'Courses', icon: <GraduationCap size={16} /> },
  { id: 'CONTENT_UPDATE', label: 'Content', icon: <BookOpen size={16} /> },
  { id: 'COMMUNITY_REPLY', label: 'Community', icon: <MessageCircle size={16} /> },
  { id: 'STREAK_REMINDER', label: 'Streaks', icon: <Flame size={16} /> },
  { id: 'AI_RESPONSE', label: 'AI Assistant', icon: <Bot size={16} /> },
];

export const NotificationCenter: React.FC = () => {
  const {
    notifications,
    unreadCount,
    isLoading,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    fetchUnreadCount
  } = useNotifications();

  const [activeTab, setActiveTab] = useState<FilterTab>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNotifications, setSelectedNotifications] = useState<Set<string>>(new Set());
  const [isSelectMode, setIsSelectMode] = useState(false);

  // Fetch notifications based on active filter
  useEffect(() => {
    const options = {
      limit: 50,
      filterType: (activeTab === 'all' || activeTab === 'unread') ? '' : activeTab as NotificationType,
      unreadOnly: activeTab === 'unread',
    };
    fetchNotifications(options);
  }, [activeTab, fetchNotifications]);

  // Handle select/deselect all
  const handleSelectAll = () => {
    if (selectedNotifications.size === notifications.length) {
      setSelectedNotifications(new Set());
    } else {
      setSelectedNotifications(new Set(notifications.map(n => n.id)));
    }
  };

  // Handle individual selection
  const handleSelect = (notificationId: string) => {
    const newSelected = new Set(selectedNotifications);
    if (newSelected.has(notificationId)) {
      newSelected.delete(notificationId);
    } else {
      newSelected.add(notificationId);
    }
    setSelectedNotifications(newSelected);
  };

  // Handle bulk mark as read
  const handleBulkMarkAsRead = async () => {
    const ids = Array.from(selectedNotifications);
    if (ids.length > 0) {
      await markAsRead(ids);
      setSelectedNotifications(new Set());
      setIsSelectMode(false);
      fetchUnreadCount();
    }
  };

  // Handle bulk delete
  const handleBulkDelete = async () => {
    const ids = Array.from(selectedNotifications);
    if (ids.length > 0) {
      for (const id of ids) {
        await deleteNotification(id);
      }
      setSelectedNotifications(new Set());
      setIsSelectMode(false);
      fetchUnreadCount();
    }
  };

  // Filter notifications by search query
  const filteredNotifications = notifications.filter(n => 
    n.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    n.message.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-40">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Bell className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Notifications
                </h1>
                <p className="text-sm text-gray-500">
                  {unreadCount > 0 ? `${unreadCount} unread notifications` : 'All caught up!'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {isSelectMode ? (
                <>
                  <span className="text-sm text-gray-600">
                    {selectedNotifications.size} selected
                  </span>
                  <button
                    onClick={handleSelectAll}
                    className="px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    {selectedNotifications.size === notifications.length ? 'Deselect All' : 'Select All'}
                  </button>
                  <button
                    onClick={handleBulkMarkAsRead}
                    disabled={selectedNotifications.size === 0}
                    className="flex items-center gap-1 px-3 py-1.5 text-sm text-green-600 hover:bg-green-50 
                             rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Check size={16} />
                    Mark Read
                  </button>
                  <button
                    onClick={handleBulkDelete}
                    disabled={selectedNotifications.size === 0}
                    className="flex items-center gap-1 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 
                             rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Trash2 size={16} />
                    Delete
                  </button>
                  <button
                    onClick={() => {
                      setIsSelectMode(false);
                      setSelectedNotifications(new Set());
                    }}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <X size={18} />
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={markAllAsRead}
                    disabled={unreadCount === 0}
                    className="flex items-center gap-1 px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 
                             rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <CheckCheck size={16} />
                    Mark all read
                  </button>
                  <button
                    onClick={() => setIsSelectMode(true)}
                    className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    Select
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search bar */}
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search notifications..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 
                     focus:ring-blue-500 focus:border-blue-500 transition-colors"
          />
        </div>

        {/* Filter tabs */}
        <div className="flex items-center gap-2 mb-6 overflow-x-auto pb-2">
          {filterTabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg whitespace-nowrap transition-colors
                         ${activeTab === tab.id 
                           ? 'bg-blue-600 text-white' 
                           : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'}`}
            >
              {tab.icon}
              {tab.label}
              {tab.id === 'unread' && unreadCount > 0 && (
                <span className={`px-2 py-0.5 text-xs font-medium rounded-full
                                ${activeTab === tab.id ? 'bg-white/20 text-white' : 'bg-red-100 text-red-600'}`}>
                  {unreadCount}
                </span>
              )}
            </button>
          ))}
          
          <div className="w-px h-8 bg-gray-300 mx-2"></div>
          
          {typeTabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg whitespace-nowrap transition-colors
                         ${activeTab === tab.id 
                           ? 'bg-blue-600 text-white' 
                           : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'}`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* Notification list */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {isLoading ? (
            <div className="flex items-center justify-center py-16">
              <Loader size={32} className="animate-spin text-blue-600" />
            </div>
          ) : filteredNotifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 px-4">
              <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <Bell size={32} className="text-gray-400" />
              </div>
              <p className="text-gray-600 font-medium text-lg">No notifications found</p>
              <p className="text-gray-400 mt-1">
                {searchQuery ? 'Try a different search term' : 'You\'re all caught up!'}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-gray-100">
              {filteredNotifications.map((notification) => (
                <div 
                  key={notification.id}
                  className={`flex items-start gap-4 ${isSelectMode ? 'cursor-pointer' : ''}`}
                  onClick={() => isSelectMode && handleSelect(notification.id)}
                >
                  {isSelectMode && (
                    <div className="flex-shrink-0 w-6 h-6 mt-4">
                      <input
                        type="checkbox"
                        checked={selectedNotifications.has(notification.id)}
                        onChange={() => handleSelect(notification.id)}
                        className="w-5 h-5 rounded border-gray-300 text-blue-600 
                                 focus:ring-blue-500 cursor-pointer"
                        onClick={(e) => e.stopPropagation()}
                      />
                    </div>
                  )}
                  <div className="flex-1">
                    <NotificationItem 
                      notification={notification}
                      onClick={() => {
                        if (!isSelectMode) {
                          // Navigate to link if available
                          if (notification.link) {
                            window.location.href = notification.link;
                          }
                        }
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NotificationCenter;
