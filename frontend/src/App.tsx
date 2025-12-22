import React, { useState, useEffect } from 'react';
import { apiService, User, ProgressData, AIGeneratedContent } from './services/api';
import './App.css';

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
}

const App: React.FC = () => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    token: null
  });
  
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [userProgress, setUserProgress] = useState<ProgressData | null>(null);
  const [courses, setCourses] = useState<any[]>([]);
  const [aiContent, setAiContent] = useState<AIGeneratedContent | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<string>('');

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const health = await apiService.healthCheck();
      console.log('Backend health:', health);
    } catch (error) {
      console.error('Backend not available:', error);
      setMessage('Backend server is not running. Please start the backend server.');
    }
  };

  const handleLogin = async (username: string, password: string) => {
    setLoading(true);
    try {
      const response = await apiService.login(username, password);
      
      if (response.success && response.user && response.access_token) {
        setAuthState({
          isAuthenticated: true,
          user: response.user,
          token: response.access_token
        });
        setMessage('Login successful!');
        
        // Load user data
        await loadUserData(response.user.user_id);
      } else {
        setMessage(response.error || 'Login failed');
      }
    } catch (error) {
      setMessage('Login failed. Please check your credentials.');
      console.error('Login error:', error);
    }
    setLoading(false);
  };

  const handleRegister = async (userData: any) => {
    setLoading(true);
    try {
      const response = await apiService.register(userData);
      
      if (response.success) {
        setMessage('Registration successful! You can now log in.');
        setActiveTab('login');
      } else {
        setMessage('Registration failed');
      }
    } catch (error) {
      setMessage('Registration failed. Please try again.');
      console.error('Registration error:', error);
    }
    setLoading(false);
  };

  const loadUserData = async (userId: string) => {
    try {
      const progress = await apiService.getUserProgress(userId);
      setUserProgress(progress);
      
      const coursesData = await apiService.getCourses();
      setCourses(coursesData);
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  };

  const generateAIContent = async () => {
    if (!authState.user) return;
    
    setLoading(true);
    try {
      const response = await apiService.generateAIContent(
        'Object-Spatial Programming',
        'Computer Science',
        'beginner',
        ['Graph Theory', 'Node Systems', 'Walker Functions']
      );
      
      setAiContent(response);
      setMessage('AI content generated successfully!');
    } catch (error) {
      setMessage('Failed to generate AI content');
      console.error('AI generation error:', error);
    }
    setLoading(false);
  };

  const renderLoginForm = () => (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Login to Jeseci Academy</h2>
        <form onSubmit={(e) => {
          e.preventDefault();
          const formData = new FormData(e.target as HTMLFormElement);
          handleLogin(formData.get('username') as string, formData.get('password') as string);
        }}>
          <input name="username" type="text" placeholder="Username or Email" required />
          <input name="password" type="password" placeholder="Password" required />
          <button type="submit" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <div className="auth-switch">
          <p>Don't have an account?</p>
          <button onClick={() => setActiveTab('register')}>Register</button>
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
          <button type="submit" disabled={loading}>
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>
        
        <div className="auth-switch">
          <p>Already have an account?</p>
          <button onClick={() => setActiveTab('login')}>Login</button>
        </div>
      </div>
    </div>
  );

  const renderDashboard = () => (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Welcome to Jeseci Smart Learning Academy</h1>
        <p>LittleX Pattern Architecture - React Frontend + Jaclang Backend</p>
        <div className="user-info">
          <p><strong>User:</strong> {authState.user?.username}</p>
          <p><strong>Learning Style:</strong> {authState.user?.learning_style}</p>
          <p><strong>Skill Level:</strong> {authState.user?.skill_level}</p>
        </div>
      </div>

      <div className="dashboard-tabs">
        <button 
          className={activeTab === 'courses' ? 'active' : ''} 
          onClick={() => setActiveTab('courses')}
        >
          Courses
        </button>
        <button 
          className={activeTab === 'progress' ? 'active' : ''} 
          onClick={() => setActiveTab('progress')}
        >
          Progress
        </button>
        <button 
          className={activeTab === 'ai' ? 'active' : ''} 
          onClick={() => setActiveTab('ai')}
        >
          AI Generator
        </button>
        <button 
          className={activeTab === 'analytics' ? 'active' : ''} 
          onClick={() => setActiveTab('analytics')}
        >
          Analytics
        </button>
      </div>

      <div className="dashboard-content">
        {activeTab === 'courses' && (
          <div className="courses-section">
            <h2>Available Courses</h2>
            <div className="courses-grid">
              {courses.map((course) => (
                <div key={course.course_id} className="course-card">
                  <h3>{course.title}</h3>
                  <p>{course.description}</p>
                  <p><strong>Domain:</strong> {course.domain}</p>
                  <p><strong>Difficulty:</strong> {course.difficulty}</p>
                  <button onClick={() => startCourse(course.course_id)}>
                    Start Learning
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'progress' && userProgress && (
          <div className="progress-section">
            <h2>Your Learning Progress</h2>
            <div className="progress-stats">
              <div className="stat-card">
                <h3>Courses Completed</h3>
                <p className="stat-number">{userProgress.progress.courses_completed}</p>
              </div>
              <div className="stat-card">
                <h3>Lessons Completed</h3>
                <p className="stat-number">{userProgress.progress.lessons_completed}</p>
              </div>
              <div className="stat-card">
                <h3>Study Time (mins)</h3>
                <p className="stat-number">{userProgress.progress.total_study_time}</p>
              </div>
              <div className="stat-card">
                <h3>Current Streak</h3>
                <p className="stat-number">{userProgress.progress.current_streak}</p>
              </div>
            </div>
            
            <div className="analytics-overview">
              <h3>Analytics Overview</h3>
              <p><strong>Completion Rate:</strong> {userProgress.analytics.completion_rate.toFixed(1)}%</p>
              <p><strong>Total Sessions:</strong> {userProgress.analytics.total_sessions}</p>
              <p><strong>Average Score:</strong> {userProgress.analytics.average_progress.toFixed(1)}</p>
            </div>
          </div>
        )}

        {activeTab === 'ai' && (
          <div className="ai-section">
            <h2>AI-Powered Content Generator</h2>
            <p>Generate personalized learning content using AI</p>
            <button onClick={generateAIContent} disabled={loading}>
              {loading ? 'Generating...' : 'Generate AI Content'}
            </button>
            
            {aiContent && (
              <div className="ai-content">
                <h3>Generated Content: {aiContent.concept_name}</h3>
                <div className="content-display">
                  <pre>{aiContent.content}</pre>
                </div>
                <p><strong>Related Concepts:</strong> {aiContent.related_concepts.join(', ')}</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="analytics-section">
            <h2>Learning Analytics</h2>
            <p>Comprehensive insights into your learning journey</p>
            <div className="analytics-grid">
              <div className="metric-card">
                <h4>Engagement Score</h4>
                <p className="metric-value">85%</p>
              </div>
              <div className="metric-card">
                <h4>Learning Velocity</h4>
                <p className="metric-value">Fast</p>
              </div>
              <div className="metric-card">
                <h4>Knowledge Retention</h4>
                <p className="metric-value">92%</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const startCourse = async (courseId: string) => {
    if (!authState.user) return;
    
    setLoading(true);
    try {
      await apiService.startLearningSession(authState.user.user_id, courseId);
      setMessage('Learning session started!');
    } catch (error) {
      setMessage('Failed to start learning session');
      console.error('Session start error:', error);
    }
    setLoading(false);
  };

  const handleLogout = () => {
    setAuthState({
      isAuthenticated: false,
      user: null,
      token: null
    });
    setUserProgress(null);
    setActiveTab('dashboard');
    setMessage('Logged out successfully');
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>🎓 Jeseci Smart Learning Academy</h1>
          <p>LittleX Pattern • React + Jaclang • AI-Powered Education</p>
          {authState.isAuthenticated && (
            <div className="header-actions">
              <button onClick={handleLogout}>Logout</button>
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
        {!authState.isAuthenticated ? (
          <div className="auth-section">
            <div className="auth-tabs">
              <button 
                className={activeTab === 'login' ? 'active' : ''} 
                onClick={() => setActiveTab('login')}
              >
                Login
              </button>
              <button 
                className={activeTab === 'register' ? 'active' : ''} 
                onClick={() => setActiveTab('register')}
              >
                Register
              </button>
            </div>
            
            {activeTab === 'login' && renderLoginForm()}
            {activeTab === 'register' && renderRegisterForm()}
          </div>
        ) : (
          renderDashboard()
        )}
      </main>

      <footer className="app-footer">
        <p>© 2025 Jeseci Smart Learning Academy • LittleX Pattern Architecture</p>
        <p>Powered by React Frontend + Jaclang Backend API</p>
      </footer>
    </div>
  );
};

export default App;
