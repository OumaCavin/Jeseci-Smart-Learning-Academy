/**
 * API Service for communicating with FastAPI backend
 * Handles all HTTP requests to the backend API
 */

const API_BASE_URL = 'http://localhost:8000';

export interface User {
  user_id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  learning_style: string;
  skill_level: string;
  is_active: boolean;
  is_verified: boolean;
  last_login: string;
  created_at: string;
  progress?: Record<string, any>;
}

export interface LoginResponse {
  success: boolean;
  access_token?: string;
  token?: string;
  token_type?: string;
  expires_in?: number;
  user?: User;
  username?: string;
  root_id?: string;
  error?: string;
}

export interface Course {
  course_id: string;
  title: string;
  description: string;
  domain: string;
  difficulty: string;
  content_type: string;
}

export interface LearningSession {
  session_id: string;
  user_id: string;
  module_id: string;
  status: string;
  progress: number;
}

export interface ProgressData {
  user_id: string;
  progress: {
    courses_completed: number;
    lessons_completed: number;
    total_study_time: number;
    current_streak: number;
    average_score: number;
  };
  analytics: {
    completion_rate: number;
    total_sessions: number;
    completed_sessions: number;
    in_progress_sessions: number;
    average_progress: number;
  };
  learning_style: string;
  skill_level: string;
  recent_activity?: Array<{
    session_id: string;
    course_id: string;
    course_title: string;
    status: string;
    progress: number;
    started_at?: string;
    completed_at?: string;
  }>;
}

export interface AnalyticsData {
  user_id: string;
  learning_analytics: {
    modules_completed: number;
    total_study_time: number;
    average_score: number;
    engagement_score: number;
    knowledge_retention: number;
    learning_velocity: string;
    generated_at: string;
  };
  recommendations: string[];
  strengths: string[];
  areas_for_improvement: string[];
}

export interface AIGeneratedContent {
  success: boolean;
  concept_name: string;
  domain: string;
  difficulty: string;
  content: string;
  related_concepts: string[];
  generated_at: string;
  source?: string;
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, defaultOptions);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Health and Status
  async healthCheck(): Promise<any> {
    return this.makeRequest('/health');
  }

  async getWelcome(): Promise<any> {
    return this.makeRequest('/walker/init', {
      method: 'GET',
    });
  }

  // Authentication
  async login(username: string, password: string): Promise<LoginResponse> {
    return this.makeRequest('/user/login', {
      method: 'POST',
      body: JSON.stringify({
        username,
        password
      }),
    });
  }

  async register(userData: {
    username: string;
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
    learning_style?: string;
    skill_level?: string;
  }): Promise<any> {
    console.log('Sending registration request to:', `${this.baseUrl}/user/create`);
    console.log('Registration data:', userData);
    const result = this.makeRequest('/user/create', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    console.log('Registration response:', result);
    return result;
  }

  // Course Management
  async createCourse(courseData: {
    title: string;
    description: string;
    domain: string;
    difficulty: string;
    content_type?: string;
  }): Promise<any> {
    return this.makeRequest('/course/create', {
      method: 'POST',
      body: JSON.stringify(courseData),
    });
  }

  async getCourses(): Promise<Course[]> {
    return this.makeRequest('/courses');
  }

  // Learning Sessions
  async startLearningSession(userId: string, moduleId: string): Promise<LearningSession> {
    return this.makeRequest('/learning/session/start', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        module_id: moduleId
      }),
    });
  }

  async endLearningSession(sessionId: string, progress: number): Promise<any> {
    return this.makeRequest('/learning/session/end', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        progress: progress
      }),
    });
  }

  // Progress Tracking
  async getUserProgress(userId: string): Promise<ProgressData> {
    return this.makeRequest('/user/progress', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId
      }),
    });
  }

  async getAnalytics(userId: string): Promise<AnalyticsData> {
    return this.makeRequest('/analytics/generate', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId
      }),
    });
  }

  // AI Content Generation
  async generateAIContent(conceptName: string, domain: string, difficulty: string, relatedConcepts: string[] = []): Promise<AIGeneratedContent> {
    return this.makeRequest('/ai/generate/content', {
      method: 'POST',
      body: JSON.stringify({
        concept_name: conceptName,
        domain: domain,
        difficulty: difficulty,
        related_concepts: relatedConcepts
      }),
    });
  }

  // Data Export
  async exportData(format: string = 'json'): Promise<any> {
    return this.makeRequest('/export/data', {
      method: 'POST',
      body: JSON.stringify({
        format: format
      }),
    });
  }
}

export const apiService = new ApiService();
export default ApiService;
