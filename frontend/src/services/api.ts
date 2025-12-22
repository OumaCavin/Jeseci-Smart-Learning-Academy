/**
 * API Service for communicating with Jaclang backend
 * Handles all HTTP requests to the Jaclang REST API
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
  domain: str = "Computer Science";
  difficulty: str = "beginner";
  content_type: str = "interactive";
}

export interface LearningPathModule {
  id: string;
  title: string;
  type: 'lesson' | 'project' | 'quiz';
  duration: string;
  completed: boolean;
}

export interface LearningPath {
  id: string;
  title: string;
  description: string;
  courses: string[];
  modules: LearningPathModule[];
  concepts: string[];
  skills_covered: string[];
  prerequisites: string[];
  total_modules: number;
  completed_modules: number;
  duration: string;
  estimated_hours: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  progress: number;
  icon: string;
  category: string;
  next_step: string;
  last_activity?: string;
}

export interface Concept {
  id: string;
  name: string;
  description: string;
  domain: str = "Computer Science";
  difficulty: str = "beginner";
  icon: str = "💡";
  related_concepts: string[];
}

export interface Quiz {
  id: string;
  title: string;
  description: string;
  questions: QuizQuestion[];
  difficulty: str = "beginner";
  estimated_time: number;
  completed: boolean;
  score?: number;
}

export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: str = "🏆";
  earned: boolean;
  earned_at?: string;
  requirement: string;
  category: str = "learning";
}

export interface ChatMessage {
  id: number;
  role: str = "user";
  content: string;
  timestamp: str;
}

export interface LearningSession {
  session_id: string;
  user_id: string;
  module_id: string;
  status: str;
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
  learning_style: str;
  skill_level: str;
  recent_activity?: Array<{
    session_id: str;
    course_id: str;
    course_title: str;
    status: str;
    progress: number;
    started_at?: str;
    completed_at?: str;
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
    learning_velocity: str;
    generated_at: str;
  };
  recommendations: string[];
  strengths: string[];
  areas_for_improvement: string[];
}

export interface AIGeneratedContent {
  success: boolean;
  concept_name: str;
  domain: str;
  difficulty: str;
  content: string;
  related_concepts: string[];
  generated_at: str;
  source?: str;
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: str = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async makeRequest<T>(endpoint: str, options: RequestInit = {}): Promise<T> {
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
        throw new Error(errorData.detail || errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Health and Status
  async healthCheck(): Promise<any> {
    return this.makeRequest('/walker/health_check', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async getWelcome(): Promise<any> {
    return this.makeRequest('/walker/init', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  // Authentication
  async login(username: str, password: str): Promise<LoginResponse> {
    return this.makeRequest('/walker/user_login', {
      method: 'POST',
      body: JSON.stringify({
        username,
        password
      }),
    });
  }

  async register(userData: {
    username: str;
    email: str;
    password: str;
    first_name?: str;
    last_name?: str;
    learning_style?: str;
    skill_level?: str;
  }): Promise<any> {
    console.log('Sending registration request to:', `${this.baseUrl}/walker/user_create`);
    console.log('Registration data:', userData);
    const result = this.makeRequest('/walker/user_create', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    console.log('Registration response:', result);
    return result;
  }

  // Course Management
  async createCourse(courseData: {
    title: str;
    description: str;
    domain: str;
    difficulty: str;
    content_type?: str;
  }): Promise<any> {
    return this.makeRequest('/walker/course_create', {
      method: 'POST',
      body: JSON.stringify(courseData),
    });
  }

  async getCourses(): Promise<Course[]> {
    return this.makeRequest('/walker/courses', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  // Learning Paths
  async getLearningPaths(): Promise<LearningPath[]> {
    return this.makeRequest('/walker/learning_paths', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  // Concepts
  async getConcepts(): Promise<Concept[]> {
    return this.makeRequest('/walker/concepts', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  // Quizzes
  async getQuizzes(): Promise<Quiz[]> {
    return this.makeRequest('/walker/quizzes', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async submitQuiz(quizId: str, answers: number[]): Promise<any> {
    return this.makeRequest('/walker/quiz_submit', {
      method: 'POST',
      body: JSON.stringify({
        quiz_id: quizId,
        answers: answers
      }),
    });
  }

  // Achievements / Motivator
  async getAchievements(userId: str): Promise<Achievement[]> {
    return this.makeRequest('/walker/achievements', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId
      }),
    });
  }

  // Chat
  async sendChatMessage(message: str): Promise<any> {
    return this.makeRequest('/walker/chat', {
      method: 'POST',
      body: JSON.stringify({
        message: message
      }),
    });
  }

  // Learning Sessions
  async startLearningSession(userId: str, moduleId: str): Promise<LearningSession> {
    return this.makeRequest('/walker/learning_session_start', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        module_id: moduleId
      }),
    });
  }

  async endLearningSession(sessionId: str, progress: number): Promise<any> {
    return this.makeRequest('/walker/learning_session_end', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        progress: progress
      }),
    });
  }

  // Progress Tracking
  async getUserProgress(userId: str): Promise<ProgressData> {
    return this.makeRequest('/walker/user_progress', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId
      }),
    });
  }

  async getAnalytics(userId: str): Promise<AnalyticsData> {
    return this.makeRequest('/walker/analytics_generate', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId
      }),
    });
  }

  // AI Content Generation
  async generateAIContent(conceptName: str, domain: str, difficulty: str, relatedConcepts: string[] = []): Promise<AIGeneratedContent> {
    return this.makeRequest('/walker/ai_generate_content', {
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
  async exportData(format: str = "json"): Promise<any> {
    return this.makeRequest('/walker/export_data', {
      method: 'POST',
      body: JSON.stringify({
        format: format
      }),
    });
  }
}

export const apiService = new ApiService();
export default ApiService;
