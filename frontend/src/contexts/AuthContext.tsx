/**
 * Auth Context - Provides authentication state and methods throughout the app
 * Includes automatic session timeout after 3 minutes of inactivity
 */

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { apiService, User } from '../services/api';
import { useSessionTimeout } from '../hooks/useSessionTimeout';
import SessionTimeoutModal from '../components/SessionTimeoutModal';

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  refreshUserData: () => Promise<void>;
  showSessionWarning: boolean;
  sessionTimeRemaining: number;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  learning_style?: string;
  skill_level?: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Storage keys
const AUTH_TOKEN_KEY = 'jeseci_auth_token';
const AUTH_USER_KEY = 'jeseci_auth_user';

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Session timeout state
  const [showSessionWarning, setShowSessionWarning] = useState(false);
  const [sessionTimeRemaining, setSessionTimeRemaining] = useState(0);

  // Initialize auth state from localStorage on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedToken = localStorage.getItem(AUTH_TOKEN_KEY);
        const storedUser = localStorage.getItem(AUTH_USER_KEY);

        if (storedToken && storedUser) {
          const userData = JSON.parse(storedUser);
          setToken(storedToken);
          setUser(userData);
          setIsAuthenticated(true);
          
          // Verify token is still valid by fetching fresh user data
          try {
            const progress = await apiService.getUserProgress(userData.user_id);
            if (progress) {
              // Token is valid, user stays logged in
              console.log('Session restored successfully');
            }
          } catch (error) {
            // Token expired (5-minute timeout for security), clear storage
            console.log('Session expired, logging out for security');
            localStorage.removeItem(AUTH_TOKEN_KEY);
            localStorage.removeItem(AUTH_USER_KEY);
            setToken(null);
            setUser(null);
            setIsAuthenticated(false);
          }
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  // Handle logout from session timeout
  const handleSessionTimeout = useCallback(() => {
    console.log('Session timeout - logging out user');
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    setShowSessionWarning(false);
  }, []);

  // Handle warning dismissed (user activity detected)
  const handleWarningDismissed = useCallback(() => {
    setShowSessionWarning(false);
    setSessionTimeRemaining(0);
  }, []);

  // Initialize session timeout when authenticated
  const {
    logout: sessionLogout,
    resetSession,
    warningTimeRemaining,
    showWarning,
    formatTime
  } = useSessionTimeout(handleSessionTimeout);

  // Update session warning state
  useEffect(() => {
    setShowSessionWarning(showWarning);
    if (showWarning) {
      setSessionTimeRemaining(Math.ceil(warningTimeRemaining / 1000));
    }
  }, [showWarning, warningTimeRemaining]);

  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      const response = await apiService.login(username, password);
      
      if (response.success && response.user) {
        const userData = response.user;
        const authToken = response.access_token || response.token;

        if (!authToken) {
          throw new Error('No token received from server');
        }

        // Store in localStorage for session persistence
        localStorage.setItem(AUTH_TOKEN_KEY, authToken);
        localStorage.setItem(AUTH_USER_KEY, JSON.stringify(userData));

        setToken(authToken);
        setUser(userData);
        setIsAuthenticated(true);

        // Reset session timeout on login
        resetSession();
      } else {
        // Provide detailed error messages based on error code
        const errorCode = response.code || '';
        const errorMessage = response.message || response.error || '';

        if (errorCode === 'CONFLICT' || errorMessage.includes('already exists')) {
          throw new Error('Username or email already exists. Please use different credentials or try logging in.');
        } else if (errorCode === 'UNAUTHORIZED' || errorMessage.includes('Invalid credentials')) {
          throw new Error('Invalid username or password. Please check your credentials and try again.');
        } else if (errorCode === 'VALIDATION_ERROR' || errorMessage.includes('validation')) {
          throw new Error('Please check your input. All fields are required and must be valid.');
        } else {
          throw new Error(errorMessage || 'Login failed due to an unknown server error.');
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData: RegisterData) => {
    setLoading(true);
    try {
      const response = await apiService.register(userData);

      if (response.success && response.user) {
        const newUserData = response.user;
        const authToken = response.access_token || response.token;

        if (!authToken) {
          throw new Error('No token received from server');
        }

        // Store in localStorage for session persistence
        localStorage.setItem(AUTH_TOKEN_KEY, authToken);
        localStorage.setItem(AUTH_USER_KEY, JSON.stringify(newUserData));

        setToken(authToken);
        setUser(newUserData);
        setIsAuthenticated(true);

        // Reset session timeout on registration
        resetSession();
      } else {
        // Provide detailed error messages based on error code
        const errorCode = response.code || '';
        const errorMessage = response.message || response.error || '';

        if (errorCode === 'CONFLICT' || errorMessage.includes('already exists')) {
          throw new Error('Username or email already exists. Please use different credentials or try logging in.');
        } else if (errorCode === 'VALIDATION_ERROR' || errorMessage.includes('validation') || errorMessage.includes('required')) {
          throw new Error('Please check your input. All fields are required and must be valid.');
        } else if (errorMessage.includes('password')) {
          throw new Error('Password requirements not met. Please ensure your password meets the criteria.');
        } else if (errorMessage.includes('email')) {
          throw new Error('Invalid email format. Please enter a valid email address.');
        } else {
          throw new Error(errorMessage || 'Registration failed due to an unknown server error.');
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    // Clear localStorage
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);

    // Reset state
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    setShowSessionWarning(false);

    // Clean up session timeout
    sessionLogout();
  };

  const refreshUserData = async () => {
    if (user) {
      try {
        const progress = await apiService.getUserProgress(user.user_id);
        const analytics = await apiService.getAnalytics(user.user_id);
        
        // Update user state with fresh data
        setUser({
          ...user,
          progress: progress
        });
      } catch (error) {
        console.error('Error refreshing user data:', error);
      }
    }
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        user,
        token,
        loading,
        login,
        register,
        logout,
        refreshUserData,
        showSessionWarning,
        sessionTimeRemaining
      }}
    >
      {children}
      {/* Session Timeout Modal - Only show when authenticated and warning is active */}
      {isAuthenticated && showSessionWarning && (
        <SessionTimeoutModal
          show={showSessionWarning}
          remainingSeconds={sessionTimeRemaining}
          onStayLoggedIn={resetSession}
          formatTime={formatTime}
        />
      )}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
