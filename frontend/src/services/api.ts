/**
 * API Service for communicating with Jaclang backend
 * Handles all HTTP requests to the Jaclang REST API
 */

// Dynamic API endpoint configuration
function getApiBaseUrl(): string {
  const hostname = window.location.hostname;
  
  // Use localhost for local development
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  
  // For production, use the placeholder URL
  // TODO: Replace with actual production backend URL
  return 'https://your-production-backend-url.com';
}

const API_BASE_URL = getApiBaseUrl();

export interface User {
  user_id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  learning_style: string;
  skill_level: string;
  is_active?: boolean;
  is_email_verified?: boolean;
  is_verified?: boolean;
  is_admin?: boolean;
  admin_role?: string;
  last_login?: string;
  created_at?: string;
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
  code?: string;
  message?: string;
  requires_verification?: boolean;
  is_email_verified?: boolean;
  email?: string;
}

export interface Course {
  course_id: string;
  title: string;
  description: string;
  domain: string;
  difficulty: string;
  content_type: string;
  estimated_duration?: string;
  concept_count?: number;
  lesson_count?: number;
  is_enrolled?: boolean;
  progress?: number;
}

export interface CourseDetails {
  course_id: string;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  estimated_duration?: string;
  is_published: boolean;
  created_at?: string;
  updated_at?: string;
  concepts: Array<{
    concept_id: string;
    name: string;
    description?: string;
    order_index: number;
  }>;
  lessons: Array<{
    lesson_id: string;
    title: string;
    description?: string;
    order_index: number;
    duration_minutes?: number;
  }>;
  concept_count: number;
  lesson_count: number;
  is_enrolled: boolean;
  progress: number;
  enrollment?: {
    enrolled_at?: string;
    last_accessed?: string;
    progress_percent: number;
  };
}

export interface LearningPathModule {
  id: string;
  title: string;
  type: 'lesson' | 'project' | 'quiz';
  duration: string;
  completed: boolean;
  order_index?: number;
  concepts?: string[];
  description?: string;
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
  is_enrolled?: boolean;
}

export interface LearningPathDetails {
  id: string;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  estimated_duration?: number;
  target_audience: string;
  is_published: boolean;
  is_enrolled: boolean;
  progress: number;
  concepts: Array<{
    concept_id: string;
    name: string;
    description?: string;
    order_index: number;
    is_required: boolean;
  }>;
  modules: LearningPathModule[];
  prerequisites: string[];
  skills_covered: string[];
  enrollment?: {
    enrolled_at?: string;
    last_accessed?: string;
    progress_percent: number;
  };
  created_at?: string;
  updated_at?: string;
}

export interface Concept {
  id: string;
  concept_id: string;
  name: string;
  display_name: string;
  category: string;
  difficulty_level: string;
  difficulty: string; // Add alias for App compatibility
  domain: string; // Add domain property
  icon: string; // Add icon property
  description?: string;
}

export interface Quiz {
  id: string;
  title: string;
  description: string;
  questions: QuizQuestion[];
  difficulty: string;
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
  icon: string;
  earned: boolean;
  earned_at?: string;
  requirement: string;
  category: string;
}

export interface ChatMessage {
  id: number;
  role: string;
  content: string;
  timestamp: string;
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

// Jaclang Editor Intelligence Interfaces
export interface JaclangValidationError {
  line: number;
  column: number;
  message: string;
  severity: 'Error' | 'Warning' | 'Info';
  raw?: string;
}

export interface JaclangValidationResponse {
  valid: boolean;
  errors: JaclangValidationError[];
  message: string;
}

export interface JaclangFormatResponse {
  formatted_code: string;
  changed: boolean;
  error?: string;
}

export interface JaclangHealthResponse {
  service: string;
  status: string;
  jac_available: boolean;
  version: string;
}

// AI Code Assistant Interfaces
export type AIAnalysisType = 'security' | 'performance' | 'bug' | 'best_practice' | 'style' | 'comprehensive';
export type AISeverity = 'error' | 'warning' | 'info';

export interface AICodeIssue {
  id: string;
  type: AIAnalysisType;
  severity: AISeverity;
  line: number;
  column: number;
  message: string;
  explanation: string;
  suggestion: string;
  code_diff?: {
    before: string;
    after: string;
  };
}

export interface AIAnalysisMetrics {
  complexity: 'low' | 'medium' | 'high';
  linesOfCode: number;
  issuesCount: number;
}

export interface AIAnalysisResponse {
  success: boolean;
  issues: AICodeIssue[];
  metrics: AIAnalysisMetrics;
  summary: string;
  error?: string;
}

export interface AIChatResponse {
  success: boolean;
  response: string;
  timestamp: string;
  fallback?: boolean;
}

export interface AICodeHealthResponse {
  success: boolean;
  available: boolean;
  model: string;
  service: string;
}

class ApiService {
  private baseUrl: string;
  private authToken: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
    // Load token from localStorage
    this.authToken = localStorage.getItem('jeseci_auth_token');
  }

  private setAuthToken(token: string) {
    this.authToken = token;
    localStorage.setItem('jeseci_auth_token', token);
  }

  private clearAuthToken() {
    this.authToken = null;
    localStorage.removeItem('jeseci_auth_token');
  }

  private extractJacData<T>(response: any): T {
    // Handle case where response is already the data we need
    if (!response) {
      return response as T;
    }

    // Jaclang API via jac serve returns data in a specific format
    // Check for reports array format (native Jaclang walker response)
    if (response?.reports && Array.isArray(response.reports) && response.reports.length > 0) {
      const report = response.reports[0];
      
      // If report is an object with success property, extract the inner data
      if (typeof report === 'object' && report !== null && !Array.isArray(report)) {
        // Some endpoints return {success: true, data: [...]}
        // Others return {success: true, concepts: [...]}
        // Others return just {...}
        if (report.success === true || report.success === undefined) {
          // Check for authentication responses with user and token properties
          // These responses have multiple important properties we must preserve
          if ('access_token' in report || 'token' in report || 'user' in report || 'message' in report) {
            return report as T;
          }
          
          // Check for nested array properties and return the array value
          const arrayKeys = ['data', 'results', 'items', 'concepts', 'paths', 
                            'courses', 'quizzes', 'achievements', 'modules',
                            'concepts_list', 'paths_list', 'courses_list',
                            'snippets', 'files', 'activities'];
          for (const key of arrayKeys) {
            if (Array.isArray(report[key])) {
              return report[key] as unknown as T;
            }
          }
          
          // If no array properties, count non-success object properties
          // Only extract if there's exactly one object property (like progress)
          // Don't extract if there are multiple mixed properties (like login)
          const objectKeys = Object.keys(report).filter(key => 
            key !== 'success' && typeof report[key] === 'object' && report[key] !== null
          );
          if (objectKeys.length === 1) {
            return report[objectKeys[0]] as unknown as T;
          }
          
          // If no suitable property found or multiple properties, return the whole report
          return report as T;
        }
        // If success is false, return the report with error info
        return report as T;
      }
      
      // If report is an array, return it directly
      if (Array.isArray(report)) {
        return report as T;
      }
      
      return report as T;
    }
    
    // Handle direct response data (already unwrapped or standard API response)
    // This handles the Pure Jaclang API format: {success: true, concepts: [...], total: n}
    if (typeof response === 'object' && response !== null) {
      // Check for success property first
      if ('success' in response) {
        if (response.success === true) {
          // Check for authentication responses with user and token properties
          // These responses have multiple important properties we must preserve
          if ('access_token' in response || 'token' in response || 'user' in response || 'message' in response) {
            return response as T;
          }
          
          // Check for array properties first - this handles the standard wrapper format
          // {success: true, concepts: [...], total: n}
          const arrayKeys = ['data', 'results', 'items', 'concepts', 'paths', 
                            'courses', 'quizzes', 'achievements', 'modules',
                            'concepts_list', 'paths_list', 'courses_list',
                            'snippets', 'files', 'activities'];
          for (const key of arrayKeys) {
            if (Array.isArray(response[key])) {
              return response[key] as unknown as T;
            }
          }
          
          // Only extract single object property (not for login with multiple properties)
          const objectKeys = Object.keys(response).filter(key => 
            key !== 'success' && typeof response[key] === 'object' && response[key] !== null
          );
          if (objectKeys.length === 1) {
            return response[objectKeys[0]] as unknown as T;
          }
        }
        // For unsuccessful responses, return the full response for error handling
        return response as T;
      }
      // If no success property, return as-is
      return response as T;
    }
    
    return response as T;
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

    // Add authorization header if token exists
    if (this.authToken) {
      defaultOptions.headers = {
        ...defaultOptions.headers,
        'Authorization': `Bearer ${this.authToken}`,
      };
    }

    try {
      const response = await fetch(url, defaultOptions);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        
        // Handle authentication errors
        if (response.status === 401) {
          this.clearAuthToken();
          throw new Error('Authentication required. Please login again.');
        }
        
        throw new Error(errorData.error || errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Extract the actual data from Jaclang response format
      return this.extractJacData<T>(data);
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  async post<T = any>(endpoint: string, body: any): Promise<T> {
    return this.makeRequest<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async get<T = any>(endpoint: string, options?: { params?: Record<string, any> }): Promise<T> {
    let url = endpoint;
    if (options?.params) {
      const searchParams = new URLSearchParams();
      Object.entries(options.params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value));
        }
      });
      const queryString = searchParams.toString();
      if (queryString) {
        url += `?${queryString}`;
      }
    }
    return this.makeRequest<T>(url, {
      method: 'GET',
    });
  }

  // Health and Status
  async healthCheck(): Promise<any> {
    return this.makeRequest('/walker/health_check', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  // Jaclang Editor Intelligence Methods
  async validateJacCode(sourceCode: string): Promise<JaclangValidationResponse> {
    try {
      const response = await this.makeRequest<JaclangValidationResponse>('/api/jaclang/validate', {
        method: 'POST',
        body: JSON.stringify({ source_code: sourceCode }),
      });
      return response;
    } catch (error) {
      console.error('Jaclang validation failed:', error);
      return {
        valid: true,
        errors: [],
        message: 'Validation service unavailable'
      };
    }
  }

  async formatJacCode(sourceCode: string): Promise<JaclangFormatResponse> {
    try {
      const response = await this.makeRequest<JaclangFormatResponse>('/walker/jaclang_format', {
        method: 'POST',
        body: JSON.stringify({ source_code: sourceCode }),
      });
      return response;
    } catch (error) {
      console.error('Jaclang formatting failed:', error);
      return {
        formatted_code: sourceCode,
        changed: false,
        error: 'Formatting service unavailable'
      };
    }
  }

  async validateAndFormatJacCode(sourceCode: string): Promise<any> {
    try {
      const response = await this.makeRequest('/api/jaclang/validate-and-format', {
        method: 'POST',
        body: JSON.stringify({ source_code: sourceCode }),
      });
      return response;
    } catch (error) {
      console.error('Jaclang validate-and-format failed:', error);
      return {
        valid: true,
        errors: [],
        formatted_code: sourceCode,
        changed: false,
        message: 'Service unavailable'
      };
    }
  }

  async jaclangHealthCheck(): Promise<JaclangHealthResponse> {
    try {
      const response = await this.makeRequest<JaclangHealthResponse>('/api/jaclang/health', {
        method: 'GET',
      });
      return response;
    } catch (error) {
      console.error('Jaclang health check failed:', error);
      return {
        service: 'Jaclang Editor Intelligence',
        status: 'unavailable',
        jac_available: false,
        version: 'not available'
      };
    }
  }

  // AI Code Assistant Methods
  async aiAnalyzeCode(
    code: string,
    language: string = 'jac',
    analysisTypes: string = 'comprehensive'
  ): Promise<AIAnalysisResponse> {
    try {
      const response = await this.makeRequest<AIAnalysisResponse>('/walker/ai_analyze_code', {
        method: 'POST',
        body: JSON.stringify({
          code,
          language,
          analysis_types: analysisTypes
        }),
      });
      return response;
    } catch (error) {
      console.error('AI code analysis failed:', error);
      return {
        success: true,
        issues: [],
        metrics: { complexity: 'medium', linesOfCode: code.split('\n').length, issuesCount: 0 },
        summary: 'AI analysis unavailable',
        error: 'Service error'
      };
    }
  }

  async aiChatAboutCode(
    message: string,
    codeContext: string = '',
    chatHistory: Array<{ role: string; content: string }> = []
  ): Promise<AIChatResponse> {
    try {
      const response = await this.makeRequest<AIChatResponse>('/walker/ai_chat_about_code', {
        method: 'POST',
        body: JSON.stringify({
          message,
          code_context: codeContext,
          chat_history: JSON.stringify(chatHistory)
        }),
      });
      return response;
    } catch (error) {
      console.error('AI chat failed:', error);
      return {
        success: true,
        response: "I'm sorry, but I'm having trouble connecting to the AI service right now. Please try again later.",
        timestamp: new Date().toISOString(),
        fallback: true
      };
    }
  }

  async aiCodeHealthCheck(): Promise<AICodeHealthResponse> {
    try {
      const response = await this.makeRequest<AICodeHealthResponse>('/walker/ai_code_health', {
        method: 'POST',
        body: JSON.stringify({}),
      });
      return response;
    } catch (error) {
      console.error('AI code health check failed:', error);
      return {
        success: true,
        available: false,
        model: 'not available',
        service: 'AI Code Intelligence'
      };
    }
  }

  async getWelcome(): Promise<any> {
    return this.makeRequest('/walker/init', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  // Authentication
  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await this.makeRequest<LoginResponse>('/walker/user_login', {
      method: 'POST',
      body: JSON.stringify({
        username,
        password
      }),
    });

    if (response.success && response.access_token) {
      this.setAuthToken(response.access_token);
    }

    return response;
  }

  async register(userData: {
    username: string;
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
    learning_style?: string;
    skill_level?: string;
  }): Promise<LoginResponse> {
    console.log('Sending registration request to:', `${this.baseUrl}/walker/user_create`);
    console.log('Registration data:', userData);
    
    const result = await this.makeRequest<LoginResponse>('/walker/user_create', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    console.log('Registration response:', result);
    
    // If registration was successful
    if (result.success) {
      console.log('Registration successful, email verification required:', result.requires_verification);
      
      // Only auto-login if email verification is NOT required
      if (!result.requires_verification) {
        console.log('Performing auto-login...');
        const loginResult = await this.login(userData.username, userData.password);
        console.log('Auto-login result:', loginResult);
        return loginResult;
      } else {
        // Email verification required - return the registration success but no token
        console.log('Email verification required, returning registration result');
        return {
          success: true,
          user: result.user,
          requires_verification: true,
          message: result.message || 'Registration successful. Please check your email to verify your account.',
          error: null
        };
      }
    }
    
    return result;
  }

  // Email Verification
  async verifyEmail(token: string): Promise<any> {
    const response = await this.makeRequest('/walker/verify_email', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token }),
    });
    return response;
  }

  async resendVerificationEmail(email: string): Promise<any> {
    const response = await this.makeRequest('/walker/resend_verification', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });
    return response;
  }

  async getVerificationStatus(userId: string): Promise<any> {
    const response = await this.makeRequest('/walker/verification_status', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    });
    return response;
  }

  // Course Management
  async createCourse(courseData: {
    title: string;
    description: string;
    domain: string;
    difficulty: string;
    content_type?: string;
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

  async enrollInCourse(courseId: string): Promise<any> {
    return this.makeRequest('/walker/enroll_in_course', {
      method: 'POST',
      body: JSON.stringify({
        course_id: courseId
      }),
    });
  }

  async getCourseDetails(courseId: string): Promise<CourseDetails> {
    return this.makeRequest('/walker/get_course_details', {
      method: 'POST',
      body: JSON.stringify({
        course_id: courseId
      }),
    });
  }

  // Learning Paths
  async getLearningPaths(): Promise<LearningPath[]> {
    return this.makeRequest('/walker/get_learning_paths', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async getLearningPathDetails(pathId: string): Promise<LearningPathDetails> {
    return this.makeRequest('/walker/get_learning_path_details', {
      method: 'POST',
      body: JSON.stringify({
        path_id: pathId
      }),
    });
  }

  async enrollInLearningPath(pathId: string): Promise<any> {
    return this.makeRequest('/walker/enroll_in_learning_path', {
      method: 'POST',
      body: JSON.stringify({
        path_id: pathId
      }),
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

  async submitQuiz(quizId: string, answers: number[]): Promise<any> {
    return this.makeRequest('/walker/quiz_submit', {
      method: 'POST',
      body: JSON.stringify({
        quiz_id: quizId,
        answers: answers
      }),
    });
  }

  // Achievements / Motivator
  async getAchievements(userId: string): Promise<Achievement[]> {
    return this.makeRequest('/walker/achievements', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId
      }),
    });
  }

  // Chat
  async sendChatMessage(message: string): Promise<any> {
    return this.makeRequest('/walker/chat', {
      method: 'POST',
      body: JSON.stringify({
        message: message
      }),
    });
  }

  // Chat Export
  async exportChatToEmail(
    email: string,
    chatMessages: Array<{role: string; content: string; timestamp: string}>,
    userName: string = "User"
  ): Promise<any> {
    return this.makeRequest('/walker/export_chat', {
      method: 'POST',
      body: JSON.stringify({
        email: email,
        chat_messages: chatMessages,
        user_name: userName
      }),
    });
  }

  // Learning Sessions
  async startLearningSession(userId: string, moduleId: string): Promise<LearningSession> {
    return this.makeRequest('/walker/learning_session_start', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        module_id: moduleId
      }),
    });
  }

  async endLearningSession(sessionId: string, progress: number): Promise<any> {
    return this.makeRequest('/walker/learning_session_end', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        progress: progress
      }),
    });
  }

  // Progress Tracking
  async getUserProgress(userId: string): Promise<ProgressData> {
    return this.makeRequest('/walker/user_progress', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId
      }),
    });
  }

  async getAnalytics(userId: string): Promise<AnalyticsData> {
    return this.makeRequest('/walker/analytics_generate', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId
      }),
    });
  }

  // AI Content Generation
  async generateAIContent(conceptName: string, domain: string, difficulty: string, relatedConcepts: string[] = []): Promise<AIGeneratedContent> {
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
  async exportData(format: string = "json"): Promise<any> {
    return this.makeRequest('/walker/export_data', {
      method: 'POST',
      body: JSON.stringify({
        format: format
      }),
    });
  }

  // Password Reset
  async forgotPassword(email: string): Promise<any> {
    return this.makeRequest('/walker/forgot_password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  }

  async validateResetToken(token: string): Promise<any> {
    return this.makeRequest('/walker/reset_password_validate', {
      method: 'POST',
      body: JSON.stringify({ token }),
    });
  }

  async resetPassword(token: string, newPassword: string, confirmPassword: string): Promise<any> {
    return this.makeRequest('/walker/reset_password', {
      method: 'POST',
      body: JSON.stringify({
        token,
        new_password: newPassword,
        confirm_password: confirmPassword
      }),
    });
  }

  // =============================================================================
  // CODE SNIPPET MANAGEMENT
  // =============================================================================

  async executeCode(code: string, entryPoint: string = "main"): Promise<any> {
    return this.makeRequest('/walker/execute_code', {
      method: 'POST',
      body: JSON.stringify({
        code,
        entry_point: entryPoint
      }),
    });
  }

  async compileCode(code: string): Promise<any> {
    return this.makeRequest('/walker/compile_code', {
      method: 'POST',
      body: JSON.stringify({ code }),
    });
  }

  async saveSnippet(snippet: {
    title: string;
    code: string;
    description?: string;
    is_public?: boolean;
    folder_id?: string;
    snippet_id?: string;
  }): Promise<any> {
    return this.makeRequest('/walker/save_snippet', {
      method: 'POST',
      body: JSON.stringify(snippet),
    });
  }

  async getSnippets(folderId?: string, limit: number = 50, offset: number = 0): Promise<any> {
    return this.makeRequest('/walker/get_snippets', {
      method: 'POST',
      body: JSON.stringify({
        folder_id: folderId || "",
        limit,
        offset
      }),
    });
  }

  async getSnippet(snippetId: string): Promise<any> {
    return this.makeRequest('/walker/get_snippet', {
      method: 'POST',
      body: JSON.stringify({ snippet_id: snippetId }),
    });
  }

  async deleteSnippet(snippetId: string): Promise<any> {
    return this.makeRequest('/walker/delete_snippet', {
      method: 'POST',
      body: JSON.stringify({ snippet_id: snippetId }),
    });
  }

  async getExecutionHistory(limit: number = 20, offset: number = 0): Promise<any> {
    return this.makeRequest('/walker/get_execution_history', {
      method: 'POST',
      body: JSON.stringify({ limit, offset }),
    });
  }

  // =============================================================================
  // FOLDER MANAGEMENT
  // =============================================================================

  async createFolder(name: string, description?: string, parentFolderId?: string, color?: string): Promise<any> {
    return this.makeRequest('/walker/create_folder', {
      method: 'POST',
      body: JSON.stringify({
        name,
        description: description || "",
        parent_folder_id: parentFolderId || "",
        color: color || "#3b82f6"
      }),
    });
  }

  async getFolders(parentFolderId?: string): Promise<any> {
    return this.makeRequest('/walker/get_folders', {
      method: 'POST',
      body: JSON.stringify({
        parent_folder_id: parentFolderId || ""
      }),
    });
  }

  // =============================================================================
  // VERSION CONTROL
  // =============================================================================

  async snippetVersion(action: string, params: {
    snippet_id?: string;
    version_id?: string;
    code?: string;
    title?: string;
    version_number?: number;
    description?: string;
    change_summary?: string;
  } = {}): Promise<any> {
    return this.makeRequest('/walker/snippet_version', {
      method: 'POST',
      body: JSON.stringify({
        action,
        ...params
      }),
    });
  }

  // =============================================================================
  // TEST CASE MANAGEMENT
  // =============================================================================

  async testCase(action: string, params: {
    snippet_id?: string;
    test_case_id?: string;
    name?: string;
    input_data?: string;
    expected_output?: string;
    is_hidden?: boolean;
    order_index?: number;
    timeout_ms?: number;
  } = {}): Promise<any> {
    return this.makeRequest('/walker/test_case', {
      method: 'POST',
      body: JSON.stringify({
        action,
        ...params
      }),
    });
  }

  // =============================================================================
  // DEBUG SESSION MANAGEMENT
  // =============================================================================

  async debugSession(action: string, params: {
    session_id?: string;
    snippet_id?: string;
    breakpoint_line?: number;
    variables?: string[];
    current_line?: number;
    command?: string;
  } = {}): Promise<any> {
    return this.makeRequest('/walker/debug_session', {
      method: 'POST',
      body: JSON.stringify({
        action,
        ...params
      }),
    });
  }

  // =============================================================================
  // USER PROFILE MANAGEMENT
  // =============================================================================

  async getUserProfile(): Promise<any> {
    return this.makeRequest('/walker/user_profile', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async updateProfile(profileData: {
    first_name?: string;
    last_name?: string;
    bio?: string;
    avatar_url?: string;
  }): Promise<any> {
    return this.makeRequest('/walker/update_profile', {
      method: 'POST',
      body: JSON.stringify(profileData),
    });
  }

  async updatePreferences(preferences: {
    learning_style?: string;
    skill_level?: string;
    daily_goal_minutes?: number;
    preferred_difficulty?: string;
    preferred_content_type?: string;
    notifications_enabled?: boolean;
    email_reminders?: boolean;
    dark_mode?: boolean;
    auto_play_videos?: boolean;
  }): Promise<any> {
    return this.makeRequest('/walker/update_preferences', {
      method: 'POST',
      body: JSON.stringify(preferences),
    });
  }

  async getLearningStreak(): Promise<any> {
    return this.makeRequest('/walker/learning_streak', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  // =============================================================================
  // NOTIFICATION SYSTEM
  // =============================================================================

  async getNotifications(): Promise<any> {
    return this.makeRequest('/walker/notifications', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async getNotificationDetails(notificationId: string): Promise<any> {
    return this.makeRequest('/walker/notification_details', {
      method: 'POST',
      body: JSON.stringify({ notification_id: notificationId }),
    });
  }

  async markNotificationRead(notificationId: string): Promise<any> {
    return this.makeRequest('/walker/notifications_mark_read', {
      method: 'POST',
      body: JSON.stringify({ notification_id: notificationId }),
    });
  }

  async markAllNotificationsRead(): Promise<any> {
    return this.makeRequest('/walker/notifications_mark_all_read', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async deleteNotification(notificationId: string): Promise<any> {
    return this.makeRequest('/walker/notifications_delete', {
      method: 'POST',
      body: JSON.stringify({ notification_id: notificationId }),
    });
  }

  async getNotificationSettings(): Promise<any> {
    return this.makeRequest('/walker/notification_settings', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async updateNotificationSettings(settings: {
    email_notifications?: boolean;
    push_notifications?: boolean;
    course_updates?: boolean;
    community_mentions?: boolean;
    achievement_alerts?: boolean;
    weekly_digest?: boolean;
    marketing_emails?: boolean;
  }): Promise<any> {
    return this.makeRequest('/walker/notification_preferences', {
      method: 'POST',
      body: JSON.stringify(settings),
    });
  }

  // =============================================================================
  // COMMUNITY FEATURES
  // =============================================================================

  async getCommunityUsers(limit: number = 20, offset: number = 0): Promise<any> {
    return this.makeRequest('/walker/community_users', {
      method: 'POST',
      body: JSON.stringify({ limit, offset }),
    });
  }

  async getCommunityPosts(limit: number = 20, offset: number = 0): Promise<any> {
    return this.makeRequest('/walker/community_posts', {
      method: 'POST',
      body: JSON.stringify({ limit, offset }),
    });
  }

  async createCommunityPost(postData: {
    content: string;
    tags?: string[];
    is_public?: boolean;
  }): Promise<any> {
    return this.makeRequest('/walker/community_create_post', {
      method: 'POST',
      body: JSON.stringify(postData),
    });
  }

  async getCommunityComments(postId: string): Promise<any> {
    return this.makeRequest('/walker/community_comments', {
      method: 'POST',
      body: JSON.stringify({ post_id: postId }),
    });
  }

  async addCommunityComment(postId: string, content: string, parentCommentId?: string): Promise<any> {
    return this.makeRequest('/walker/community_add_comment', {
      method: 'POST',
      body: JSON.stringify({
        post_id: postId,
        content,
        parent_comment_id: parentCommentId || ""
      }),
    });
  }

  async addCommunityReaction(postId: string, reactionType: string): Promise<any> {
    return this.makeRequest('/walker/community_reactions', {
      method: 'POST',
      body: JSON.stringify({
        post_id: postId,
        reaction_type: reactionType,
        action: "add"
      }),
    });
  }

  async removeCommunityReaction(postId: string, reactionType: string): Promise<any> {
    return this.makeRequest('/walker/community_reactions', {
      method: 'POST',
      body: JSON.stringify({
        post_id: postId,
        reaction_type: reactionType,
        action: "remove"
      }),
    });
  }

  async followUser(userId: string): Promise<any> {
    return this.makeRequest('/walker/community_follows', {
      method: 'POST',
      body: JSON.stringify({
        target_user_id: userId,
        action: "follow"
      }),
    });
  }

  async unfollowUser(userId: string): Promise<any> {
    return this.makeRequest('/walker/community_follows', {
      method: 'POST',
      body: JSON.stringify({
        target_user_id: userId,
        action: "unfollow"
      }),
    });
  }

  async getFollowing(limit: number = 20, offset: number = 0): Promise<any> {
    return this.makeRequest('/walker/community_follows', {
      method: 'POST',
      body: JSON.stringify({
        action: "list",
        limit,
        offset
      }),
    });
  }

  async getFollowers(userId: string, limit: number = 20, offset: number = 0): Promise<any> {
    return this.makeRequest('/walker/community_follows', {
      method: 'POST',
      body: JSON.stringify({
        target_user_id: userId,
        action: "followers",
        limit,
        offset
      }),
    });
  }

  async sendCommunityMessage(userId: string, content: string): Promise<any> {
    return this.makeRequest('/walker/community_messages', {
      method: 'POST',
      body: JSON.stringify({
        target_user_id: userId,
        content,
        action: "send"
      }),
    });
  }

  async getCommunityMessages(userId: string, limit: number = 50, offset: number = 0): Promise<any> {
    return this.makeRequest('/walker/community_messages', {
      method: 'POST',
      body: JSON.stringify({
        target_user_id: userId,
        action: "list",
        limit,
        offset
      }),
    });
  }

  async getTrendingContent(): Promise<any> {
    return this.makeRequest('/walker/community_trending', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async getCommunityFeed(limit: number = 20, offset: number = 0): Promise<any> {
    return this.makeRequest('/walker/community_feed', {
      method: 'POST',
      body: JSON.stringify({ limit, offset }),
    });
  }

  async getCommunityAnalytics(): Promise<any> {
    return this.makeRequest('/walker/community_analytics', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  // =============================================================================
  // CONTENT INTERACTIONS
  // =============================================================================

  async getContentViews(): Promise<any> {
    return this.makeRequest('/walker/content_views', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async likeContent(contentId: string, contentType: string): Promise<any> {
    return this.makeRequest('/walker/content_like', {
      method: 'POST',
      body: JSON.stringify({
        content_id: contentId,
        content_type: contentType,
        action: "like"
      }),
    });
  }

  async unlikeContent(contentId: string, contentType: string): Promise<any> {
    return this.makeRequest('/walker/content_like', {
      method: 'POST',
      body: JSON.stringify({
        content_id: contentId,
        content_type: contentType,
        action: "unlike"
      }),
    });
  }

  async saveContent(contentId: string, contentType: string, folderId?: string): Promise<any> {
    return this.makeRequest('/walker/content_save', {
      method: 'POST',
      body: JSON.stringify({
        content_id: contentId,
        content_type: contentType,
        folder_id: folderId || "",
        action: "save"
      }),
    });
  }

  async unsaveContent(contentId: string, contentType: string): Promise<any> {
    return this.makeRequest('/walker/content_save', {
      method: 'POST',
      body: JSON.stringify({
        content_id: contentId,
        content_type: contentType,
        action: "unsave"
      }),
    });
  }

  async getSavedContent(): Promise<any> {
    return this.makeRequest('/walker/content_save', {
      method: 'POST',
      body: JSON.stringify({ action: "list" }),
    });
  }

  async shareContent(contentId: string, contentType: string, platform?: string): Promise<any> {
    return this.makeRequest('/walker/content_share', {
      method: 'POST',
      body: JSON.stringify({
        content_id: contentId,
        content_type: contentType,
        platform: platform || "link"
      }),
    });
  }

  // =============================================================================
  // ACTIVITY TRACKING
  // =============================================================================

  async getRecentActivity(limit: number = 10): Promise<any> {
    return this.makeRequest('/walker/recent_activity', {
      method: 'POST',
      body: JSON.stringify({ limit }),
    });
  }

  // =============================================================================
  // STATIC METHOD ALIASES (for backward compatibility)
  // =============================================================================

  static async getFollowers(userId?: string, limit: number = 20, offset: number = 0): Promise<any> {
    const instance = new ApiService();
    return userId ? instance.getFollowers(userId, limit, offset) : instance.getFollowing(limit, offset);
  }

  static async getFollowing(limit: number = 20, offset: number = 0): Promise<any> {
    const instance = new ApiService();
    return instance.getFollowing(limit, offset);
  }

  static async followUser(userId: string): Promise<any> {
    const instance = new ApiService();
    return instance.followUser(userId);
  }

  static async unfollowUser(userId: string): Promise<any> {
    const instance = new ApiService();
    return instance.unfollowUser(userId);
  }

  static async getSavedContent(): Promise<any> {
    const instance = new ApiService();
    return instance.getSavedContent();
  }

  static async removeSavedContent(contentId: string): Promise<any> {
    const instance = new ApiService();
    return instance.makeRequest('/walker/saved_content', {
      method: 'POST',
      body: JSON.stringify({
        action: "remove",
        content_id: contentId
      }),
    });
  }
}

export const apiService = new ApiService();
export default ApiService;