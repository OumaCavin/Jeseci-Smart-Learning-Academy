/**
 * Admin Context - Provides admin authentication state and methods
 * Includes automatic session timeout after 3 minutes of inactivity
 */

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { apiService, User } from '../services/api';
import { useSessionTimeout } from '../hooks/useSessionTimeout';
import SessionTimeoutModal from '../components/SessionTimeoutModal';

interface AdminContextType {
  isAdminAuthenticated: boolean;
  adminUser: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshAdminData: () => Promise<void>;
  showSessionWarning: boolean;
  sessionTimeRemaining: number;
}

const AdminContext = createContext<AdminContextType | undefined>(undefined);

const ADMIN_TOKEN_KEY = 'jeseci_admin_token';
const ADMIN_USER_KEY = 'jeseci_admin_user';

export const AdminProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState<boolean>(false);
  const [adminUser, setAdminUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Session timeout state
  const [showSessionWarning, setShowSessionWarning] = useState(false);
  const [sessionTimeRemaining, setSessionTimeRemaining] = useState(0);

  // Handle logout from session timeout
  const handleSessionTimeout = useCallback(() => {
    console.log('Admin session timeout - logging out admin');
    localStorage.removeItem(ADMIN_TOKEN_KEY);
    localStorage.removeItem(ADMIN_USER_KEY);
    setAdminUser(null);
    setIsAdminAuthenticated(false);
    setShowSessionWarning(false);
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

  useEffect(() => {
    const initAdminAuth = async () => {
      try {
        const storedToken = localStorage.getItem(ADMIN_TOKEN_KEY);
        const storedUser = localStorage.getItem(ADMIN_USER_KEY);

        if (storedToken && storedUser) {
          const userData = JSON.parse(storedUser) as User;
          
          // Verify admin status
          if (userData.is_admin) {
            setAdminUser(userData);
            setIsAdminAuthenticated(true);
            console.log('Admin session restored successfully');
          } else {
            // User is not admin, clear storage
            localStorage.removeItem(ADMIN_TOKEN_KEY);
            localStorage.removeItem(ADMIN_USER_KEY);
          }
        }
      } catch (error) {
        console.error('Error initializing admin auth:', error);
      } finally {
        setLoading(false);
      }
    };

    initAdminAuth();
  }, []);

  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      const response = await apiService.login(username, password);
      
      if (response.success && response.user) {
        const userData = response.user;
        const authToken = response.access_token || response.token;

        // Check if user has admin privileges
        if (userData.is_admin) {
          localStorage.setItem(ADMIN_TOKEN_KEY, authToken);
          localStorage.setItem(ADMIN_USER_KEY, JSON.stringify(userData));

          setAdminUser(userData);
          setIsAdminAuthenticated(true);

          // Reset session timeout on admin login
          resetSession();
        } else {
          throw new Error('Access denied. Admin privileges required.');
        }
      } else {
        throw new Error('Login failed. Please check your credentials.');
      }
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem(ADMIN_TOKEN_KEY);
    localStorage.removeItem(ADMIN_USER_KEY);
    setAdminUser(null);
    setIsAdminAuthenticated(false);
    setShowSessionWarning(false);

    // Clean up session timeout
    sessionLogout();
  };

  const refreshAdminData = async () => {
    if (adminUser) {
      try {
        // Re-verify admin status
        const response = await apiService.login(adminUser.username, '');
        if (response.success && response.user?.is_admin) {
          setAdminUser(response.user);
        } else {
          logout();
        }
      } catch (error) {
        console.error('Error refreshing admin data:', error);
        logout();
      }
    }
  };

  return (
    <AdminContext.Provider
      value={{
        isAdminAuthenticated,
        adminUser,
        loading,
        login,
        logout,
        refreshAdminData,
        showSessionWarning,
        sessionTimeRemaining
      }}
    >
      {children}
      {/* Session Timeout Modal - Only show when authenticated and warning is active */}
      {isAdminAuthenticated && showSessionWarning && (
        <SessionTimeoutModal
          show={showSessionWarning}
          remainingSeconds={sessionTimeRemaining}
          onStayLoggedIn={resetSession}
          formatTime={formatTime}
        />
      )}
    </AdminContext.Provider>
  );
};

export const useAdmin = (): AdminContextType => {
  const context = useContext(AdminContext);
  if (context === undefined) {
    throw new Error('useAdmin must be used within an AdminProvider');
  }
  return context;
};

export default AdminContext;
