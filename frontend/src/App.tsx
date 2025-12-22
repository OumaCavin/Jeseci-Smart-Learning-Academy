import React, { useState, useEffect, useContext } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { apiService, User, ProgressData, AnalyticsData, AIGeneratedContent, LearningPath, Concept, Quiz, Achievement, ChatMessage } from './services/api';
import './App.css';

// =============================================================================
// MAIN APP COMPONENT
// =============================================================================

const AppContent: React.FC = () => {
  const { isAuthenticated, user, loading, login, register, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [userProgress, setUserProgress] = useState<ProgressData | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [courses, setCourses] = useState<any[]>([]);
  const [aiContent, setAiContent] = useState<AIGeneratedContent | null>(null);
  const [loadingState, setLoadingState] = useState<boolean>(false);
  const [message, setMessage] = useState<string>('');

  // Additional state for new features
  const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState<string>('');

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
      
      // Load all user data
      const progress = await apiService.getUserProgress(user.user_id);
      setUserProgress(progress);
      
      const analyticsData = await apiService.getAnalytics(user.user_id);
      setAnalytics(analyticsData);
      
      const coursesData = await apiService.getCourses();
      setCourses(coursesData);
      
      // Load additional features
      const paths = await apiService.getLearningPaths();
      setLearningPaths(paths);
      
      const conceptsData = await apiService.getConcepts();
      setConcepts(conceptsData);
      
      const quizzesData = await apiService.getQuizzes();
      setQuizzes(quizzesData);
      
      const achievementsData = await apiService.getAchievements(user.user_id);
      setAchievements(achievementsData);
      
      console.log('All user data loaded successfully');
    } catch (error) {
      console.error('Error loading user data:', error);
    } finally {
      setLoadingState(false);
    }
  };

  const handleLogin = async (username: string, password: string) => {
    setLoadingState(true);
    try {
      await login(username, password);
      setMessage('Login successful!');
      setActiveTab('dashboard');
    } catch (error) {
      setMessage('Login failed. Please check your credentials.');
      console.error('Login error:', error);
    } finally {
      setLoadingState(false);
    }
  };

  const handleRegister = async (userData: any) => {
    setLoadingState(true);
    try {
      await register(userData);
      setMessage('Registration successful! Welcome to Jeseci Academy.');
      setActiveTab('dashboard');
    } catch (error) {
      setMessage('Registration failed. Please try again.');
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

  // =============================================================================
  // AUTH FORMS
  // =============================================================================

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
          <button type="submit" disabled={loadingState}>
            {loadingState ? 'Logging in...' : 'Login'}
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
          <button type="submit" disabled={loadingState}>
            {loadingState ? 'Registering...' : 'Register'}
          </button>
        </form>
        
        <div className="auth-switch">
          <p>Already have an account?</p>
          <button onClick={() => setActiveTab('login')}>Login</button>
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
                <p className="stat-number">{userProgress.progress.courses_completed}</p>
              </div>
              <div className="stat-card">
                <h3>Lessons Completed</h3>
                <p className="stat-number">{userProgress.progress.lessons_completed}</p>
              </div>
              <div className="stat-card">
                <h3>Study Time</h3>
                <p className="stat-number">{userProgress.progress.total_study_time} mins</p>
              </div>
              <div className="stat-card">
                <h3>Current Streak</h3>
                <p className="stat-number">{userProgress.progress.current_streak} days</p>
              </div>
            </div>

            {userProgress.recent_activity && userProgress.recent_activity.length > 0 && (
              <div className="recent-activity-section">
                <h3>Recent Activity</h3>
                {userProgress.recent_activity.slice(0, 5).map((activity) => (
                  <div key={activity.session_id} className="activity-item">
                    <span className="activity-course">{activity.course_title}</span>
                    <span className="activity-status">{activity.status}</span>
                    <span className="activity-progress">{activity.progress}%</span>
                  </div>
                ))}
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
                  ))}
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
              {courses.map((course) => (
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
              ))}
            </div>
          </div>
        )}

        {/* LEARNING PATHS */}
        {activeTab === 'paths' && (
          <div className="paths-section">
            <h2>Learning Paths</h2>
            <p>Structured paths to master specific skills</p>
            <div className="paths-grid">
              {learningPaths.map((path) => (
                <div key={path.id} className="path-card">
                  <h3>{path.title}</h3>
                  <p>{path.description}</p>
                  <div className="path-progress">
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${path.progress}%` }}></div>
                    </div>
                    <span>{path.progress}% complete</span>
                  </div>
                  <div className="path-modules">
                    <span>{path.courses.length} modules</span>
                    <span>{path.duration}</span>
                  </div>
                  <button onClick={() => setActiveTab('concepts')}>Continue Path</button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CONCEPTS */}
        {activeTab === 'concepts' && (
          <div className="concepts-section">
            <h2>Concepts Library</h2>
            <p>Explore topics across different domains</p>
            <div className="concepts-grid">
              {concepts.map((concept) => (
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
                <p className="stat-number">{userProgress.progress.courses_completed}</p>
              </div>
              <div className="stat-card">
                <h3>Lessons Completed</h3>
                <p className="stat-number">{userProgress.progress.lessons_completed}</p>
              </div>
              <div className="stat-card">
                <h3>Study Time</h3>
                <p className="stat-number">{userProgress.progress.total_study_time} mins</p>
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
              <p><strong>Average Score:</strong> {userProgress.analytics.average_progress.toFixed(1)}%</p>
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
                  {achievements.filter(a => a.earned).map((achievement) => (
                    <div key={achievement.id} className="achievement-card earned">
                      <span className="achievement-icon">{achievement.icon}</span>
                      <h4>{achievement.name}</h4>
                      <p>{achievement.description}</p>
                      <span className="achievement-date">Earned: {achievement.earned_at}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="achievement-category">
                <h3>Locked Achievements</h3>
                <div className="achievements-grid">
                  {achievements.filter(a => !a.earned).map((achievement) => (
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
              {quizzes.map((quiz) => (
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
              ))}
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
                  chatMessages.map((msg) => (
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
              <h3>Personalized Recommendations</h3>
              <ul>
                {analytics.recommendations.map((rec, index) => (
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
      <header className="app-header">
        <div className="header-content">
          <h1>🎓 Jeseci Smart Learning Academy</h1>
          <p>AI-Powered Personalized Learning</p>
          {isAuthenticated && (
            <div className="header-actions">
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
        {!isAuthenticated ? (
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
        <p>© 2025 Jeseci Smart Learning Academy • Pure Jaclang Backend</p>
        <p>Powered by React + Jaclang + OpenAI</p>
      </footer>
    </div>
  );
};

// Wrap App with AuthProvider
const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
