// Activity Service for Jeseci Smart Learning Academy
// Handles all API communication for user activities and recent activity feed

import { apiService } from './api';

// Activity type definitions
export type ActivityType =
  | 'LESSON_COMPLETED'
  | 'COURSE_STARTED'
  | 'COURSE_COMPLETED'
  | 'QUIZ_PASSED'
  | 'ACHIEVEMENT_EARNED'
  | 'STREAK_MILESTONE'
  | 'LOGIN'
  | 'CONTENT_VIEWED'
  | 'AI_GENERATED'
  | 'LEARNING_PATH_STARTED'
  | 'LEARNING_PATH_COMPLETED'
  | 'CONCEPT_MASTERED'
  | 'BADGE_EARNED';

export interface Activity {
  id: string;
  user_id: string;
  type: ActivityType;
  title: string;
  description?: string;
  metadata?: Record<string, any>;
  xp_earned: number;
  created_at: string;
  config?: ActivityConfig;
}

export interface ActivityConfig {
  icon: string;
  color: string;
  title_template: string;
  xp: number;
}

export interface ActivitySummary {
  total_activities: number;
  today_activities: number;
  total_xp_earned: number;
  activities_by_type: Record<ActivityType, number>;
  timeframe: string;
}

export interface ActivityStreak {
  current_streak: number;
  longest_streak: number;
  last_activity_date?: string;
  streak_start_date?: string;
}

export interface ActivitiesResponse {
  success: boolean;
  activities: Activity[];
  total_count: number;
  has_more: boolean;
  error?: string;
}

export interface ActivitySummaryResponse {
  success: boolean;
  summary: ActivitySummary;
  error?: string;
}

export interface ActivityStreakResponse {
  success: boolean;
  streak: ActivityStreak;
  error?: string;
}

export interface LogActivityResponse {
  success: boolean;
  activity?: Activity;
  message?: string;
  error?: string;
}

// Activity type configuration
export const ACTIVITY_TYPE_CONFIG: Record<ActivityType, { icon: string; color: string; label: string }> = {
  LESSON_COMPLETED: { icon: 'book-open', color: 'blue', label: 'Lesson Completed' },
  COURSE_STARTED: { icon: 'play', color: 'green', label: 'Course Started' },
  COURSE_COMPLETED: { icon: 'check-circle', color: 'emerald', label: 'Course Completed' },
  QUIZ_PASSED: { icon: 'award', color: 'yellow', label: 'Quiz Passed' },
  ACHIEVEMENT_EARNED: { icon: 'trophy', color: 'amber', label: 'Achievement Earned' },
  STREAK_MILESTONE: { icon: 'flame', color: 'orange', label: 'Streak Milestone' },
  LOGIN: { icon: 'user', color: 'gray', label: 'Login' },
  CONTENT_VIEWED: { icon: 'eye', color: 'indigo', label: 'Content Viewed' },
  AI_GENERATED: { icon: 'bot', color: 'purple', label: 'AI Generated' },
  LEARNING_PATH_STARTED: { icon: 'map', color: 'cyan', label: 'Learning Path Started' },
  LEARNING_PATH_COMPLETED: { icon: 'flag', color: 'teal', label: 'Learning Path Completed' },
  CONCEPT_MASTERED: { icon: 'lightbulb', color: 'lime', label: 'Concept Mastered' },
  BADGE_EARNED: { icon: 'medal', color: 'rose', label: 'Badge Earned' },
};

// Activity Service class
class ActivityService {
  private baseUrl = '/walker';

  /**
   * Log a new activity
   */
  async logActivity(
    userId: string,
    activityType: ActivityType,
    title: string,
    options: {
      description?: string;
      metadata?: Record<string, any>;
      xpEarned?: number;
    } = {}
  ): Promise<LogActivityResponse> {
    try {
      const response = await apiService.post(this.baseUrl + '/log_activity', {
        user_id: userId,
        activity_type: activityType,
        title,
        description: options.description || '',
        metadata: options.metadata || {},
        xp_earned: options.xpEarned || 0,
      });

      return {
        success: response.success,
        activity: response.activity,
        message: response.message,
      };
    } catch (error) {
      console.error('Error logging activity:', error);
      return {
        success: false,
        error: 'Failed to log activity',
      };
    }
  }

  /**
   * Get user activities with pagination and filtering
   */
  async getActivities(
    userId: string,
    options: {
      limit?: number;
      offset?: number;
      activityType?: ActivityType | '';
      startDate?: string;
      endDate?: string;
    } = {}
  ): Promise<ActivitiesResponse> {
    try {
      const { limit = 20, offset = 0, activityType = '', startDate, endDate } = options;

      const response = await apiService.post(this.baseUrl + '/get_user_activities', {
        user_id: userId,
        limit,
        offset,
        activity_type: activityType,
        start_date: startDate || '',
        end_date: endDate || '',
      });

      return {
        success: true,
        activities: response.activities || [],
        total_count: response.total_count || 0,
        has_more: response.has_more || false,
      };
    } catch (error) {
      console.error('Error fetching activities:', error);
      return {
        success: false,
        activities: [],
        total_count: 0,
        has_more: false,
        error: 'Failed to fetch activities',
      };
    }
  }

  /**
   * Get activity summary statistics
   */
  async getActivitySummary(
    userId: string,
    timeframe: 'day' | 'week' | 'month' | 'all' = 'week'
  ): Promise<ActivitySummaryResponse> {
    try {
      const response = await apiService.post(this.baseUrl + '/get_activity_summary', {
        user_id: userId,
        timeframe,
      });

      return {
        success: true,
        summary: response.summary || {
          total_activities: 0,
          today_activities: 0,
          total_xp_earned: 0,
          activities_by_type: {},
          timeframe,
        },
      };
    } catch (error) {
      console.error('Error fetching activity summary:', error);
      return {
        success: false,
        summary: {
          total_activities: 0,
          today_activities: 0,
          total_xp_earned: 0,
          activities_by_type: {},
          timeframe,
        },
        error: 'Failed to fetch activity summary',
      };
    }
  }

  /**
   * Get activity streak data
   */
  async getActivityStreak(userId: string): Promise<ActivityStreakResponse> {
    try {
      const response = await apiService.post(this.baseUrl + '/get_activity_streak', {
        user_id: userId,
      });

      return {
        success: true,
        streak: response.streak || {
          current_streak: 0,
          longest_streak: 0,
          last_activity_date: undefined,
          streak_start_date: undefined,
        },
      };
    } catch (error) {
      console.error('Error fetching activity streak:', error);
      return {
        success: false,
        streak: {
          current_streak: 0,
          longest_streak: 0,
          last_activity_date: undefined,
          streak_start_date: undefined,
        },
        error: 'Failed to fetch activity streak',
      };
    }
  }

  /**
   * Delete old activities
   */
  async deleteOldActivities(
    userId: string,
    olderThanDays: number = 365
  ): Promise<{ success: boolean; deletedCount: number; message: string }> {
    try {
      const response = await apiService.post(this.baseUrl + '/delete_user_activities', {
        user_id: userId,
        older_than_days: olderThanDays,
      });

      return {
        success: response.success,
        deletedCount: response.deleted_count || 0,
        message: response.message || 'Activities deleted',
      };
    } catch (error) {
      console.error('Error deleting activities:', error);
      return {
        success: false,
        deletedCount: 0,
        message: 'Failed to delete activities',
      };
    }
  }

  /**
   * Helper: Log lesson completed
   */
  async logLessonCompleted(
    userId: string,
    lessonName: string,
    lessonId: string,
    courseName?: string,
    courseId?: string
  ): Promise<LogActivityResponse> {
    try {
      const response = await apiService.post(this.baseUrl + '/log_lesson_completed', {
        user_id: userId,
        lesson_name: lessonName,
        lesson_id: lessonId,
        course_name: courseName || '',
        course_id: courseId || '',
      });

      return {
        success: response.success,
        activity: response.activity,
        message: response.message,
      };
    } catch (error) {
      console.error('Error logging lesson completed:', error);
      return {
        success: false,
        error: 'Failed to log lesson completion',
      };
    }
  }

  /**
   * Helper: Log quiz passed
   */
  async logQuizPassed(
    userId: string,
    quizName: string,
    quizId: string,
    score: number,
    passingScore: number = 70
  ): Promise<LogActivityResponse> {
    try {
      const response = await apiService.post(this.baseUrl + '/log_quiz_passed', {
        user_id: userId,
        quiz_name: quizName,
        quiz_id: quizId,
        score,
        passing_score: passingScore,
      });

      return {
        success: response.success,
        activity: response.activity,
        message: response.message,
      };
    } catch (error) {
      console.error('Error logging quiz passed:', error);
      return {
        success: false,
        error: 'Failed to log quiz pass',
      };
    }
  }

  /**
   * Helper: Log user login
   */
  async logUserLogin(userId: string): Promise<LogActivityResponse> {
    try {
      const response = await apiService.post(this.baseUrl + '/log_user_login', {
        user_id: userId,
      });

      return {
        success: response.success,
        activity: response.activity,
        message: response.message,
      };
    } catch (error) {
      console.error('Error logging user login:', error);
      return {
        success: false,
        error: 'Failed to log login',
      };
    }
  }

  /**
   * Format relative time from activity creation
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
   * Get color class based on activity type
   */
  getActivityColorClass(activityType: ActivityType): string {
    const config = ACTIVITY_TYPE_CONFIG[activityType];
    if (!config) return 'bg-gray-100 text-gray-600';

    const colorMap: Record<string, string> = {
      blue: 'bg-blue-100 text-blue-600',
      green: 'bg-green-100 text-green-600',
      emerald: 'bg-emerald-100 text-emerald-600',
      yellow: 'bg-yellow-100 text-yellow-600',
      amber: 'bg-amber-100 text-amber-600',
      orange: 'bg-orange-100 text-orange-600',
      gray: 'bg-gray-100 text-gray-600',
      indigo: 'bg-indigo-100 text-indigo-600',
      purple: 'bg-purple-100 text-purple-600',
      cyan: 'bg-cyan-100 text-cyan-600',
      teal: 'bg-teal-100 text-teal-600',
      lime: 'bg-lime-100 text-lime-600',
      rose: 'bg-rose-100 text-rose-600',
    };

    return colorMap[config.color] || 'bg-gray-100 text-gray-600';
  }
}

// Export singleton instance
export const activityService = new ActivityService();
