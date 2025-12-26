/**
 * Admin Context - Provides admin authentication state and methods
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiService } from '../services/api';

interface AdminUser {
  user_id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_admin: boolean;
  admin_role: string;
}

interface AdminContextType {
  isAdminAuthenticated: boolean;
  adminUser: AdminUser | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshAdminData: () => Promise<void>;
}

const AdminContext = createContext<AdminContextType | undefined>(undefined);

const ADMIN_TOKEN_KEY = 'jeseci_admin_token';
const ADMIN_USER_KEY = 'jeseci_admin_user';

export const AdminProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState<boolean>(false);
  const [adminUser, setAdminUser] = useState<AdminUser | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const initAdminAuth = async () => {
      try {
        const storedToken = localStorage.getItem(ADMIN_TOKEN_KEY);
        const storedUser = localStorage.getItem(ADMIN_USER_KEY);

        if (storedToken && storedUser) {
          const userData = JSON.parse(storedUser);
          
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
        refreshAdminData
      }}
    >
      {children}
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
