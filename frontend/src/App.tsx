import React, { useState, useEffect } from 'react';
import { apiService, User, ProgressData, AnalyticsData, AIGeneratedContent } from './services/api';
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
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
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
      console.log('Login response:', response);
      
      if (response.success && response.user) {
        setAuthState({
          isAuthenticated: true,
          user: response.user,
          token: response.access_token || null
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
      console.log('Starting registration with data:', userData);
      const response = await apiService.register(userData);
      console.log('Registration response received:', response);
      
      if (response.success) {
        console.log('Registration successful - setting message and switching tab');
        setMessage('Registration successful! You can now log in.');
        setActiveTab('login');
      } else {
        console.log('Registration response format:', response);
        // Check if it's already registered
        if (response.error && response.error.includes('already exists')) {
          setMessage('User already exists. Please login.');
        } else {
          setMessage('Registration failed');
        }
      }
    } catch (error) {
      setMessage('Registration failed. Please try again.');
      console.error('Registration error:', error);
    }
    setLoading(false);
  };

  const loadUserData = async (userId: string) => {
    try {
      // Load progress data
      const progress = await apiService.getUserProgress(userId);
      setUserProgress(progress);
      console.log('User progress loaded:', progress);
      
      // Load analytics data
      const analyticsData = await apiService.getAnalytics(userId);
      setAnalytics(analyticsData);
      console.log('Analytics loaded:', analyticsData);
      
      // Load courses
      const coursesData = await apiService.getCourses();
      setCourses(coursesData);
      console.log('Courses loaded:', coursesData);
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  };

  const generateAIContent = async () => {
    if (!authState.user) return;
    
    setLoading(true);
    setMessage('');
    try {
      const response = await apiService.generateAIContent(
        'Object-Spatial Programming',
        'Computer Science',
        'beginner',
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
        <p>AI-Powered Learning Platform with Dynamic Analytics</p>
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
                <p className="stat-number">{userProgress.progress.current_streak} days</p>
              </div>
            </div>
            
            <div className="analytics-overview">
              <h3>Analytics Overview</h3>
              <p><strong>Completion Rate:</strong> {userProgress.analytics.completion_rate.toFixed(1)}%</p>
              <p><strong>Total Sessions:</strong> {userProgress.analytics.total_sessions}</p>
              <p><strong>Completed Sessions:</strong> {userProgress.analytics.completed_sessions}</p>
              <p><strong>In Progress:</strong> {userProgress.analytics.in_progress_sessions}</p>
              <p><strong>Average Score:</strong> {userProgress.analytics.average_progress.toFixed(1)}%</p>
            </div>
            
            {userProgress.recent_activity && userProgress.recent_activity.length > 0 && (
              <div className="recent-activity">
                <h3>Recent Activity</h3>
                {userProgress.recent_activity.slice(0, 5).map((activity) => (
                  <div key={activity.session_id} className="activity-item">
                    <p><strong>{activity.course_title}</strong> - {activity.status}</p>
                    <p>Progress: {activity.progress}%</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'ai' && (
          <div className="ai-section">
            <h2>AI-Powered Content Generator</h2>
            <p>Generate personalized learning content using OpenAI GPT-4o-mini</p>
            <button onClick={generateAIContent} disabled={loading} className="ai-button">
              {loading ? 'Generating...' : 'Generate AI Content'}
            </button>
            
            {aiContent && (
              <div className="ai-content">
                <h3>Generated Content: {aiContent.concept_name}</h3>
                <div className="content-display">
                  <pre>{aiContent.content}</pre>
                </div>
                <p><strong>Related Concepts:</strong> {aiContent.related_concepts.join(', ')}</p>
                <p><strong>Generated at:</strong> {new Date(aiContent.generated_at).toLocaleString()}</p>
                {aiContent.source && <p><strong>Source:</strong> {aiContent.source}</p>}
              </div>
            )}
          </div>
        )}

        {activeTab === 'analytics' && analytics && (
          <div className="analytics-section">
            <h2>Learning Analytics</h2>
            <p>Comprehensive insights into your learning journey</p>
            
            <div className="analytics-grid">
              <div className="metric-card">
                <h4>Modules Completed</h4>
                <p className="metric-value">{analytics.learning_analytics.modules_completed}</p>
              </div>
              <div className="metric-card">
                <h4>Total Study Time</h4>
                <p className="metric-value">{analytics.learning_analytics.total_study_time} mins</p>
              </div>
              <div className="metric-card">
                <h4>Average Score</h4>
                <p className="metric-value">{analytics.learning_analytics.average_score}%</p>
              </div>
              <div className="metric-card">
                <h4>Engagement Score</h4>
                <p className="metric-value">{analytics.learning_analytics.engagement_score}%</p>
              </div>
              <div className="metric-card">
                <h4>Knowledge Retention</h4>
                <p className="metric-value">{analytics.learning_analytics.knowledge_retention}%</p>
              </div>
              <div className="metric-card">
                <h4>Learning Velocity</h4>
                <p className="metric-value">{analytics.learning_analytics.learning_velocity}</p>
              </div>
            </div>
            
            <div className="recommendations-section">
              <h3>Recommendations</h3>
              <ul>
                {analytics.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
            
            <div className="strengths-section">
              <h3>Your Strengths</h3>
              <ul>
                {analytics.strengths.map((strength, index) => (
                  <li key={index}>{strength}</li>
                ))}
              </ul>
            </div>
            
            <div className="improvements-section">
              <h3>Areas for Improvement</h3>
              <ul>
                {analytics.areas_for_improvement.map((area, index) => (
                  <li key={index}>{area}</li>
                ))}
              </ul>
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
      
      // Refresh user data
      await loadUserData(authState.user.user_id);
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
    setAnalytics(null);
    setActiveTab('dashboard');
    setMessage('Logged out successfully');
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>Jeseci Smart Learning Academy</h1>
          <p>AI-Powered Education • Dynamic Analytics • OpenAI Integration</p>
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
        <p>© 2025 Jeseci Smart Learning Academy • AI-Powered Learning Platform</p>
        <p>Powered by FastAPI Backend + OpenAI GPT-4o-mini</p>
      </footer>
    </div>
  );
};

export default App;
