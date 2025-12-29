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
}

export interface AdminConcept {
  concept_id: string;
  name: string;
  display_name: string;
  category: string;
  difficulty_level: string;
  domain: string;
  description?: string;
  icon?: string;
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
      return data;
    } catch (error) {
      console.error(`Admin API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Dashboard
  async getDashboardStats(): Promise<AdminStatsResponse> {
    return this.makeRequest<AdminStatsResponse>('/walker/admin_dashboard', {
      method: 'GET',
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
    const queryParams = new URLSearchParams();
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.offset) queryParams.append('offset', params.offset.toString());
    if (params.include_inactive) queryParams.append('include_inactive', 'true');
    if (params.admin_only) queryParams.append('admin_only', 'true');
    if (params.search) queryParams.append('search', params.search);

    return this.makeRequest<AdminUserListResponse>(`/walker/admin_users?${queryParams}`, {
      method: 'GET',
    });
  }

  async createAdminUser(userData: {
    username: string;
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
    admin_role: string;
    skip_verification?: boolean;
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
      method: 'PUT',
      body: JSON.stringify({ user_id: userId, ...updates }),
    });
  }

  async bulkUserAction(userIds: string[], action: 'suspend' | 'activate' | 'delete', reason?: string): Promise<AdminActionResponse> {
    return this.makeRequest<AdminActionResponse>('/walker/admin_users_bulk_action', {
      method: 'POST',
      body: JSON.stringify({ user_ids: userIds, action, reason }),
    });
  }

  // Content Management
  async getCourses(): Promise<{ success: boolean; courses: AdminCourse[] }> {
    return this.makeRequest('/walker/admin_content_courses', { method: 'GET' });
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
    return this.makeRequest(`/walker/admin_content_courses/${courseId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deleteCourse(courseId: string): Promise<{ success: boolean; message: string }> {
    return this.makeRequest(`/walker/admin_content_courses/${courseId}`, { method: 'DELETE' });
  }

  async getConcepts(): Promise<{ success: boolean; concepts: AdminConcept[] }> {
    return this.makeRequest('/walker/admin_content_concepts', { method: 'GET' });
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
    return this.makeRequest('/walker/admin_content_paths', { method: 'GET' });
  }

  // Quiz Management
  async getQuizzes(): Promise<{ success: boolean; quizzes: AdminQuiz[] }> {
    return this.makeRequest('/walker/admin_quizzes', { method: 'GET' });
  }

  async createQuiz(quizData: {
    title: string;
    description: string;
    course_id?: string;
    difficulty: string;
  }): Promise<{ success: boolean; quiz_id: string; message: string }> {
    return this.makeRequest('/walker/admin_quizzes', {
      method: 'POST',
      body: JSON.stringify(quizData),
    });
  }

  async updateQuiz(quizId: string, updates: Partial<AdminQuiz>): Promise<{ success: boolean; message: string }> {
    return this.makeRequest(`/walker/admin_quizzes/${quizId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deleteQuiz(quizId: string): Promise<{ success: boolean; message: string }> {
    return this.makeRequest(`/walker/admin_quizzes/${quizId}`, { method: 'DELETE' });
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
    return this.makeRequest('/walker/admin_quizzes_analytics', { method: 'GET' });
  }

  // AI Content Management
  async getAIContent(): Promise<{ success: boolean; content: AIGeneratedContentAdmin[] }> {
    return this.makeRequest('/walker/admin_ai_content', { method: 'GET' });
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
    return this.makeRequest('/walker/admin_ai_stats', { method: 'GET' });
  }

  async getDomains(): Promise<{ success: boolean; domains: Domain[] }> {
    return this.makeRequest('/walker/admin_ai_domains', { method: 'GET' });
  }

  // Analytics
  async getUserAnalytics(): Promise<{
    success: boolean;
    analytics: {
      total_users: number;
      active_users: number;
      new_users: number[];
      user_growth: { date: string; count: number }[];
    };
  }> {
    return this.makeRequest('/walker/admin_analytics_users', { method: 'GET' });
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
    return this.makeRequest('/walker/admin_analytics_learning', { method: 'GET' });
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
    return this.makeRequest('/walker/admin_analytics_content', { method: 'GET' });
  }

  async refreshAnalytics(): Promise<{ success: boolean; message: string }> {
    return this.makeRequest('/walker/admin_analytics_refresh', { method: 'POST' });
  }
}

// Create instance
const adminApiService = new AdminApiService('http://localhost:8000');
export default adminApiService;
