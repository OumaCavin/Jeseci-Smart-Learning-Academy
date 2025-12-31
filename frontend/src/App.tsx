import React, { useState, useEffect, useContext } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { apiService, User, ProgressData, AnalyticsData, AIGeneratedContent, LearningPath, Concept, Quiz, Achievement, ChatMessage } from './services/api';
import { AdminProvider, useAdmin } from './contexts/AdminContext';
import { AdminLayout, DashboardOverview, UserManagement, ContentManager, QuizManager, AILab, AnalyticsReports } from './admin';
import LandingPageWithNavigation, { HelpCenterPage, ContactPage, PrivacyPage, TermsPage } from './components/LandingPage';
import VerifyEmail from './pages/VerifyEmail';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import './App.css';

// =============================================================================
// ADMIN PAGE COMPONENT
// =============================================================================

const AdminPage: React.FC = () => {
  const { isAdminAuthenticated, adminUser, loading, login, logout } = useAdmin();
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [loginError, setLoginError] = useState('');
  const [adminLoading, setAdminLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAdminLoading(true);
    setLoginError('');
    try {
      await login(loginForm.username, loginForm.password);
    } catch (err: any) {
      setLoginError(err.message || 'Login failed');
    } finally {
      setAdminLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="App loading">
        <div className="loading-spinner">
          <h1>🎓 Jeseci Academy</h1>
          <p>Loading admin session...</p>
        </div>
      </div>
    );
  }

  if (!isAdminAuthenticated) {
    return (
      <div className="App">
        <div className="auth-container" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div className="auth-card" style={{ maxWidth: '400px' }}>
            <h2 style={{ marginBottom: '8px' }}>🔐 Admin Login</h2>
            <p style={{ color: '#6b7280', marginBottom: '24px' }}>
              Enter your admin credentials to access the admin panel
            </p>
            
            {loginError && (
              <div style={{ padding: '12px', background: '#fee2e2', color: '#dc2626', borderRadius: '8px', marginBottom: '16px' }}>
                {loginError}
              </div>
            )}

            <form onSubmit={handleLogin}>
              <div className="form-group">
                <label className="form-label">Username</label>
                <input
                  type="text"
                  className="form-input"
                  value={loginForm.username}
                  onChange={(e) => setLoginForm(f => ({ ...f, username: e.target.value }))}
                  placeholder="Enter username"
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Password</label>
                <input
                  type="password"
                  className="form-input"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm(f => ({ ...f, password: e.target.value }))}
                  placeholder="Enter password"
                  required
                />
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={adminLoading}>
                {adminLoading ? 'Logging in...' : 'Login to Admin Panel'}
              </button>
            </form>

            <div style={{ marginTop: '24px', textAlign: 'center' }}>
              <a href="/" style={{ color: '#2563eb', textDecoration: 'none' }}>← Back to Student Portal</a>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <AdminLayout>
      {(props: { activeSection: string }) => {
        switch (props.activeSection) {
          case 'dashboard':
            return <DashboardOverview activeSection={props.activeSection} />;
          case 'users':
            return <UserManagement activeSection={props.activeSection} />;
          case 'content':
            return <ContentManager activeSection={props.activeSection} />;
          case 'quizzes':
            return <QuizManager activeSection={props.activeSection} />;
          case 'ai':
            return <AILab activeSection={props.activeSection} />;
          case 'analytics':
            return <AnalyticsReports activeSection={props.activeSection} />;
          default:
            return <DashboardOverview activeSection="dashboard" />;
        }
      }}
    </AdminLayout>
  );
};

// Main app content with routing
const AppContent: React.FC = () => {
  const { isAuthenticated, user, loading, login, register, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [viewMode, setViewMode] = useState<'student' | 'admin'>('student');
  const [userProgress, setUserProgress] = useState<ProgressData | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [courses, setCourses] = useState<any[]>([]);
  const [aiContent, setAiContent] = useState<AIGeneratedContent | null>(null);
  const [loadingState, setLoadingState] = useState<boolean>(false);
  const [message, setMessage] = useState<string>('');
  const [showLandingPage, setShowLandingPage] = useState<boolean>(true);
  const [verificationRequired, setVerificationRequired] = useState<boolean>(false);
  const [unverifiedEmail, setUnverifiedEmail] = useState<string>('');
  const [showVerifyPage, setShowVerifyPage] = useState<boolean>(false);
  const [showForgotPassword, setShowForgotPassword] = useState<boolean>(false);
  
  // Support page state for authenticated users
  const [showSupportPage, setShowSupportPage] = useState<'help' | 'contact' | 'privacy' | 'terms' | null>(null);

  // Additional state for new features
  const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState<string>('');

  // Check for verification and reset pages on mount
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    if (window.location.pathname.includes('verify-email') || urlParams.has('token')) {
      setShowVerifyPage(true);
    }
    if (window.location.pathname.includes('reset-password') || urlParams.has('reset_token')) {
      setShowForgotPassword(true);
    }
  }, []);

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth();
  }, []);

  // Load user data when authenticated
  useEffect(() => {
    if (isAuthenticated && user) {
      loadUserData();
    }
  }, [isAuthenticated, user]);

  // Helper function to extract arrays from API response objects
  const extractArrayFromResponse = <T,>(response: any): T[] => {
    // If response is already an array, return it directly
    if (Array.isArray(response)) {
      return response as T[];
    }
    
    // If response is null or undefined, return empty array
    if (!response) {
      return [] as T[];
    }
    
    // If response is an object, look for common array properties
    if (typeof response === 'object') {
      // Common property names that might contain the array data
      const arrayProperties = [
        'data', 'results', 'items', 'concepts', 'paths', 
        'courses', 'quizzes', 'achievements', 'modules',
        'concepts_list', 'paths_list', 'courses_list'
      ];
      
      // First, check for known array properties
      for (const prop of arrayProperties) {
        if (Array.isArray(response[prop])) {
          return response[prop] as T[];
        }
      }
      
      // If response has success property, try to find any array property (excluding 'success')
      if ('success' in response) {
        const keys = Object.keys(response);
        for (const key of keys) {
          // Skip the success property and look for arrays
          if (key !== 'success' && Array.isArray(response[key])) {
            return response[key] as T[];
          }
        }
        
        // If we have a 'success' property but no array found, 
        // check if the response itself should be returned (for responses with multiple properties)
        // But for list endpoints, we should still try to find data
        const dataKeys = keys.filter(k => k !== 'success');
        if (dataKeys.length === 0) {
          return [] as T[];
        }
      }
    }
    
    // Return empty array as fallback with logging
    console.warn('Could not extract array from response:', response);
    return [] as T[];
  };

  const checkBackendHealth = async () => {
    try {
      const health = await apiService.healthCheck();
      console.log('Backend health:', health);
    } catch (error) {
      console.error('Backend not available:', error);
      setMessage('Backend server is not running. Please start the backend server.');
    }
  };

  const loadUserData = async () => {
    if (!user) return;
    
    try {
      setLoadingState(true);
      
      // Load concepts - extract array from API response object
      const conceptsResponse = await apiService.getConcepts();
      console.log('Concepts API response:', conceptsResponse);
      const conceptsArray = extractArrayFromResponse<Concept>(conceptsResponse);
      setConcepts(conceptsArray);
      
      // Load learning paths - extract array from API response object
      const pathsResponse = await apiService.getLearningPaths();
      console.log('Learning Paths API response:', pathsResponse);
      const pathsArray = extractArrayFromResponse<LearningPath>(pathsResponse);
      setLearningPaths(pathsArray);
      
      // Try to load additional data, but don't fail if endpoints don't exist
      try {
        const coursesResponse = await apiService.getCourses();
        console.log('Courses API response:', coursesResponse);
        const coursesArray = extractArrayFromResponse(coursesResponse);
        setCourses(coursesArray);
      } catch (error) {
        console.log('Courses endpoint not available, using mock data');
        setCourses(getMockCourses());
      }
      
      try {
        const achievementsResponse = await apiService.getAchievements(user.user_id);
        console.log('Achievements API response:', achievementsResponse);
        const achievementsArray = extractArrayFromResponse<Achievement>(achievementsResponse);
        // Ensure achievements is always an array before setting state
        if (Array.isArray(achievementsArray)) {
          setAchievements(achievementsArray);
        } else {
          console.warn('Achievements API did not return valid array, using mock data');
          setAchievements(getMockAchievements());
        }
      } catch (error) {
        console.log('Achievements endpoint not available, using mock data');
        setAchievements(getMockAchievements());
      }
      
      try {
        const quizzesResponse = await apiService.getQuizzes();
        console.log('Quizzes API response:', quizzesResponse);
        const quizzesArray = extractArrayFromResponse<Quiz>(quizzesResponse);
        setQuizzes(quizzesArray);
      } catch (error) {
        console.log('Quizzes endpoint not available, using mock data');
        setQuizzes(getMockQuizzes());
      }
      
      try {
        const progress = await apiService.getUserProgress(user.user_id);
        setUserProgress(progress);
      } catch (error) {
        console.log('User progress endpoint not available, using mock data');
        setUserProgress(getMockProgress(user.user_id));
      }
      
      try {
        const analyticsResponse = await apiService.getAnalytics(user.user_id);
        console.log('Analytics API response:', analyticsResponse);
        // Ensure analytics has the expected structure
        if (analyticsResponse && analyticsResponse.learning_analytics) {
          setAnalytics(analyticsResponse);
        } else {
          console.warn('Analytics API did not return expected structure, using mock data');
          setAnalytics(getMockAnalytics(user.user_id));
        }
      } catch (error) {
        console.log('Analytics endpoint not available, using mock data');
        setAnalytics(getMockAnalytics(user.user_id));
      }
      
      console.log('User data loaded successfully');
    } catch (error) {
      console.error('Error loading user data:', error);
    } finally {
      setLoadingState(false);
    }
  };

  const handleLogin = async (username: string, password: string) => {
    setLoadingState(true);
    setVerificationRequired(false);
    try {
      // Use apiService directly to get the full response
      const result = await apiService.login(username, password);
      
      // Check if email verification is required
      if (result.code === 'EMAIL_NOT_VERIFIED') {
        setVerificationRequired(true);
        setUnverifiedEmail(result.user?.email || username);
        setMessage('Please verify your email before logging in.');
        // Still call the auth login to store the user data
        await login(username, password);
        return;
      }
      
      // Proceed with normal login
      await login(username, password);
      setMessage('Login successful!');
      setActiveTab('dashboard');
    } catch (error: any) {
      // Check for email verification requirement in error
      const errorMessage = error.message || 'Login failed';
      const errorCode = error.code || '';
      
      if (errorCode === 'EMAIL_NOT_VERIFIED') {
        setVerificationRequired(true);
        setUnverifiedEmail(error.user?.email || username);
        setMessage('Please verify your email before logging in.');
      } else if (errorMessage.includes('already exists') || errorMessage.includes('Invalid credentials')) {
        setMessage(errorMessage);
      } else if (errorMessage.includes('no token')) {
        setMessage('Authentication failed. No token received from server.');
      } else {
        setMessage('Login failed. Please check your credentials and try again.');
      }
      console.error('Login error:', error);
    } finally {
      setLoadingState(false);
    }
  };

  const handleRegister = async (userData: any) => {
    setLoadingState(true);
    try {
      await register(userData);
      setMessage('Registration successful! Please check your email to verify your account.');
      // Redirect to verify email page with email pre-filled
      window.location.href = `/verify-email?email=${encodeURIComponent(userData.email)}`;
    } catch (error: any) {
      // Display detailed error message from the backend
      const errorMessage = error.message || 'Registration failed';
      if (errorMessage.includes('already exists')) {
        setMessage('This username or email is already registered. Please try logging in or use different credentials.');
      } else if (errorMessage.includes('password')) {
        setMessage('Password requirement error: ' + errorMessage);
      } else if (errorMessage.includes('email')) {
        setMessage('Email validation error: ' + errorMessage);
      } else if (errorMessage.includes('input') || errorMessage.includes('required')) {
        setMessage('Please fill in all required fields correctly.');
      } else {
        setMessage(errorMessage || 'Registration failed. Please try again.');
      }
      console.error('Registration error:', error);
    } finally {
      setLoadingState(false);
    }
  };

  const generateAIContent = async (conceptName?: string, domain?: string, difficulty?: string) => {
    if (!user) return;
    
    setLoadingState(true);
    setMessage('');
    try {
      const response = await apiService.generateAIContent(
        conceptName || 'Object-Spatial Programming',
        domain || 'Computer Science',
        difficulty || 'beginner',
        ['Graph Theory', 'Node Systems', 'Walker Functions']
      );
      
      if (response.success) {
        setAiContent(response);
        setMessage('AI content generated successfully!');
      } else {
        setMessage('Failed to generate AI content');
      }
    } catch (error) {
      setMessage('Failed to generate AI content');
      console.error('AI generation error:', error);
    } finally {
      setLoadingState(false);
    }
  };

  const sendChatMessage = async () => {
    if (!newMessage.trim() || !user) return;
    
    const userMsg: ChatMessage = {
      id: Date.now(),
      role: 'user',
      content: newMessage,
      timestamp: new Date().toISOString()
    };
    
    setChatMessages(prev => [...prev, userMsg]);
    setNewMessage('');
    
    try {
      const response = await apiService.sendChatMessage(newMessage);
      const botMsg: ChatMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.response || 'I understand. Let me help you with that.',
        timestamp: new Date().toISOString()
      };
      setChatMessages(prev => [...prev, botMsg]);
    } catch (error) {
      console.error('Chat error:', error);
    }
  };

  const startCourse = async (courseId: string) => {
    if (!user) return;
    
    setLoadingState(true);
    try {
      await apiService.startLearningSession(user.user_id, courseId);
      setMessage('Learning session started!');
      await loadUserData();
    } catch (error) {
      setMessage('Failed to start learning session');
      console.error('Session start error:', error);
    } finally {
      setLoadingState(false);
    }
  };

  const startQuiz = async (quizId: string) => {
    setActiveTab('quiz');
    setMessage(`Starting quiz ${quizId}...`);
  };

  // Mock data functions for fallback
  const getMockCourses = () => [
    {
      course_id: 'jac_fundamentals',
      title: 'Jac Programming Fundamentals',
      description: 'Learn the basics of Jac programming language - variables, functions, and control flow',
      domain: 'Jac Language',
      difficulty: 'beginner',
      content_type: 'tutorial'
    },
    {
      course_id: 'jac_osp_basics',
      title: 'Object-Spatial Programming Basics',
      description: 'Master the fundamentals of OSP with nodes, edges, and walkers',
      domain: 'Jac Language',
      difficulty: 'intermediate',
      content_type: 'tutorial'
    },
    {
      course_id: 'jac_advanced_osp',
      title: 'Advanced Object-Spatial Programming',
      description: 'Deep dive into graph traversal, mobile computation, and distributed patterns',
      domain: 'Jac Language',
      difficulty: 'advanced',
      content_type: 'tutorial'
    }
  ];

  const getMockAchievements = () => [
    {
      id: 'first_login',
      name: 'Welcome Aboard',
      description: 'Logged in for the first time',
      icon: '🎉',
      earned: true,
      earned_at: '2025-01-01',
      requirement: 'Login once',
      category: 'milestone'
    },
    {
      id: 'concept_explorer',
      name: 'Concept Explorer',
      description: 'Viewed 5 different concepts',
      icon: '🔍',
      earned: false,
      requirement: 'View 5 concepts',
      category: 'learning'
    }
  ];

  const getMockQuizzes = () => [
    {
      id: 'jac_variables_quiz',
      title: 'Jac Variables and Data Types Quiz',
      description: 'Test your knowledge of Jac variables, type annotations, and basic data types',
      questions: [
        {
          id: 'q1',
          question: 'What is the correct way to declare a variable with type annotation in Jac?',
          options: ['var name: str = "Alice"', 'name: str = "Alice"', 'let name: str = "Alice"', 'All of the above'],
          correct_answer: 3,
          explanation: 'Jac supports multiple variable declaration styles with type annotations'
        },
        {
          id: 'q2',
          question: 'Which data type is used for true/false values in Jac?',
          options: ['bool', 'boolean', 'Bit', 'TrueFalse'],
          correct_answer: 0,
          explanation: 'Jac uses "bool" for boolean data types'
        }
      ],
      difficulty: 'beginner',
      estimated_time: 10,
      completed: false
    },
    {
      id: 'jac_osp_quiz',
      title: 'Object-Spatial Programming Quiz',
      description: 'Test your understanding of nodes, edges, and walkers in Jac',
      questions: [
        {
          id: 'q1',
          question: 'What is a walker in Jac?',
          options: ['A function', 'A graph traversal entity', 'A variable', 'A loop'],
          correct_answer: 1,
          explanation: 'A walker is a graph traversal entity in Jac that moves through nodes and edges'
        },
        {
          id: 'q2',
          question: 'What are the three fundamental components of OSP?',
          options: ['Nodes, Edges, Walkers', 'Classes, Objects, Methods', 'Variables, Functions, Loops', 'Strings, Numbers, Booleans'],
          correct_answer: 0,
          explanation: 'OSP is built on Nodes (stateful entities), Edges (typed relationships), and Walkers (mobile computation)'
        }
      ],
      difficulty: 'intermediate',
      estimated_time: 15,
      completed: false
    }
  ];

  const getMockConcepts = () => [
    {
      id: 'osp_basics',
      concept_id: 'osp_basics',
      name: 'Object-Spatial Programming Basics',
      display_name: 'OSP Basics',
      category: 'Programming Paradigm',
      difficulty_level: 'beginner',
      difficulty: 'beginner',
      domain: 'Jac Language',
      icon: '🗺️',
      description: 'Learn the fundamentals of Object-Spatial Programming in Jac'
    },
    {
      id: 'nodes',
      concept_id: 'nodes',
      name: 'Nodes in Jac',
      display_name: 'Nodes',
      category: 'Graph Structures',
      difficulty_level: 'intermediate',
      difficulty: 'intermediate',
      domain: 'Jac Language',
      icon: '🔷',
      description: 'Understanding node structures and state management'
    },
    {
      id: 'edges',
      concept_id: 'edges',
      name: 'Edges and Connections',
      display_name: 'Edges',
      category: 'Graph Structures',
      difficulty_level: 'intermediate',
      difficulty: 'intermediate',
      domain: 'Jac Language',
      icon: '🔗',
      description: 'Creating relationships between nodes with edges'
    },
    {
      id: 'walkers',
      concept_id: 'walkers',
      name: 'Walker Functions',
      display_name: 'Walkers',
      category: 'Computation',
      difficulty_level: 'advanced',
      difficulty: 'advanced',
      domain: 'Jac Language',
      icon: '🚶',
      description: 'Mobile computation with walker functions'
    }
  ];

  const getMockLearningPaths = (): LearningPath[] => [
    {
      id: 'jac_fundamentals_path',
      title: 'Jac Programming Fundamentals',
      description: 'Master the basics of Jac programming language',
      courses: ['jac_fundamentals'],
      modules: [
        { id: 'mod1', title: 'Variables & Types', type: 'lesson', duration: '30 min', completed: true },
        { id: 'mod2', title: 'Functions', type: 'lesson', duration: '45 min', completed: false },
        { id: 'mod3', title: 'Quiz', type: 'quiz', duration: '15 min', completed: false }
      ],
      concepts: ['osp_basics'],
      skills_covered: ['Variables', 'Functions', 'Type Annotations'],
      prerequisites: [],
      total_modules: 3,
      completed_modules: 1,
      duration: '2 hours',
      estimated_hours: 2,
      difficulty: 'beginner',
      progress: 33,
      icon: '📚',
      category: 'Foundations',
      next_step: 'Functions',
      last_activity: '2025-12-25'
    },
    {
      id: 'osp_path',
      title: 'Object-Spatial Programming Mastery',
      description: 'Deep dive into OSP with nodes, edges, and walkers',
      courses: ['jac_osp_basics', 'jac_advanced_osp'],
      modules: [
        { id: 'mod1', title: 'Introduction to Nodes', type: 'lesson', duration: '45 min', completed: false },
        { id: 'mod2', title: 'Creating Edges', type: 'lesson', duration: '45 min', completed: false },
        { id: 'mod3', title: 'Walker Basics', type: 'lesson', duration: '60 min', completed: false },
        { id: 'mod4', title: 'Project', type: 'project', duration: '2 hours', completed: false }
      ],
      concepts: ['nodes', 'edges', 'walkers'],
      skills_covered: ['Node Creation', 'Edge Management', 'Walker Functions'],
      prerequisites: ['jac_fundamentals_path'],
      total_modules: 4,
      completed_modules: 0,
      duration: '5 hours',
      estimated_hours: 5,
      difficulty: 'intermediate',
      progress: 0,
      icon: '🎯',
      category: 'Core Concepts',
      next_step: 'Introduction to Nodes'
    }
  ];

  const getMockProgress = (userId: string): ProgressData => ({
    user_id: userId,
    progress: {
      courses_completed: 0,
      lessons_completed: 5,
      total_study_time: 120,
      current_streak: 3,
      average_score: 85
    },
    analytics: {
      completion_rate: 75,
      total_sessions: 10,
      completed_sessions: 8,
      in_progress_sessions: 2,
      average_progress: 60
    },
    learning_style: user.learning_style || 'visual',
    skill_level: user.skill_level || 'beginner',
    recent_activity: [
      {
        session_id: 'session_1',
        course_id: 'jac_basics',
        course_title: 'Jac Programming Fundamentals',
        status: 'completed',
        progress: 100
      }
    ]
  });

  const getMockAnalytics = (userId: string): AnalyticsData => ({
    user_id: userId,
    learning_analytics: {
      modules_completed: 5,
      total_study_time: 120,
      average_score: 85,
      engagement_score: 78,
      knowledge_retention: 82,
      learning_velocity: 'moderate',
      generated_at: new Date().toISOString()
    },
    recommendations: [
      'Continue practicing graph traversal concepts',
      'Explore advanced walker patterns',
      'Try implementing your own learning path'
    ],
    strengths: ['Pattern Recognition', 'Graph Theory'],
    areas_for_improvement: ['Advanced Syntax', 'Performance Optimization']
  });

  // =============================================================================
  // AUTH FORMS
  // =============================================================================

  const renderLoginForm = () => (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Login to Jeseci Academy</h2>
        
        {verificationRequired && (
          <div className="verification-notice">
            <div className="verification-icon">📧</div>
            <h3>Email Verification Required</h3>
            <p>Your email address ({unverifiedEmail || 'your account'}) has not been verified yet.</p>
            <p>Please check your inbox for the verification email or request a new one.</p>
            <button 
              className="btn btn-primary" 
              onClick={() => {
                setShowLandingPage(false);
                setShowVerifyPage(true);
              }}
            >
              Go to Verification Page
            </button>
          </div>
        )}
        
        {!verificationRequired && (
          <form onSubmit={(e) => {
            e.preventDefault();
            const formData = new FormData(e.target as HTMLFormElement);
            handleLogin(formData.get('username') as string, formData.get('password') as string);
          }}>
            <input name="username" type="text" placeholder="Username or Email" required />
            <input name="password" type="password" placeholder="Password" required />
            <button type="submit" disabled={loadingState}>
              {loadingState ? 'Logging in...' : 'Login'}
            </button>
          </form>
        )}
        
        <div className="auth-switch">
          <p>Don't have an account?</p>
          <button onClick={() => {
            setActiveTab('register');
            setVerificationRequired(false);
          }}>Register</button>
        </div>

        <div className="auth-forgot">
          <button 
            className="btn-link"
            onClick={() => {
              setShowForgotPassword(true);
              setActiveTab('login');
            }}
          >
            Forgot Password?
          </button>
        </div>

        <div className="auth-back">
          <button onClick={() => setShowLandingPage(true)}>← Back to Home</button>
        </div>
      </div>
    </div>
  );

  const renderRegisterForm = () => (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Register for Jeseci Academy</h2>
        <form onSubmit={(e) => {
          e.preventDefault();
          const formData = new FormData(e.target as HTMLFormElement);
          const userData = {
            username: formData.get('username') as string,
            email: formData.get('email') as string,
            password: formData.get('password') as string,
            first_name: formData.get('first_name') as string,
            last_name: formData.get('last_name') as string,
            learning_style: formData.get('learning_style') as string,
            skill_level: formData.get('skill_level') as string
          };
          handleRegister(userData);
        }}>
          <input name="username" type="text" placeholder="Username" required />
          <input name="email" type="email" placeholder="Email" required />
          <input name="password" type="password" placeholder="Password" required />
          <input name="first_name" type="text" placeholder="First Name" />
          <input name="last_name" type="text" placeholder="Last Name" />
          <select name="learning_style">
            <option value="visual">Visual Learner</option>
            <option value="auditory">Auditory Learner</option>
            <option value="kinesthetic">Kinesthetic Learner</option>
            <option value="reading">Reading/Writing Learner</option>
          </select>
          <select name="skill_level">
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
          <button type="submit" disabled={loadingState}>
            {loadingState ? 'Registering...' : 'Register'}
          </button>
        </form>
        
        <div className="auth-switch">
          <p>Already have an account?</p>
          <button onClick={() => setActiveTab('login')}>Login</button>
        </div>
        
        <div className="auth-back">
          <button onClick={() => setShowLandingPage(true)}>← Back to Home</button>
        </div>
      </div>
    </div>
  );

  // =============================================================================
  // DASHBOARD SECTIONS
  // =============================================================================

  const renderDashboard = () => (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Welcome back, {user?.first_name || user?.username || 'Learner'}!</h1>
        <p>Your personalized learning journey continues</p>
        <div className="user-info">
          <span className="user-badge">{user?.learning_style} Learner</span>
          <span className="user-badge">{user?.skill_level}</span>
        </div>
      </div>

      <div className="dashboard-tabs">
        <button className={activeTab === 'dashboard' ? 'active' : ''} onClick={() => setActiveTab('dashboard')}>
          Dashboard
        </button>
        <button className={activeTab === 'courses' ? 'active' : ''} onClick={() => setActiveTab('courses')}>
          Courses
        </button>
        <button className={activeTab === 'paths' ? 'active' : ''} onClick={() => setActiveTab('paths')}>
          Learning Paths
        </button>
        <button className={activeTab === 'concepts' ? 'active' : ''} onClick={() => setActiveTab('concepts')}>
          Concepts
        </button>
        <button className={activeTab === 'progress' ? 'active' : ''} onClick={() => setActiveTab('progress')}>
          Progress
        </button>
        <button className={activeTab === 'motivator' ? 'active' : ''} onClick={() => setActiveTab('motivator')}>
          Achievements
        </button>
        <button className={activeTab === 'quizzes' ? 'active' : ''} onClick={() => setActiveTab('quizzes')}>
          Quizzes
        </button>
        <button className={activeTab === 'ai' ? 'active' : ''} onClick={() => setActiveTab('ai')}>
          AI Generator
        </button>
        <button className={activeTab === 'chat' ? 'active' : ''} onClick={() => setActiveTab('chat')}>
          AI Chat
        </button>
        <button className={activeTab === 'analytics' ? 'active' : ''} onClick={() => setActiveTab('analytics')}>
          Analytics
        </button>
      </div>

      <div className="dashboard-content">
        {/* MAIN DASHBOARD OVERVIEW */}
        {activeTab === 'dashboard' && userProgress && (
          <div className="dashboard-overview">
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Courses Completed</h3>
                <p className="stat-number">{userProgress?.progress?.courses_completed || 0}</p>
              </div>
              <div className="stat-card">
                <h3>Lessons Completed</h3>
                <p className="stat-number">{userProgress?.progress?.lessons_completed || 0}</p>
              </div>
              <div className="stat-card">
                <h3>Study Time</h3>
                <p className="stat-number">{userProgress?.progress?.total_study_time || 0} mins</p>
              </div>
              <div className="stat-card">
                <h3>Current Streak</h3>
                <p className="stat-number">{userProgress?.progress?.current_streak || 0} days</p>
              </div>
            </div>

            {userProgress?.recent_activity && userProgress?.recent_activity.length > 0 && (
              <div className="recent-activity-section">
                <h3>Recent Activity</h3>
                {userProgress?.recent_activity.slice(0, 5).map((activity) => (
                  <div key={activity.session_id} className="activity-item">
                    <span className="activity-course">{activity.course_title}</span>
                    <span className="activity-status">{activity.status}</span>
                    <span className="activity-progress">{activity.progress}%</span>
                  </div>
                )) || []}
              </div>
            )}

            {achievements.length > 0 && (
              <div className="achievements-preview">
                <h3>Recent Achievements</h3>
                <div className="achievements-grid">
                  {achievements.slice(0, 4).map((achievement) => (
                    <div key={achievement.id} className="achievement-card">
                      <span className="achievement-icon">{achievement.icon}</span>
                      <span className="achievement-name">{achievement.name}</span>
                    </div>
                  )) || []}
                </div>
              </div>
            )}
          </div>
        )}

        {/* COURSES */}
        {activeTab === 'courses' && (
          <div className="courses-section">
            <h2>Available Courses</h2>
            <div className="courses-grid">
              {Array.isArray(courses) && courses.map((course) => (
                <div key={course.course_id} className="course-card">
                  <h3>{course.title}</h3>
                  <p>{course.description}</p>
                  <div className="course-meta">
                    <span className="course-domain">{course.domain}</span>
                    <span className="course-difficulty">{course.difficulty}</span>
                  </div>
                  <button onClick={() => startCourse(course.course_id)}>
                    Start Learning
                  </button>
                </div>
              )) || []}
            </div>
          </div>
        )}

        {/* LEARNING PATHS */}
        {activeTab === 'paths' && (
          <div className="paths-section">
            <div className="section-header">
              <h2>Learning Paths</h2>
              <p>Structured paths to master specific skills and technologies</p>
            </div>
            
            <div className="paths-filter">
              <button className="filter-btn active">All Paths</button>
              <button className="filter-btn">In Progress</button>
              <button className="filter-btn">Not Started</button>
              <button className="filter-btn">Completed</button>
            </div>
            
            <div className="paths-grid">
              {(learningPaths || []).map((path) => (
                <div key={path.id} className="path-card">
                  <div className="path-card-header">
                    <span className="path-icon">{path.icon}</span>
                    <span className={`difficulty-badge ${path.difficulty}`}>{path.difficulty}</span>
                  </div>
                  
                  <div className="path-card-body">
                    <h3>{path.title}</h3>
                    <p className="path-description">{path.description}</p>
                    
                    <div className="path-meta">
                      <div className="meta-item">
                        <span className="meta-label">Duration</span>
                        <span className="meta-value">{path.duration}</span>
                      </div>
                      <div className="meta-item">
                        <span className="meta-label">Hours</span>
                        <span className="meta-value">{path.estimated_hours}h</span>
                      </div>
                      <div className="meta-item">
                        <span className="meta-label">Modules</span>
                        <span className="meta-value">{path.total_modules}</span>
                      </div>
                    </div>
                    
                    <div className="path-progress-section">
                      <div className="progress-header">
                        <span>Progress</span>
                        <span>{path.progress}%</span>
                      </div>
                      <div className="progress-bar">
                        <div 
                          className="progress-fill" 
                          style={{ width: `${path.progress}%` }}
                        ></div>
                      </div>
                      <div className="modules-completed">
                        {path.completed_modules} of {path.total_modules} modules completed
                      </div>
                    </div>
                    
                    {path.next_step && path.progress > 0 && (
                      <div className="next-step">
                        <span className="next-label">Next up:</span>
                        <span className="next-title">{path.next_step}</span>
                      </div>
                    )}
                    
                    <div className="skills-preview">
                      {path.skills_covered.slice(0, 3).map((skill, index) => (
                        <span key={index} className="skill-tag">{skill}</span>
                      )) || []}
                      {path.skills_covered.length > 3 && (
                        <span className="skill-more">+{path.skills_covered.length - 3} more</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="path-card-footer">
                    <button 
                      className="continue-btn"
                      onClick={() => setActiveTab('concepts')}
                    >
                      {path.progress === 0 ? 'Start Path' : 'Continue Learning'}
                    </button>
                    <button className="details-btn">
                      View Details
                    </button>
                  </div>
                </div>
              ))}
            </div>
            
            {learningPaths.length === 0 && (
              <div className="empty-state">
                <span className="empty-icon">📚</span>
                <h3>No Learning Paths Available</h3>
                <p>Check back soon for new learning paths!</p>
              </div>
            )}
          </div>
        )}

        {/* CONCEPTS */}
        {activeTab === 'concepts' && (
          <div className="concepts-section">
            <h2>Concepts Library</h2>
            <p>Explore topics across different domains</p>
            <div className="concepts-grid">
              {(concepts || []).map((concept) => (
                <div key={concept.id} className="concept-card">
                  <span className="concept-icon">{concept.icon}</span>
                  <h3>{concept.name}</h3>
                  <p>{concept.description}</p>
                  <div className="concept-meta">
                    <span className="concept-domain">{concept.domain}</span>
                    <span className="concept-difficulty">{concept.difficulty}</span>
                  </div>
                  <button onClick={() => generateAIContent(concept.name, concept.domain, concept.difficulty)}>
                    Learn with AI
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* PROGRESS */}
        {activeTab === 'progress' && userProgress && (
          <div className="progress-section">
            <h2>Your Learning Progress</h2>
            <div className="progress-stats">
              <div className="stat-card">
                <h3>Courses Completed</h3>
                <p className="stat-number">{userProgress?.progress?.courses_completed || 0}</p>
              </div>
              <div className="stat-card">
                <h3>Lessons Completed</h3>
                <p className="stat-number">{userProgress?.progress?.lessons_completed || 0}</p>
              </div>
              <div className="stat-card">
                <h3>Study Time</h3>
                <p className="stat-number">{userProgress?.progress?.total_study_time || 0} mins</p>
              </div>
              <div className="stat-card">
                <h3>Current Streak</h3>
                <p className="stat-number">{userProgress?.progress?.current_streak || 0} days</p>
              </div>
            </div>
            
            <div className="analytics-overview">
              <h3>Analytics Overview</h3>
              <p><strong>Completion Rate:</strong> {userProgress?.analytics?.completion_rate?.toFixed(1) || '0.0'}%</p>
              <p><strong>Total Sessions:</strong> {userProgress?.analytics?.total_sessions || 0}</p>
              <p><strong>Average Score:</strong> {userProgress?.analytics?.average_progress?.toFixed(1) || '0.0'}%</p>
            </div>
          </div>
        )}

        {/* MOTIVATOR / ACHIEVEMENTS */}
        {activeTab === 'motivator' && (
          <div className="motivator-section">
            <h2>Achievements & Gamification</h2>
            <p>Track your accomplishments and stay motivated</p>
            
            <div className="achievements-categories">
              <div className="achievement-category">
                <h3>Earned Badges</h3>
                <div className="achievements-grid">
                  {(achievements || []).filter(a => a.earned).map((achievement) => (
                    <div key={achievement.id} className="achievement-card earned">
                      <span className="achievement-icon">{achievement.icon}</span>
                      <h4>{achievement.name}</h4>
                      <p>{achievement.description}</p>
                      <span className="achievement-date">Earned: {achievement.earned_at}</span>
                    </div>
                  )) || []}
                </div>
              </div>
              
              <div className="achievement-category">
                <h3>Locked Achievements</h3>
                <div className="achievements-grid">
                  {(achievements || []).filter(a => !a.earned).map((achievement) => (
                    <div key={achievement.id} className="achievement-card locked">
                      <span className="achievement-icon">🔒</span>
                      <h4>{achievement.name}</h4>
                      <p>{achievement.description}</p>
                      <p className="achievement-requirement">Requirement: {achievement.requirement}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* QUIZZES */}
        {activeTab === 'quizzes' && (
          <div className="quizzes-section">
            <h2>Knowledge Checks</h2>
            <p>Test your understanding with interactive quizzes</p>
            <div className="quizzes-grid">
              {Array.isArray(quizzes) && quizzes.map((quiz) => (
                <div key={quiz.id} className="quiz-card">
                  <h3>{quiz.title}</h3>
                  <p>{quiz.description}</p>
                  <div className="quiz-meta">
                    <span>{quiz.questions.length} questions</span>
                    <span>{quiz.difficulty}</span>
                    <span>{quiz.estimated_time} mins</span>
                  </div>
                  <button onClick={() => startQuiz(quiz.id)}>
                    {quiz.completed ? 'Retake Quiz' : 'Start Quiz'}
                  </button>
                </div>
              )) || []}
            </div>
          </div>
        )}

        {/* AI GENERATOR */}
        {activeTab === 'ai' && (
          <div className="ai-section">
            <h2>AI-Powered Content Generator</h2>
            <p>Generate personalized learning content using AI</p>
            <div className="ai-generator">
              <div className="ai-inputs">
                <input 
                  type="text" 
                  placeholder="What concept do you want to learn?" 
                  defaultValue="Object-Spatial Programming"
                />
                <select defaultValue="Computer Science">
                  <option value="Computer Science">Computer Science</option>
                  <option value="Mathematics">Mathematics</option>
                  <option value="Physics">Physics</option>
                  <option value="Biology">Biology</option>
                </select>
                <select defaultValue="beginner">
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
                <button onClick={() => generateAIContent()} disabled={loadingState}>
                  {loadingState ? 'Generating...' : 'Generate AI Content'}
                </button>
              </div>
              
              {aiContent && (
                <div className="ai-content">
                  <h3>Generated: {aiContent.concept_name}</h3>
                  <div className="content-display">
                    <pre>{aiContent.content}</pre>
                  </div>
                  <p><strong>Related Concepts:</strong> {aiContent.related_concepts.join(', ')}</p>
                  <p><strong>Generated:</strong> {new Date(aiContent.generated_at).toLocaleString()}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* AI CHAT */}
        {activeTab === 'chat' && (
          <div className="chat-section">
            <h2>AI Learning Assistant</h2>
            <p>Chat with your AI tutor for personalized help</p>
            <div className="chat-container">
              <div className="chat-messages">
                {chatMessages.length === 0 ? (
                  <div className="chat-empty">
                    <p>Start a conversation with your AI learning assistant!</p>
                    <p>Ask questions, get explanations, or discuss concepts.</p>
                  </div>
                ) : (
                  (chatMessages || []).map((msg) => (
                    <div key={msg.id} className={`chat-message ${msg.role}`}>
                      <span className="message-role">{msg.role === 'user' ? 'You' : 'AI'}</span>
                      <p className="message-content">{msg.content}</p>
                      <span className="message-time">
                        {new Date(msg.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  ))
                )}
              </div>
              <div className="chat-input">
                <input 
                  type="text" 
                  placeholder="Ask your AI tutor..." 
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                />
                <button onClick={sendChatMessage}>Send</button>
              </div>
            </div>
          </div>
        )}

        {/* ANALYTICS */}
        {activeTab === 'analytics' && analytics && (
          <div className="analytics-section">
            <h2>Learning Analytics</h2>
            <p>Comprehensive insights into your learning journey</p>
            
            <div className="analytics-grid">
              <div className="metric-card">
                <h4>Modules Completed</h4>
                <p className="metric-value">{analytics?.learning_analytics?.modules_completed || 0}</p>
              </div>
              <div className="metric-card">
                <h4>Total Study Time</h4>
                <p className="metric-value">{analytics?.learning_analytics?.total_study_time || 0} mins</p>
              </div>
              <div className="metric-card">
                <h4>Average Score</h4>
                <p className="metric-value">{analytics?.learning_analytics?.average_score || 0}%</p>
              </div>
              <div className="metric-card">
                <h4>Engagement Score</h4>
                <p className="metric-value">{analytics?.learning_analytics?.engagement_score || 0}%</p>
              </div>
              <div className="metric-card">
                <h4>Knowledge Retention</h4>
                <p className="metric-value">{analytics?.learning_analytics?.knowledge_retention || 0}%</p>
              </div>
              <div className="metric-card">
                <h4>Learning Velocity</h4>
                <p className="metric-value">{analytics?.learning_analytics?.learning_velocity || 'N/A'}</p>
              </div>
            </div>
            
            <div className="recommendations-section">
              <h3>Personalized Recommendations</h3>
              <ul>
                {(analytics?.recommendations || []).map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  // =============================================================================
  // MAIN RENDER
  // =============================================================================

  if (loading) {
    return (
      <div className="App loading">
        <div className="loading-spinner">
          <h1>🎓 Jeseci Academy</h1>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      {/* Show Email Verification Page if URL contains verify-email or token */}
      {showVerifyPage && !isAuthenticated && (
        <BrowserRouter>
          <VerifyEmail />
        </BrowserRouter>
      )}

      {/* Show Forgot Password Page */}
      {showForgotPassword && !isAuthenticated && (
        <BrowserRouter>
          <ForgotPassword />
        </BrowserRouter>
      )}

      {/* Show Reset Password Page if URL contains reset token */}
      {window.location.pathname.includes('reset-password') && !isAuthenticated && (
        <BrowserRouter>
          <ResetPassword />
        </BrowserRouter>
      )}

      {/* Show Landing Page for non-authenticated users (only if not on verify page) */}
      {!isAuthenticated && showLandingPage && !showVerifyPage ? (
        <LandingPageWithNavigation 
          onShowLogin={() => {
            setActiveTab('login');
            setShowLandingPage(false);
          }}
          onShowRegister={() => {
            setActiveTab('register');
            setShowLandingPage(false);
          }}
        />
      ) : null}

      {/* Show main application for authenticated users OR auth forms for non-authenticated users */}
      {(isAuthenticated || (!showLandingPage && !showVerifyPage)) && (
        <>
          <header className="app-header">
            <div className="header-content">
              <h1>🎓 Jeseci Smart Learning Academy</h1>
              <p>AI-Powered Personalized Learning</p>
              {isAuthenticated && (
                <div className="header-actions">
                  {user?.is_admin && (
                    <button 
                      onClick={() => setViewMode('admin')}
                      style={{ 
                        marginRight: '12px',
                        background: '#dbeafe', 
                        color: '#1d4ed8',
                        padding: '8px 16px',
                        borderRadius: '6px',
                        border: 'none',
                        cursor: 'pointer',
                        fontWeight: '500'
                      }}
                    >
                      ⚙️ Admin Panel
                    </button>
                  )}
                  <span className="user-greeting">Hello, {user?.first_name || user?.username}</span>
                  <button onClick={logout}>Logout</button>
                </div>
              )}
            </div>
          </header>

          {message && (
            <div className="message-banner">
              {message}
              <button onClick={() => setMessage('')}>×</button>
            </div>
          )}

          <main className="app-main">
            {isAuthenticated ? (
              viewMode === 'admin' ? (
                <AdminPage />
              ) : (
                renderDashboard()
              )
            ) : (
              <div className="auth-section">
                <div className="auth-tabs">
                  <button 
                    className={activeTab === 'login' ? 'active' : ''} 
                    onClick={() => setActiveTab('login')}
                    style={{ display: activeTab === 'login' ? 'none' : 'inline-block' }}
                  >
                    Login
                  </button>
                  <button 
                    className={activeTab === 'register' ? 'active' : ''} 
                    onClick={() => setActiveTab('register')}
                    style={{ display: activeTab === 'register' ? 'none' : 'inline-block' }}
                  >
                    Register
                  </button>
                </div>
                
                {activeTab === 'login' && renderLoginForm()}
                {activeTab === 'register' && renderRegisterForm()}
              </div>
            )}
          </main>

          {/* Show Support Pages for authenticated users */}
          {showSupportPage && (
            <>
              {showSupportPage === 'help' && <HelpCenterPage onBack={() => setShowSupportPage(null)} />}
              {showSupportPage === 'contact' && <ContactPage onBack={() => setShowSupportPage(null)} />}
              {showSupportPage === 'privacy' && <PrivacyPage onBack={() => setShowSupportPage(null)} />}
              {showSupportPage === 'terms' && <TermsPage onBack={() => setShowSupportPage(null)} />}
            </>
          )}

          {!showSupportPage && (
            <footer className="app-footer">
              <div className="footer-content">
                <div className="footer-section footer-brand">
                  <div className="footer-brand-header">
                    <span className="footer-logo">🎓</span>
                    <span className="footer-brand-name">Jeseci Academy</span>
                  </div>
                  <p className="footer-brand-description">
                    Empowering developers worldwide to master Object-Spatial Programming with Jac Language 
                    through AI-powered personalized education.
                  </p>
                </div>
                
                <div className="footer-section">
                  <h5 className="footer-title">Jac Learning</h5>
                  <ul className="footer-links">
                    <li><button onClick={() => setActiveTab('paths')} className="footer-link-btn">Learning Paths</button></li>
                    <li><button onClick={() => setActiveTab('ai')} className="footer-link-btn">AI Code Assistant</button></li>
                    <li><button onClick={() => setActiveTab('progress')} className="footer-link-btn">Progress Tracking</button></li>
                    <li><button onClick={() => setActiveTab('achievements')} className="footer-link-btn">Achievements</button></li>
                  </ul>
                </div>
                
                <div className="footer-section">
                  <h5 className="footer-title">Jac Topics</h5>
                  <ul className="footer-links">
                    <li><button onClick={() => setActiveTab('concepts')} className="footer-link-btn">Jac Fundamentals</button></li>
                    <li><button onClick={() => setActiveTab('concepts')} className="footer-link-btn">Object-Spatial Programming</button></li>
                    <li><button onClick={() => setActiveTab('paths')} className="footer-link-btn">Nodes, Edges & Walkers</button></li>
                    <li><button onClick={() => setActiveTab('quiz')} className="footer-link-btn">Semantic Strings</button></li>
                  </ul>
                </div>
                
                <div className="footer-section">
                  <h5 className="footer-title">Support</h5>
                  <ul className="footer-links">
                    <li><button onClick={() => setShowSupportPage('help')} className="footer-link-btn">Help Center</button></li>
                    <li><button onClick={() => setShowSupportPage('contact')} className="footer-link-btn">Contact Us</button></li>
                    <li><button onClick={() => setShowSupportPage('privacy')} className="footer-link-btn">Privacy Policy</button></li>
                    <li><button onClick={() => setShowSupportPage('terms')} className="footer-link-btn">Terms of Service</button></li>
                  </ul>
                </div>
              </div>
              
              <div className="footer-bottom">
                <p>© 2025 Jeseci Smart Learning Academy. All rights reserved.</p>
                <p className="footer-tech">Powered by React + Jaclang + OpenAI + Object-Spatial Programming</p>
              </div>
            </footer>
          )}
        </>
      )}
    </div>
  );
};

// Wrap App with AuthProvider and AdminProvider
const App: React.FC = () => {
  return (
    <AdminProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </AdminProvider>
  );
};

export default App;