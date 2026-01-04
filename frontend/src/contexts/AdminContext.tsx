/**
 * Admin Context - Provides admin authentication state and methods
 * Includes automatic session timeout after 3 minutes of inactivity
 * Provides permission-based authorization for admin features
 */

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { apiService, User } from '../services/api';
import { useSessionTimeout } from '../hooks/useSessionTimeout';
import SessionTimeoutModal from '../components/SessionTimeoutModal';

// Admin permission types
interface AdminPermissions {
  canManageUsers: boolean;
  canManageContent: boolean;
  canManageQuizzes: boolean;
  canAccessAI: boolean;
  canViewAnalytics: boolean;
  canViewUserActivity: boolean;
  canViewDatabaseActivity: boolean;
  canManageCache: boolean;
  canViewAuditLogs: boolean;
  canViewAuditHistory: boolean;
  canManageSystem: boolean;
}

export interface SystemUser {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'super_admin' | 'moderator';
  permissions: AdminPermissions;
  lastLogin?: string;
  createdAt: string;
  isActive: boolean;
}

export interface AuditLogEntry {
  id: string;
  userId: string;
  userName: string;
  action: string;
  resource: string;
  resourceId?: string;
  details?: Record<string, unknown>;
  ipAddress: string;
  userAgent: string;
  timestamp: string;
  status: 'success' | 'failure';
}

export interface SystemMetrics {
  totalUsers: number;
  activeUsers: number;
  totalCourses: number;
  activeCourses: number;
  totalExecutions: number;
  avgExecutionTime: number;
  storageUsed: number;
  memoryUsed: number;
  cpuUsage: number;
  uptime: number;
}

export interface SystemHealth {
  status: 'healthy' | 'warning' | 'critical';
  checks: Array<{
    name: string;
    status: 'pass' | 'fail' | 'warn';
    message?: string;
    lastChecked: string;
  }>;
  lastUpdated: string;
}

export interface UserFilter {
  search?: string;
  role?: string;
  status?: 'active' | 'inactive' | 'banned';
  dateRange?: { start: string; end: string };
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  page: number;
  pageSize: number;
}

export interface AuditLogFilter {
  userId?: string;
  action?: string;
  resource?: string;
  status?: 'success' | 'failure';
  dateRange?: { start: string; end: string };
  ipAddress?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  page: number;
  pageSize: number;
}

export interface BulkUserAction {
  action: 'activate' | 'deactivate' | 'ban' | 'unban' | 'delete' | 'role';
  userIds: string[];
  reason?: string;
}

export interface AdminContextType {
  isAdminAuthenticated: boolean;
  adminUser: User | null;
  loading: boolean;
  permissions: AdminPermissions | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshAdminData: () => Promise<void>;
  showSessionWarning: boolean;
  sessionTimeRemaining: number;
  hasPermission: (permission: keyof AdminPermissions) => boolean;
}

const AdminContext = createContext<AdminContextType | undefined>(undefined);

const ADMIN_TOKEN_KEY = 'jeseci_admin_token';
const ADMIN_USER_KEY = 'jeseci_admin_user';

// Default permissions based on admin role
const getDefaultPermissions = (adminRole?: string): AdminPermissions => {
  switch (adminRole) {
    case 'super_admin':
      return {
        canManageUsers: true,
        canManageContent: true,
        canManageQuizzes: true,
        canAccessAI: true,
        canViewAnalytics: true,
        canViewUserActivity: true,
        canViewDatabaseActivity: true,
        canManageCache: true,
        canViewAuditLogs: true,
        canViewAuditHistory: true,
        canManageSystem: true
      };
    case 'content_admin':
      return {
        canManageUsers: false,
        canManageContent: true,
        canManageQuizzes: true,
        canAccessAI: true,
        canViewAnalytics: true,
        canViewUserActivity: false,
        canViewDatabaseActivity: false,
        canManageCache: false,
        canViewAuditLogs: false,
        canViewAuditHistory: false,
        canManageSystem: false
      };
    case 'moderator':
      return {
        canManageUsers: false,
        canManageContent: true,
        canManageQuizzes: false,
        canAccessAI: false,
        canViewAnalytics: false,
        canViewUserActivity: false,
        canViewDatabaseActivity: false,
        canManageCache: false,
        canViewAuditLogs: true,
        canViewAuditHistory: true,
        canManageSystem: false
      };
    case 'viewer':
      return {
        canManageUsers: false,
        canManageContent: false,
        canManageQuizzes: false,
        canAccessAI: false,
        canViewAnalytics: true,
        canViewUserActivity: false,
        canViewDatabaseActivity: false,
        canManageCache: false,
        canViewAuditLogs: false,
        canViewAuditHistory: false,
        canManageSystem: false
      };
    default:
      // Default to full access for regular admin
      return {
        canManageUsers: true,
        canManageContent: true,
        canManageQuizzes: true,
        canAccessAI: true,
        canViewAnalytics: true,
        canViewUserActivity: true,
        canViewDatabaseActivity: true,
        canManageCache: true,
        canViewAuditLogs: true,
        canViewAuditHistory: true,
        canManageSystem: false
      };
  }
};

export const AdminProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState<boolean>(false);
  const [adminUser, setAdminUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [permissions, setPermissions] = useState<AdminPermissions | null>(null);

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
            setPermissions(getDefaultPermissions(userData.admin_role));
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
          setPermissions(getDefaultPermissions(userData.admin_role));

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
    setPermissions(null);
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
          setPermissions(getDefaultPermissions(response.user.admin_role));
        } else {
          logout();
        }
      } catch (error) {
        console.error('Error refreshing admin data:', error);
        logout();
      }
    }
  };

  // Permission check helper
  const hasPermission = useCallback((permission: keyof AdminPermissions): boolean => {
    if (!permissions) return false;
    return permissions[permission];
  }, [permissions]);

  return (
    <AdminContext.Provider
      value={{
        isAdminAuthenticated,
        adminUser,
        loading,
        permissions,
        login,
        logout,
        refreshAdminData,
        showSessionWarning,
        sessionTimeRemaining,
        hasPermission
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
