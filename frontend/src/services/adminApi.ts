/**
 * Admin API Service - Extended API methods for admin operations
 * Handles all admin HTTP requests to the Jaclang REST API
 */

// Admin types
export interface AdminUser {
  user_id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_admin: boolean;
  admin_role: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
  // Soft delete fields
  is_deleted?: boolean;
  deleted_at?: string;
  deleted_by?: string;
}

export interface AdminDashboardStats {
  user_statistics: {
    total_users: number;
    active_users: number;
    inactive_users: number;
    total_admins: number;
    new_users_this_week: number;
  };
  admin_statistics: {
    total_admins: number;
    role_distribution: Record<string, number>;
  };
  system_health: {
    database_status: string;
    api_status: string;
    auth_system: string;
  };
}

export interface AdminStatsResponse {
  success: boolean;
  stats: AdminDashboardStats;
  generated_at: string;
}

export interface AdminUserListResponse {
  success: boolean;
  users: AdminUser[];
  total: number;
  limit: number;
  offset: number;
  filters: {
    include_inactive: boolean;
    admin_only: boolean;
    search: string | null;
  };
}

export interface AdminActionResponse {
  success: boolean;
  message: string;
  user_id?: string;
  action: string;
  timestamp: string;
}

// Course types for admin
export interface AdminCourse {
  course_id: string;
  title: string;
  description: string;
  domain: string;
  difficulty: string;
  content_type: string;
  created_at: string;
  updated_at?: string;
  // Soft delete fields
  is_deleted?: boolean;
  deleted_at?: string;
  deleted_by?: string;
}

export interface AdminConcept {
  concept_id: string;
  name: string;
  display_name: string;
  category: string;
  subcategory: string;
  difficulty_level: string;
  complexity_score: number;
  cognitive_load: number;
  domain: string;
  description?: string;
  icon?: string;
  key_terms: string[];
  synonyms: string[];
}

export interface AdminLearningPath {
  path_id: string;
  title: string;
  description: string;
  courses: string[];
  concepts: string[];
  difficulty: string;
  total_modules: number;
  duration: string;
  target_audience: string;
  concept_count: number;
}

// Quiz types for admin
export interface AdminQuiz {
  quiz_id: string;
  title: string;
  description: string;
  course_id?: string;
  difficulty: string;
  questions_count: number;
  created_at: string;
}

export interface AdminQuizQuestion {
  question_id: string;
  quiz_id: string;
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
}

// Analytics types
export interface AdminAnalytics {
  total_users: number;
  active_learners: number;
  courses_completed: number;
  average_score: number;
  total_study_time: number;
  content_generated: number;
}

// AI Content types
export interface AIGeneratedContentAdmin {
  content_id: string;
  concept_name: string;
  domain: string;
  difficulty: string;
  content: string;
  related_concepts: string[];
  generated_at: string;
  generated_by: string;
}

export interface AIUsageStats {
  total_generations: number;
  total_tokens_used: number;
  domains_used: Record<string, number>;
  recent_generations: AIGeneratedContentAdmin[];
}

export interface Domain {
  id: string;
  name: string;
  description: string;
  course_count: number;
}

// Extend ApiService with admin methods
class AdminApiService {
  private baseUrl: string;
  private authToken: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.authToken = localStorage.getItem('jeseci_auth_token');
  }

  private getAuthHeaders(): HeadersInit {
    return {
      'Content-Type': 'application/json',
      ...(this.authToken ? { 'Authorization': `Bearer ${this.authToken}` } : {}),
    };
  }

  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...this.getAuthHeaders(),
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.message || errorData.error || `HTTP error ${response.status}`);
      }

      const data = await response.json();
      console.log(`Raw Admin API response from ${endpoint}:`, JSON.stringify(data, null, 2));
      
      // Handle Jaclang API response wrapped in reports array
      if (data?.reports && Array.isArray(data.reports) && data.reports.length > 0) {
        const result = data.reports[0];
        console.log(`Admin API extracted from reports:`, result);
        return result;
      }
      
      // Handle response with result field (echoed input data)
      if (data?.result !== undefined && !data?.reports) {
        console.log(`Admin API using result field:`, data.result);
        return data.result;
      }
      
      // Direct response (walker metadata or unwrapped data) - return as-is
      console.log(`Admin API direct response:`, data);
      return data;
    } catch (error) {
      console.error(`Admin API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Dashboard
  async getDashboardStats(): Promise<AdminStatsResponse> {
    return this.makeRequest<AdminStatsResponse>('/walker/admin_dashboard', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  // User Management
  async getUsers(params: {
    limit?: number;
    offset?: number;
    include_inactive?: boolean;
    admin_only?: boolean;
    search?: string;
  } = {}): Promise<AdminUserListResponse> {
    return this.makeRequest<AdminUserListResponse>('/walker/admin_users', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async createAdminUser(userData: {
    username: string;
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
    admin_role: string;
    learning_style?: string;
    skill_level?: string;
    skip_verification?: boolean;
    daily_goal_minutes?: number;
    notifications_enabled?: boolean;
    email_reminders?: boolean;
    dark_mode?: boolean;
    auto_play_videos?: boolean;
  }): Promise<AdminActionResponse> {
    return this.makeRequest<AdminActionResponse>('/walker/admin_users_create', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async updateUser(userId: string, updates: {
    is_admin?: boolean;
    admin_role?: string;
    is_active?: boolean;
  }): Promise<AdminActionResponse> {
    return this.makeRequest<AdminActionResponse>('/walker/admin_users_update', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, ...updates }),
    });
  }

  async bulkUserAction(userIds: string[], action: 'suspend' | 'activate' | 'delete', reason?: string, deletedBy?: string, ipAddress?: string): Promise<AdminActionResponse> {
    return this.makeRequest<AdminActionResponse>('/walker/admin_users_bulk_action', {
      method: 'POST',
      body: JSON.stringify({ user_ids: userIds, action, reason, deleted_by: deletedBy, ip_address: ipAddress }),
    });
  }

  // Restore soft-deleted users
  async restoreUsers(userIds: string[], restoredBy?: string, ipAddress?: string): Promise<AdminActionResponse> {
    return this.makeRequest<AdminActionResponse>('/walker/admin_users_restore', {
      method: 'POST',
      body: JSON.stringify({ user_ids: userIds, restored_by: restoredBy, ip_address: ipAddress }),
    });
  }

  // Get deleted users (trash view)
  async getDeletedUsers(): Promise<{ success: boolean; users: AdminUser[]; total: number }> {
    return this.makeRequest('/walker/admin_users_deleted', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  // Content Management
  async getCourses(): Promise<{ success: boolean; courses: AdminCourse[] }> {
    return this.makeRequest('/walker/admin_content_courses', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async createCourse(courseData: {
    title: string;
    description: string;
    domain: string;
    difficulty: string;
    content_type?: string;
  }): Promise<{ success: boolean; course_id: string; message: string }> {
    return this.makeRequest('/walker/admin_content_courses', {
      method: 'POST',
      body: JSON.stringify(courseData),
    });
  }

  async updateCourse(courseId: string, updates: Partial<AdminCourse>): Promise<{ success: boolean; message: string }> {
    return this.makeRequest('/walker/admin_content_course_update', {
      method: 'POST',
      body: JSON.stringify({ course_id: courseId, ...updates }),
    });
  }

  async deleteCourse(courseId: string, deletedBy?: string, ipAddress?: string): Promise<{ success: boolean; message: string }> {
    return this.makeRequest('/walker/admin_content_course_delete', {
      method: 'POST',
      body: JSON.stringify({ course_id: courseId, deleted_by: deletedBy, ip_address: ipAddress }),
    });
  }

  // Restore soft-deleted course
  async restoreCourse(courseId: string, restoredBy?: string, ipAddress?: string): Promise<{ success: boolean; message: string }> {
    return this.makeRequest('/walker/admin_content_course_restore', {
      method: 'POST',
      body: JSON.stringify({ course_id: courseId, restored_by: restoredBy, ip_address: ipAddress }),
    });
  }

  // Get deleted courses (trash view)
  async getDeletedCourses(): Promise<{ success: boolean; courses: AdminCourse[]; total: number }> {
    return this.makeRequest('/walker/admin_content_courses_deleted', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async getConcepts(): Promise<{ success: boolean; concepts: AdminConcept[] }> {
    return this.makeRequest('/walker/admin_content_concepts', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async getConceptRelationships(): Promise<{
    success: boolean;
    relationships: Array<{
      source_id: string;
      source_name: string;
      source_display: string;
      target_id: string;
      target_name: string;
      target_display: string;
      relationship_type: string;
      strength: number;
    }>;
  }> {
    return this.makeRequest('/walker/admin_content_relationships', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async addConceptRelationship(data: {
    source_id: string;
    target_id: string;
    relationship_type: string;
    strength?: number;
  }): Promise<{ success: boolean; message: string }> {
    return this.makeRequest('/walker/admin_content_relationships_create', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteConceptRelationship(data: {
    source_id: string;
    target_id: string;
    relationship_type: string;
  }): Promise<{ success: boolean; message: string }> {
    return this.makeRequest('/walker/admin_content_relationships_delete', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async createConcept(conceptData: {
    name: string;
    display_name: string;
    category: string;
    difficulty_level: string;
    domain: string;
    description?: string;
    icon?: string;
  }): Promise<{ success: boolean; concept_id: string; message: string }> {
    return this.makeRequest('/walker/admin_content_concepts', {
      method: 'POST',
      body: JSON.stringify(conceptData),
    });
  }

  async getLearningPaths(): Promise<{ success: boolean; paths: AdminLearningPath[] }> {
    return this.makeRequest('/walker/admin_content_paths', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async createLearningPath(pathData: {
    title: string;
    description: string;
    courses: string[];
    concepts: string[];
    difficulty: string;
    duration: string;
    target_audience?: string;
  }): Promise<{ success: boolean; path_id: string; message: string }> {
    return this.makeRequest('/walker/admin_content_path_create', {
      method: 'POST',
      body: JSON.stringify(pathData),
    });
  }

  // Quiz Management
  async getQuizzes(): Promise<{ success: boolean; quizzes: AdminQuiz[] }> {
    return this.makeRequest('/walker/admin_quizzes', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async createQuiz(quizData: {
    title: string;
    description: string;
    course_id?: string;
    difficulty: string;
  }): Promise<{ success: boolean; quiz_id: string; message: string }> {
    return this.makeRequest('/walker/admin_quizzes_create', {
      method: 'POST',
      body: JSON.stringify(quizData),
    });
  }

  async updateQuiz(quizId: string, updates: Partial<AdminQuiz>): Promise<{ success: boolean; message: string }> {
    return this.makeRequest('/walker/admin_quizzes_update', {
      method: 'POST',
      body: JSON.stringify({ quiz_id: quizId, ...updates }),
    });
  }

  async deleteQuiz(quizId: string): Promise<{ success: boolean; message: string }> {
    return this.makeRequest('/walker/admin_quizzes_delete', {
      method: 'POST',
      body: JSON.stringify({ quiz_id: quizId }),
    });
  }

  async generateAIQuiz(request: {
    topic: string;
    difficulty: string;
    question_count?: number;
  }): Promise<{
    success: boolean;
    quiz?: {
      title: string;
      description: string;
      questions: Array<{
        question: string;
        options: string[];
        correct_answer: number;
        explanation: string;
      }>;
    };
    topic: string;
    difficulty: string;
    question_count: number;
    is_sample?: boolean;
    message: string;
  }> {
    return this.makeRequest('/walker/admin_quizzes_generate_ai', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async saveAIQuiz(quizData: {
    title: string;
    description: string;
    questions: Array<{
      question: string;
      options: string[];
      correct_answer: number;
      explanation: string;
    }>;
  }, topic: string, difficulty: string): Promise<{ success: boolean; quiz_id: string; message: string }> {
    return this.makeRequest('/walker/admin_quizzes_save_ai', {
      method: 'POST',
      body: JSON.stringify({ quiz: quizData, topic, difficulty }),
    });
  }

  async getQuizAnalytics(): Promise<{
    success: boolean;
    analytics: {
      total_quizzes: number;
      total_attempts: number;
      average_score: number;
      pass_rate: number;
    };
  }> {
    return this.makeRequest('/walker/admin_quizzes_analytics', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  // AI Content Management
  async getAIContent(): Promise<{ success: boolean; content: AIGeneratedContentAdmin[] }> {
    return this.makeRequest('/walker/admin_ai_content', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async generateAIContent(request: {
    concept_name: string;
    domain: string;
    difficulty: string;
    related_concepts?: string[];
  }): Promise<{ success: boolean; content: AIGeneratedContentAdmin; message: string }> {
    return this.makeRequest('/walker/admin_ai_generate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getAIUsageStats(): Promise<{ success: boolean; stats: AIUsageStats }> {
    return this.makeRequest('/walker/admin_ai_stats', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async getDomains(): Promise<{ success: boolean; domains: Domain[] }> {
    return this.makeRequest('/walker/admin_ai_domains', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  // Analytics - Updated to use new database-backed walkers
  async getUserAnalytics(): Promise<{
    success: boolean;
    analytics: {
      total_users: number;
      active_users: number;
      new_users: number[];
      user_growth: { date: string; count: number }[];
    };
  }> {
    return this.makeRequest('/walker/admin_user_analytics', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async getLearningAnalytics(): Promise<{
    success: boolean;
    analytics: {
      total_sessions: number;
      completed_courses: number;
      average_progress: number;
      learning_trends: { date: string; sessions: number }[];
    };
  }> {
    return this.makeRequest('/walker/admin_learning_analytics', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async getContentAnalytics(): Promise<{
    success: boolean;
    analytics: {
      total_courses: number;
      total_concepts: number;
      popular_content: { title: string; views: number }[];
      content_by_difficulty: Record<string, number>;
    };
  }> {
    return this.makeRequest('/walker/admin_content_analytics', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  // Analytics API Endpoints - For frontend AnalyticsContext.tsx integration
  async getExecutionMetrics(params: {
    startDate?: string;
    endDate?: string;
    language?: string;
    userId?: string;
    courseId?: string;
  } = {}): Promise<{
    success: boolean;
    data: Array<{
      language: string;
      totalRuns: number;
      successfulRuns: number;
      failedRuns: number;
      successRate: number;
      avgRuntimeMs: number;
    }>;
  }> {
    return this.makeRequest('/walker/analytics_executions', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async getEngagementMetrics(params: {
    startDate?: string;
    endDate?: string;
    cohortId?: string;
  } = {}): Promise<{
    success: boolean;
    data: {
      dailyActiveUsers: number;
      weeklyActiveUsers: number;
      monthlyActiveUsers: number;
      avgSessionDuration: number;
      completionRate: number;
    };
  }> {
    return this.makeRequest('/walker/analytics_engagement', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async getPerformanceTrends(params: {
    startDate?: string;
    endDate?: string;
    language?: string;
    userId?: string;
  } = {}): Promise<{
    success: boolean;
    data: Array<{
      date: string;
      executions: number;
      successRate: number;
      avgRuntime: number;
      activeUsers: number;
    }>;
  }> {
    return this.makeRequest('/walker/analytics_trends', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async getActivityData(params: {
    startDate?: string;
    endDate?: string;
    userId?: string;
  } = {}): Promise<{
    success: boolean;
    data: Array<{
      date: string;
      value: number;
    }>;
  }> {
    return this.makeRequest('/walker/analytics_activity', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async getSkillsData(params: {
    userId?: string;
  } = {}): Promise<{
    success: boolean;
    data: Array<{
      category: string;
      skills: Array<{
        id: string;
        name: string;
        level: number;
        maxLevel: number;
        practiceCount: number;
        successRate: number;
      }>;
    }>;
  }> {
    return this.makeRequest('/walker/analytics_skills', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async getStudentPerformance(params: {
    cohortId?: string;
    courseId?: string;
    startDate?: string;
    endDate?: string;
  } = {}): Promise<{
    success: boolean;
    data: Array<{
      userId: string;
      userName: string;
      totalExecutions: number;
      successRate: number;
      avgScore: number;
      completionRate: number;
      engagementScore: number;
      riskLevel: 'low' | 'medium' | 'high';
      riskFactors: string[];
      lastActive: string;
    }>;
    total: number;
  }> {
    return this.makeRequest('/walker/analytics_student_performance', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async getCohortAnalytics(cohortId: string): Promise<{
    success: boolean;
    data: {
      cohortId: string;
      cohortName: string;
      studentCount: number;
      avgSuccessRate: number;
      avgCompletionRate: number;
      avgEngagement: number;
      atRiskCount: number;
      topPerformers: Array<{
        userId: string;
        userName: string;
        avgScore: number;
      }>;
      strugglingStudents: Array<{
        userId: string;
        userName: string;
        avgScore: number;
      }>;
      conceptMastery: Array<{
        conceptId: string;
        conceptName: string;
        masteryLevel: number;
      }>;
    };
  }> {
    return this.makeRequest('/walker/analytics_cohort', {
      method: 'POST',
      body: JSON.stringify({ cohort_id: cohortId }),
    });
  }

  async refreshAnalytics(): Promise<{ success: boolean; message: string }> {
    return this.makeRequest('/walker/admin_analytics_refresh', { method: 'POST' });
  }
}

// Create instance with dynamic API URL for production
const ADMIN_API_BASE_URL = (() => {
  const hostname = window.location.hostname;
  const protocol = window.location.protocol;
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  
  // For production, use same origin (assumes reverse proxy)
  return `${protocol}//${hostname}`;
})();

const adminApiService = new AdminApiService(ADMIN_API_BASE_URL);
export default adminApiService;
