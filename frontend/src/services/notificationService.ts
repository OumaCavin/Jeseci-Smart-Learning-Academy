// Notification Service for Jeseci Smart Learning Academy
// Handles all API communication for in-app notifications

import { apiService } from './api';

// Notification type definitions
export interface Notification {
  id: string;
  user_id: string;
  type: NotificationType;
  title: string;
  message: string;
  link?: string;
  is_read: boolean;
  is_archived: boolean;
  metadata?: Record<string, any>;
  created_at: string;
}

export type NotificationType = 
  | 'ACHIEVEMENT'
  | 'COURSE_MILESTONE'
  | 'CONTENT_UPDATE'
  | 'COMMUNITY_REPLY'
  | 'STREAK_REMINDER'
  | 'AI_RESPONSE'
  | 'SYSTEM_ANNOUNCEMENT';

export interface NotificationPreferences {
  user_id: string;
  email_enabled: boolean;
  push_enabled: boolean;
  types_config: Record<NotificationType, boolean>;
  created_at?: string;
  updated_at?: string;
}

export interface NotificationsResponse {
  success: boolean;
  notifications: Notification[];
  total_count: number;
  unread_count: number;
  has_more: boolean;
  error?: string;
}

export interface UnreadCountResponse {
  success: boolean;
  unread_count: number;
  error?: string;
}

export interface MarkReadResponse {
  success: boolean;
  updated_count: number;
  message: string;
  error?: string;
}

export interface NotificationSettingsResponse {
  success: boolean;
  preferences: NotificationPreferences;
  error?: string;
}

// Notification type icons and colors
export const NOTIFICATION_TYPE_CONFIG: Record<NotificationType, { icon: string; color: string; label: string }> = {
  ACHIEVEMENT: { icon: 'trophy', color: 'text-yellow-600 bg-yellow-100', label: 'Achievement' },
  COURSE_MILESTONE: { icon: 'graduation-cap', color: 'text-blue-600 bg-blue-100', label: 'Course Progress' },
  CONTENT_UPDATE: { icon: 'book-open', color: 'text-green-600 bg-green-100', label: 'New Content' },
  COMMUNITY_REPLY: { icon: 'message-circle', color: 'text-purple-600 bg-purple-100', label: 'Community' },
  STREAK_REMINDER: { icon: 'flame', color: 'text-orange-600 bg-orange-100', label: 'Streak' },
  AI_RESPONSE: { icon: 'bot', color: 'text-indigo-600 bg-indigo-100', label: 'AI Assistant' },
  SYSTEM_ANNOUNCEMENT: { icon: 'bell', color: 'text-gray-600 bg-gray-100', label: 'System' },
};

// Notification Service class
class NotificationService {
  private baseUrl = '/walker';

  /**
   * Fetch notifications for the current user
   */
  async getNotifications(
    userId: string,
    options: {
      limit?: number;
      offset?: number;
      filterType?: NotificationType | '';
      unreadOnly?: boolean;
    } = {}
  ): Promise<NotificationsResponse> {
    try {
      const { limit = 20, offset = 0, filterType = '', unreadOnly = false } = options;

      const response = await apiService.post(this.baseUrl + '/get_notifications', {
        user_id: userId,
        limit,
        offset,
        filter_type: filterType,
        unread_only: unreadOnly,
      });

      return response;
    } catch (error) {
      console.error('Error fetching notifications:', error);
      return {
        success: false,
        notifications: [],
        total_count: 0,
        unread_count: 0,
        has_more: false,
        error: 'Failed to fetch notifications',
      };
    }
  }

  /**
   * Get unread notification count for the current user
   */
  async getUnreadCount(userId: string): Promise<UnreadCountResponse> {
    try {
      const response = await apiService.post(this.baseUrl + '/get_unread_count', {
        user_id: userId,
      });

      return {
        success: true,
        unread_count: response.unread_count || 0,
      };
    } catch (error) {
      console.error('Error fetching unread count:', error);
      return {
        success: false,
        unread_count: 0,
        error: 'Failed to fetch unread count',
      };
    }
  }

  /**
   * Mark one or more notifications as read
   */
  async markAsRead(userId: string, notificationIds: string[]): Promise<MarkReadResponse> {
    try {
      const response = await apiService.post(this.baseUrl + '/mark_notification_read', {
        user_id: userId,
        notification_ids: notificationIds,
      });

      return {
        success: response.success,
        updated_count: response.updated_count || 0,
        message: response.message || 'Notifications marked as read',
      };
    } catch (error) {
      console.error('Error marking notifications as read:', error);
      return {
        success: false,
        updated_count: 0,
        message: 'Failed to mark notifications as read',
      };
    }
  }

  /**
   * Mark all notifications as read for the current user
   */
  async markAllAsRead(userId: string): Promise<MarkReadResponse> {
    try {
      const response = await apiService.post(this.baseUrl + '/mark_all_notifications_read', {
        user_id: userId,
      });

      return {
        success: response.success,
        updated_count: response.updated_count || 0,
        message: response.message || 'All notifications marked as read',
      };
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      return {
        success: false,
        updated_count: 0,
        message: 'Failed to mark all notifications as read',
      };
    }
  }

  /**
   * Delete a notification (soft delete)
   */
  async deleteNotification(userId: string, notificationId: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await apiService.post(this.baseUrl + '/delete_notification', {
        user_id: userId,
        notification_id: notificationId,
      });

      return {
        success: response.success,
        message: response.message || 'Notification deleted',
      };
    } catch (error) {
      console.error('Error deleting notification:', error);
      return {
        success: false,
        message: 'Failed to delete notification',
      };
    }
  }

  /**
   * Get notification preferences for the current user
   */
  async getPreferences(userId: string): Promise<NotificationSettingsResponse> {
    try {
      const response = await apiService.post(this.baseUrl + '/get_notification_preferences', {
        user_id: userId,
      });

      return {
        success: true,
        preferences: response.preferences || this.getDefaultPreferences(userId),
      };
    } catch (error) {
      console.error('Error fetching notification preferences:', error);
      return {
        success: false,
        preferences: this.getDefaultPreferences(userId),
        error: 'Failed to fetch preferences',
      };
    }
  }

  /**
   * Update notification preferences for the current user
   */
  async updatePreferences(
    userId: string,
    preferences: Partial<NotificationPreferences>
  ): Promise<NotificationSettingsResponse> {
    try {
      const response = await apiService.post(this.baseUrl + '/update_notification_preferences', {
        user_id: userId,
        email_enabled: preferences.email_enabled ?? true,
        push_enabled: preferences.push_enabled ?? true,
        types_config: preferences.types_config,
      });

      if (response.success && response.preferences) {
        return {
          success: true,
          preferences: response.preferences,
        };
      }

      return {
        success: false,
        preferences: this.getDefaultPreferences(userId),
        error: response.error || 'Failed to update preferences',
      };
    } catch (error) {
      console.error('Error updating notification preferences:', error);
      return {
        success: false,
        preferences: this.getDefaultPreferences(userId),
        error: 'Failed to update preferences',
      };
    }
  }

  /**
   * Get default notification preferences
   */
  getDefaultPreferences(userId: string): NotificationPreferences {
    return {
      user_id: userId,
      email_enabled: true,
      push_enabled: true,
      types_config: {
        ACHIEVEMENT: true,
        COURSE_MILESTONE: true,
        CONTENT_UPDATE: true,
        COMMUNITY_REPLY: true,
        STREAK_REMINDER: true,
        AI_RESPONSE: true,
        SYSTEM_ANNOUNCEMENT: true,
      },
    };
  }

  /**
   * Format relative time from notification creation
   */
  formatRelativeTime(createdAt: string): string {
    const now = new Date();
    const created = new Date(createdAt);
    const diffMs = now.getTime() - created.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffSecs < 60) {
      return 'Just now';
    } else if (diffMins < 60) {
      return `${diffMins}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    } else {
      return created.toLocaleDateString();
    }
  }

  /**
   * Truncate text with ellipsis
   */
  truncateText(text: string, maxLength: number): string {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3) + '...';
  }
}

// Export singleton instance
export const notificationService = new NotificationService();
