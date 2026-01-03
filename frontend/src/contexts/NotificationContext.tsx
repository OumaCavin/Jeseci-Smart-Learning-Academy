// Notification Context Provider
// Manages notification state and provides it to components

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { notificationService, Notification, NotificationPreferences, NotificationType } from '../services/notificationService';

// Context type definition
interface NotificationContextType {
  // State
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  isDropdownOpen: boolean;
  preferences: NotificationPreferences | null;
  
  // Actions
  fetchNotifications: (options?: { limit?: number; offset?: number; filterType?: NotificationType | ''; unreadOnly?: boolean }) => Promise<void>;
  fetchUnreadCount: () => Promise<void>;
  markAsRead: (notificationIds: string[]) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  deleteNotification: (notificationId: string) => Promise<void>;
  openDropdown: () => void;
  closeDropdown: () => void;
  toggleDropdown: () => void;
  fetchPreferences: () => Promise<void>;
  updatePreferences: (preferences: Partial<NotificationPreferences>) => Promise<void>;
  handleNotificationClick: (notification: Notification) => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

// Polling interval for unread count (30 seconds)
const POLLING_INTERVAL = 30000;

interface NotificationProviderProps {
  children: ReactNode;
  userId: string | null;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children, userId }) => {
  // State
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
  const [pollingTimer, setPollingTimer] = useState<NodeJS.Timeout | null>(null);

  // Fetch unread count
  const fetchUnreadCount = useCallback(async () => {
    if (!userId) return;
    
    try {
      const response = await notificationService.getUnreadCount(userId);
      if (response.success) {
        setUnreadCount(response.unread_count);
      }
    } catch (error) {
      console.error('Error fetching unread count:', error);
    }
  }, [userId]);

  // Fetch notifications
  const fetchNotifications = useCallback(async (options: { 
    limit?: number; 
    offset?: number; 
    filterType?: NotificationType | ''; 
    unreadOnly?: boolean 
  } = {}) => {
    if (!userId) return;
    
    setIsLoading(true);
    try {
      const response = await notificationService.getNotifications(userId, options);
      if (response.success) {
        setNotifications(response.notifications);
        setUnreadCount(response.unread_count);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  // Mark notifications as read
  const markAsRead = useCallback(async (notificationIds: string[]) => {
    if (!userId || notificationIds.length === 0) return;
    
    try {
      const response = await notificationService.markAsRead(userId, notificationIds);
      if (response.success) {
        // Update local state
        setNotifications(prev => 
          prev.map(n => 
            notificationIds.includes(n.id) ? { ...n, is_read: true } : n
          )
        );
        setUnreadCount(prev => Math.max(0, prev - response.updated_count));
      }
    } catch (error) {
      console.error('Error marking notifications as read:', error);
    }
  }, [userId]);

  // Mark all notifications as read
  const markAllAsRead = useCallback(async () => {
    if (!userId) return;
    
    try {
      const response = await notificationService.markAllAsRead(userId);
      if (response.success) {
        // Update local state
        setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
        setUnreadCount(0);
      }
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  }, [userId]);

  // Delete notification
  const deleteNotification = useCallback(async (notificationId: string) => {
    if (!userId) return;
    
    try {
      const response = await notificationService.deleteNotification(userId, notificationId);
      if (response.success) {
        // Update local state
        const deletedNotification = notifications.find(n => n.id === notificationId);
        setNotifications(prev => prev.filter(n => n.id !== notificationId));
        if (deletedNotification && !deletedNotification.is_read) {
          setUnreadCount(prev => Math.max(0, prev - 1));
        }
      }
    } catch (error) {
      console.error('Error deleting notification:', error);
    }
  }, [userId, notifications]);

  // Fetch preferences
  const fetchPreferences = useCallback(async () => {
    if (!userId) return;
    
    try {
      const response = await notificationService.getPreferences(userId);
      if (response.success) {
        setPreferences(response.preferences);
      }
    } catch (error) {
      console.error('Error fetching notification preferences:', error);
    }
  }, [userId]);

  // Update preferences
  const updatePreferences = useCallback(async (newPreferences: Partial<NotificationPreferences>) => {
    if (!userId) return;
    
    try {
      const response = await notificationService.updatePreferences(userId, newPreferences);
      if (response.success && response.preferences) {
        setPreferences(response.preferences);
      }
    } catch (error) {
      console.error('Error updating notification preferences:', error);
    }
  }, [userId]);

  // Handle notification click
  const handleNotificationClick = useCallback(async (notification: Notification) => {
    // Mark as read if not already read
    if (!notification.is_read) {
      await markAsRead([notification.id]);
    }
    
    // Navigate to link if available
    if (notification.link) {
      window.location.href = notification.link;
    }
  }, [markAsRead]);

  // Dropdown controls
  const openDropdown = useCallback(() => {
    setIsDropdownOpen(true);
    // Fetch notifications when opening dropdown
    fetchNotifications({ limit: 10 });
  }, [fetchNotifications]);

  const closeDropdown = useCallback(() => {
    setIsDropdownOpen(false);
  }, []);

  const toggleDropdown = useCallback(() => {
    if (isDropdownOpen) {
      closeDropdown();
    } else {
      openDropdown();
    }
  }, [isDropdownOpen, openDropdown, closeDropdown]);

  // Initial fetch and polling setup
  useEffect(() => {
    if (userId) {
      // Fetch initial data
      fetchUnreadCount();
      fetchPreferences();
      
      // Set up polling for unread count
      const timer = setInterval(() => {
        fetchUnreadCount();
      }, POLLING_INTERVAL);
      
      setPollingTimer(timer);
      
      // Cleanup
      return () => {
        if (timer) {
          clearInterval(timer);
        }
      };
    }
  }, [userId, fetchUnreadCount, fetchPreferences]);

  // Context value
  const value: NotificationContextType = {
    notifications,
    unreadCount,
    isLoading,
    isDropdownOpen,
    preferences,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    openDropdown,
    closeDropdown,
    toggleDropdown,
    fetchPreferences,
    updatePreferences,
    handleNotificationClick,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

// Custom hook to use notification context
export const useNotifications = (): NotificationContextType => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

export default NotificationContext;
