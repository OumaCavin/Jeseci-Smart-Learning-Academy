/**
 * API Service for communicating with Jaclang backend
 * Handles all HTTP requests to the Jaclang REST API
 */

// Dynamic API endpoint configuration for production-ready deployment
function getApiBaseUrl(): string {
  const hostname = window.location.hostname;
  const protocol = window.location.protocol;
  
  // Use localhost for local development
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  
  // For production deployments, use the same origin
  // This assumes the backend runs on the same domain (e.g., via reverse proxy)
  return `${protocol}//${hostname}`;
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
  is_verified?: boolean;
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
}

export interface Course {
  course_id: string;
  title: string;
  description: string;
  domain: string;
  difficulty: string;
  content_type: string;
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
  concept_id: string;
  name: string;
  display_name: string;
  category: string;
  difficulty_level: string;
  description?: string;
}

export interface PlatformStats {
  total_users: number;
  total_courses: number;
  total_lessons: number;
  active_learners_today: number;
}

export interface PlatformStatsResponse {
  success: boolean;
  stats?: PlatformStats;
  error?: string;
}

export interface Testimonial {
  id: string;
  name: string;
  role: string;
  content: string;
  avatar_url?: string;
  rating: number;
}

export interface TestimonialsResponse {
  success: boolean;
  testimonials: Testimonial[];
  error?: string;
}

// Code Execution Interfaces
export interface CodeSnippet {
  snippet_id: string;
  user_id: string;
  title: string;
  code: string;
  language: string;
  description?: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface ExecutionRequest {
  code: string;
  language: string;
  input?: string;
  timeout?: number;
}

export interface ExecutionResponse {
  success: boolean;
  output: string;
  error?: string;
  execution_time: number;
  memory_used?: number;
  logs?: string[];
}

export interface ExecutionLog {
  log_id: string;
  user_id: string;
  snippet_id?: string;
  code: string;
  language: string;
  output: string;
  status: 'success' | 'error' | 'timeout';
  execution_time: number;
  memory_used?: number;
  created_at: string;
}

export interface CodeSnippetRequest {
  title: string;
  code: string;
  language: string;
  description?: string;
  is_public?: boolean;
}

export interface CodeExecutionResponse {
  success: boolean;
  output?: string;
  error?: string;
  execution_time?: number;
  memory_used?: number;
  test_results?: TestResult[];
  error_suggestion?: ErrorSuggestion;
}

export interface SnippetsListResponse {
  success: boolean;
  snippets?: CodeSnippet[];
  error?: string;
}

export interface SnippetVersion {
  id: string;
  snippet_id: string;
  version_number: number;
  code_content: string;
  title: string;
  description?: string;
  created_by: number;
  change_summary?: string;
  created_at: string;
}

export interface TestCase {
  id: string;
  snippet_id: string;
  name: string;
  input_data?: string;
  expected_output: string;
  is_hidden: boolean;
  order_index: number;
  timeout_ms: number;
  created_by?: number;
  created_at: string;
}

export interface TestResult {
  id: string;
  test_case_id: string;
  execution_id: string;
  passed: boolean;
  actual_output: string;
  execution_time_ms: number;
  error_message?: string;
  created_at: string;
}

export interface ErrorSuggestion {
  title: string;
  description: string;
  suggestion: string;
  documentation_link?: string;
  examples?: string[];
}

export interface DebugSession {
  id: string;
  snippet_id: string;
  status: 'running' | 'paused' | 'completed';
  current_line?: number;
  variables?: Record<string, any>;
}

export interface SnippetVersionResponse {
  success: boolean;
  versions?: SnippetVersion[];
  error?: string;
}

export interface TestCaseResponse {
  success: boolean;
  test_cases?: TestCase[];
  error?: string;
}

export interface TestResultsResponse {
  success: boolean;
  test_results?: TestResult[];
  passed_count?: number;
  total_count?: number;
  error?: string;
}

export interface DebugSessionResponse {
  success: boolean;
  session?: DebugSession;
  current_line?: number;
  variables?: Record<string, any>;
  status?: 'running' | 'paused' | 'completed';
  output?: string;
  error?: string;
}

export interface CreateVersionResponse {
  success: boolean;
  version?: SnippetVersion;
  error?: string;
}

export interface CreateTestCaseResponse {
  success: boolean;
  test_case?: TestCase;
  error?: string;
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

export interface JaclangServiceHealth {
  service: string;
  status: string;
  jac_available: boolean;
  version: string;
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
    // Handle Jaclang API response wrapped in reports array
    if (response?.reports && Array.isArray(response.reports) && response.reports.length > 0) {
      // Extract from reports array
      const report = response.reports[0];
      if (typeof report === 'object' && !Array.isArray(report)) {
        console.log('API extracted from reports:', report);
        return report;
      }
      console.log('API extracted from reports (non-object):', report);
      return report;
    }
    
    // Handle direct response data (when reports array is not present)
    if (typeof response === 'object' && !Array.isArray(response)) {
      console.log('API direct response:', response);
      return response;
    }
    
    console.log('API fallback response:', response);
    return response;
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

  // Platform Stats
  async getPlatformStats(): Promise<PlatformStatsResponse> {
    return this.makeRequest('/walker/platform_stats', {
      method: 'GET',
    });
  }

  // Testimonials
  async getTestimonials(limit: number = 6, featuredOnly: boolean = false): Promise<TestimonialsResponse> {
    return this.makeRequest('/walker/testimonials', {
      method: 'POST',
      body: JSON.stringify({
        limit,
        featured_only: featuredOnly
      }),
    });
  }

  // Code Execution
  async executeCode(code: string, language: string = 'jac', mode: string = 'run', timeout?: number): Promise<CodeExecutionResponse> {
    return this.makeRequest('/walker/code_execute', {
      method: 'POST',
      body: JSON.stringify({
        code,
        language,
        mode,
        timeout: timeout || 30
      }),
    });
  }

  // Legacy code execution with different response format
  async executeJacCode(code: string): Promise<any> {
    return this.makeRequest('/walker/code_execute', {
      method: 'POST',
      body: JSON.stringify({
        code,
        language: 'jac'
      }),
    });
  }

  async saveCodeSnippet(snippetData: CodeSnippetRequest): Promise<any> {
    return this.makeRequest('/walker/code_snippet', {
      method: 'POST',
      body: JSON.stringify({
        action: 'save',
        ...snippetData
      }),
    });
  }

  async getCodeSnippets(userId?: string): Promise<SnippetsListResponse> {
    return this.makeRequest('/walker/code_snippet', {
      method: 'POST',
      body: JSON.stringify({
        action: 'list',
        user_id: userId || this.authToken ? undefined : undefined
      }),
    });
  }

  async getCodeSnippet(snippetId: string): Promise<any> {
    return this.makeRequest('/walker/code_snippet', {
      method: 'POST',
      body: JSON.stringify({
        action: 'get',
        snippet_id: snippetId
      }),
    });
  }

  async deleteCodeSnippet(snippetId: string): Promise<any> {
    return this.makeRequest('/walker/code_snippet', {
      method: 'POST',
      body: JSON.stringify({
        action: 'delete',
        snippet_id: snippetId
      }),
    });
  }

  // Code Editor legacy methods (for backward compatibility with CodeEditor component)
  async getUserSnippets(): Promise<any> {
    try {
      const response = await this.makeRequest('/walker/code_snippet', {
        method: 'POST',
        body: JSON.stringify({ action: 'list' }),
      });
      return { success: true, snippets: response };
    } catch (error) {
      return { success: false, error: 'Failed to load snippets', snippets: [] };
    }
  }

  async getCodeFolders(): Promise<any> {
    // Return empty folders for now - folder management can be added later
    return { success: true, folders: [] };
  }

  async getExecutionHistory(): Promise<any> {
    // Return empty history for now - execution logging can be enhanced later
    return { success: true, history: [] };
  }

  async saveSnippet(data: { title: string; code: string; language?: string; description?: string; snippet_id?: string }): Promise<any> {
    return this.saveCodeSnippet({
      title: data.title,
      code: data.code,
      description: data.description,
      language: data.language || 'jac'
    });
  }

  async createFolder(data: { name: string; description?: string; parent_folder_id?: string }): Promise<any> {
    // Folder creation can be implemented later
    return { success: true, folder: { id: Date.now().toString(), name: data.name } };
  }

  async deleteSnippet(snippetId: string): Promise<any> {
    return this.deleteCodeSnippet(snippetId);
  }

  // Snippet versions
  async getSnippetVersions(snippetId: string): Promise<SnippetVersionResponse> {
    return this.makeRequest('/walker/snippet_version', {
      method: 'POST',
      body: JSON.stringify({
        action: 'list',
        snippet_id: snippetId
      }),
    });
  }

  async createVersion(snippetId: string, code: string, title: string, versionNumber: number, description?: string): Promise<CreateVersionResponse> {
    return this.makeRequest('/walker/snippet_version', {
      method: 'POST',
      body: JSON.stringify({
        action: 'create',
        snippet_id: snippetId,
        code,
        title,
        version_number: versionNumber,
        description
      }),
    });
  }

  // Test cases
  async getSnippetTestCases(snippetId: string): Promise<TestCaseResponse> {
    return this.makeRequest('/walker/test_case', {
      method: 'POST',
      body: JSON.stringify({
        action: 'list',
        snippet_id: snippetId
      }),
    });
  }

  async createTestCase(data: {
    snippet_id: string;
    name: string;
    input_data: string;
    expected_output: string;
    is_hidden?: boolean;
  }): Promise<CreateTestCaseResponse> {
    return this.makeRequest('/walker/test_case', {
      method: 'POST',
      body: JSON.stringify({
        action: 'create',
        ...data
      }),
    });
  }

  // Debug sessions
  async createDebugSession(snippetId: string): Promise<DebugSessionResponse> {
    return this.makeRequest('/walker/debug_session', {
      method: 'POST',
      body: JSON.stringify({
        action: 'create',
        snippet_id: snippetId
      }),
    });
  }

  async debugStep(sessionId: string, action: string): Promise<DebugSessionResponse> {
    return this.makeRequest('/walker/debug_session', {
      method: 'POST',
      body: JSON.stringify({
        action: action,
        session_id: sessionId
      }),
    });
  }

  // ============================================================================
  // Jaclang Editor Intelligence Service
  // ============================================================================

  /**
   * Check the health of the Jaclang service
   */
  async getJaclangServiceHealth(): Promise<JaclangServiceHealth> {
    return this.makeRequest('/api/jaclang/health', {
      method: 'GET',
    });
  }

  /**
   * Validate Jaclang source code for syntax errors
   * @param sourceCode - The Jaclang code to validate
   * @returns Validation result with any syntax errors
   */
  async validateJacCode(sourceCode: string): Promise<JaclangValidationResponse> {
    return this.makeRequest('/api/jaclang/validate', {
      method: 'POST',
      body: JSON.stringify({
        source_code: sourceCode
      }),
    });
  }

  /**
   * Format Jaclang source code according to language standards
   * @param sourceCode - The Jaclang code to format
   * @returns Formatted code and whether it changed
   */
  async formatJacCode(sourceCode: string): Promise<JaclangFormatResponse> {
    return this.makeRequest('/api/jaclang/format', {
      method: 'POST',
      body: JSON.stringify({
        source_code: sourceCode
      }),
    });
  }

  /**
   * Validate and format Jaclang code in a single request
   * @param sourceCode - The Jaclang code to validate and format
   * @returns Combined validation and formatting result
   */
  async validateAndFormatJacCode(sourceCode: string): Promise<{
    valid: boolean;
    errors: JaclangValidationError[];
    formatted_code: string;
    changed: boolean;
    message: string;
  }> {
    return this.makeRequest('/api/jaclang/validate-and-format', {
      method: 'POST',
      body: JSON.stringify({
        source_code: sourceCode
      }),
    });
  }
}

export const apiService = new ApiService();
export default ApiService;