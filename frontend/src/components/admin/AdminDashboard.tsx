/**
 * Admin Dashboard - Comprehensive admin dashboard integrating all admin components
 * Now with real-time data from the backend API
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useAdmin } from '../../contexts/AdminContext';
import { AdminUserActivity } from './AdminUserActivity';
import { AdminTableActivity } from './AdminTableActivity';
import { AdminCacheManagement } from './AdminCacheManagement';
import { AdminAuditLogs } from './AdminAuditLogs';
import { AdminAuditHistory } from './AdminAuditHistory';
import './AdminDashboard.css';

// Type definitions for dashboard statistics
interface DashboardStats {
  users: {
    total_users: number;
    active_users: number;
    new_this_week: number;
    week_over_week_change: number;
  };
  content: {
    total_items: number;
    concepts: number;
    learning_paths: number;
    lessons: number;
    new_this_week: number;
    content_change: number;
  };
  activity: {
    daily_activity: number;
    weekly_sessions: number;
    active_users: number;
    avg_session_duration: number;
    activity_change: number;
  };
  issues: {
    pending: number;
    critical: number;
    resolved_this_week: number;
    issue_change: number;
  };
  progress: {
    completed_concepts: number;
    in_progress: number;
    quiz_pass_rate: number;
    avg_progress: number;
  };
  generated_at: string;
}

interface AdminDashboardProps {
  activeSection: string;
  onNavigate: (section: string) => void;
}

// Helper function to format numbers with commas
const formatNumber = (num: number): string => {
  return num.toLocaleString();
};

// Helper function to format percentage change
const formatChange = (change: number, isPositive: boolean): string => {
  const sign = change >= 0 ? '+' : '';
  return `${sign}${change.toFixed(1)}%`;
};

// Helper to determine if change is positive
const isPositiveChange = (change: number): boolean => {
  return change >= 0;
};

const AdminDashboard: React.FC<AdminDashboardProps> = ({ activeSection, onNavigate }) => {
  const { adminUser, isAuthenticated } = useAdmin();
  const [dateRange, setDateRange] = useState<'day' | 'week' | 'month'>('week');
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch dashboard statistics from API
  const fetchDashboardStats = useCallback(async () => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await fetch('/api/admin/dashboard/stats', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success && data.data) {
        setStats(data.data);
      } else {
        throw new Error(data.detail || 'Failed to fetch statistics');
      }
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
      setError(err instanceof Error ? err.message : 'Failed to load statistics');
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  // Fetch stats on component mount
  useEffect(() => {
    fetchDashboardStats();
  }, [fetchDashboardStats]);

  // Refresh stats when date range changes
  useEffect(() => {
    if (dateRange) {
      fetchDashboardStats();
    }
  }, [dateRange, fetchDashboardStats]);

  // Loading skeleton component
  const LoadingSkeleton: React.FC = () => (
    <div className="stat-card skeleton">
      <div className="stat-icon skeleton-icon"></div>
      <div className="stat-content">
        <span className="stat-label skeleton-text"></span>
        <span className="stat-value skeleton-text"></span>
        <span className="stat-change skeleton-text"></span>
      </div>
    </div>
  );

  // Error display component
  const ErrorDisplay: React.FC<{ message: string }> = ({ message }) => (
    <div className="error-banner">
      <span className="error-icon">⚠️</span>
      <span className="error-message">{message}</span>
      <button className="retry-btn" onClick={fetchDashboardStats}>
        Retry
      </button>
    </div>
  );

  return (
    <div className="admin-dashboard">
      {/* Welcome Header */}
      <div className="dashboard-header">
        <div className="welcome-section">
          <h1>Welcome back, {adminUser?.first_name || adminUser?.username || 'Administrator'}!</h1>
          <p>Here's what's happening with your platform today.</p>
        </div>
        <div className="date-selector">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value as 'day' | 'week' | 'month')}
            className="date-range-select"
          >
            <option value="day">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
          </select>
        </div>
      </div>

      {/* Error Display */}
      {error && <ErrorDisplay message={error} />}

      {/* Quick Stats Overview */}
      <div className="stats-overview">
        {/* Users Stat Card */}
        <div className="stat-card users">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <span className="stat-label">Total Users</span>
            {loading || !stats ? (
              <span className="stat-value skeleton-text"></span>
            ) : (
              <span className="stat-value">{formatNumber(stats.users.total_users)}</span>
            )}
            {loading || !stats ? (
              <span className="stat-change skeleton-text"></span>
            ) : (
              <span className={`stat-change ${isPositiveChange(stats.users.week_over_week_change) ? 'positive' : 'negative'}`}>
                {formatChange(stats.users.week_over_week_change, isPositiveChange(stats.users.week_over_week_change))} this week
              </span>
            )}
          </div>
        </div>

        {/* Content Items Stat Card */}
        <div className="stat-card content">
          <div className="stat-icon">📚</div>
          <div className="stat-content">
            <span className="stat-label">Content Items</span>
            {loading || !stats ? (
              <span className="stat-value skeleton-text"></span>
            ) : (
              <span className="stat-value">{formatNumber(stats.content.total_items)}</span>
            )}
            {loading || !stats ? (
              <span className="stat-change skeleton-text"></span>
            ) : (
              <span className={`stat-change ${isPositiveChange(stats.content.content_change) ? 'positive' : 'negative'}`}>
                {formatChange(stats.content.content_change, isPositiveChange(stats.content.content_change))} this week
              </span>
            )}
          </div>
        </div>

        {/* Daily Activity Stat Card */}
        <div className="stat-card activity">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <span className="stat-label">Daily Activity</span>
            {loading || !stats ? (
              <span className="stat-value skeleton-text"></span>
            ) : (
              <span className="stat-value">{formatNumber(stats.activity.daily_activity)}</span>
            )}
            {loading || !stats ? (
              <span className="stat-change skeleton-text"></span>
            ) : (
              <span className={`stat-change ${isPositiveChange(stats.activity.activity_change) ? 'positive' : 'negative'}`}>
                {formatChange(stats.activity.activity_change, isPositiveChange(stats.activity.activity_change))} this week
              </span>
            )}
          </div>
        </div>

        {/* Pending Issues Stat Card */}
        <div className="stat-card issues">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <span className="stat-label">Pending Issues</span>
            {loading || !stats ? (
              <span className="stat-value skeleton-text"></span>
            ) : (
              <span className="stat-value">{formatNumber(stats.issues.pending)}</span>
            )}
            {loading || !stats ? (
              <span className="stat-change skeleton-text"></span>
            ) : (
              <span className="stat-change negative">
                {stats.issues.critical > 0 ? `${stats.issues.critical} critical` : 'All clear'}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="actions-grid">
          <button
            className="action-btn"
            onClick={() => onNavigate('user-activity')}
          >
            <span className="action-icon">👥</span>
            <span className="action-label">User Activity</span>
          </button>
          <button
            className="action-btn"
            onClick={() => onNavigate('table-activity')}
          >
            <span className="action-icon">🗄️</span>
            <span className="action-label">Database Activity</span>
          </button>
          <button
            className="action-btn"
            onClick={() => onNavigate('cache-management')}
          >
            <span className="action-icon">💾</span>
            <span className="action-label">Cache Management</span>
          </button>
          <button
            className="action-btn"
            onClick={() => onNavigate('audit-logs')}
          >
            <span className="action-icon">📋</span>
            <span className="action-label">Audit Logs</span>
          </button>
          <button
            className="action-btn"
            onClick={() => onNavigate('audit-history')}
          >
            <span className="action-icon">📜</span>
            <span className="action-label">Audit History</span>
          </button>
        </div>
      </div>

      {/* Recent Activity Feed */}
      <div className="recent-activity-section">
        <h2>Recent Admin Activity</h2>
        <div className="activity-feed">
          <div className="activity-item">
            <span className="activity-icon">👤</span>
            <div className="activity-content">
              <p><strong>User Management</strong> - {loading || !stats ? 'Loading...' : `${stats.users.new_this_week} new users registered`}</p>
              <span className="activity-time">5 minutes ago</span>
            </div>
          </div>
          <div className="activity-item">
            <span className="activity-icon">📝</span>
            <div className="activity-content">
              <p><strong>Content Moderation</strong> - {loading || !stats ? 'Loading...' : `${stats.content.new_this_week} new items added`}</p>
              <span className="activity-time">15 minutes ago</span>
            </div>
          </div>
          <div className="activity-item">
            <span className="activity-icon">🔧</span>
            <div className="activity-content">
              <p><strong>System</strong> - Cache cleared successfully</p>
              <span className="activity-time">1 hour ago</span>
            </div>
          </div>
          <div className="activity-item">
            <span className="activity-icon">🛡️</span>
            <div className="activity-content">
              <p><strong>Security</strong> - Failed login attempt blocked (IP: 192.168.1.xxx)</p>
              <span className="activity-time">2 hours ago</span>
            </div>
          </div>
        </div>
      </div>

      {/* Data Quality Notice */}
      {!loading && !error && stats && (
        <div className="data-quality-notice">
          <span className="notice-icon">ℹ️</span>
          <span className="notice-text">
            Statistics updated: {new Date(stats.generated_at).toLocaleString()}
          </span>
        </div>
      )}
    </div>
  );
};

// User Activity Page
export const UserActivityPage: React.FC<{ onNavigate: (section: string) => void }> = ({ onNavigate }) => (
  <div className="admin-page">
    <div className="page-header">
      <button className="back-btn" onClick={() => onNavigate('dashboard')}>← Back to Dashboard</button>
      <h1>User Activity Monitoring</h1>
      <p>Track user engagement, login activity, and behavioral patterns</p>
    </div>
    <AdminUserActivity />
  </div>
);

// Table Activity Page
export const TableActivityPage: React.FC<{ onNavigate: (section: string) => void }> = ({ onNavigate }) => (
  <div className="admin-page">
    <div className="page-header">
      <button className="back-btn" onClick={() => onNavigate('dashboard')}>← Back to Dashboard</button>
      <h1>Database Table Activity</h1>
      <p>Monitor database performance, table sizes, and query activity</p>
    </div>
    <AdminTableActivity />
  </div>
);

// Cache Management Page
export const CacheManagementPage: React.FC<{ onNavigate: (section: string) => void }> = ({ onNavigate }) => (
  <div className="admin-page">
    <div className="page-header">
      <button className="back-btn" onClick={() => onNavigate('dashboard')}>← Back to Dashboard</button>
      <h1>Cache Management</h1>
      <p>Manage content cache, clear cache regions, and monitor cache performance</p>
    </div>
    <AdminCacheManagement />
  </div>
);

// Audit Logs Page
export const AuditLogsPage: React.FC<{ onNavigate: (section: string) => void }> = ({ onNavigate }) => (
  <div className="admin-page">
    <div className="page-header">
      <button className="back-btn" onClick={() => onNavigate('dashboard')}>← Back to Dashboard</button>
      <h1>Audit Logs</h1>
      <p>View comprehensive audit logs for system monitoring and security</p>
    </div>
    <AdminAuditLogs />
  </div>
);

// Audit History Page
export const AuditHistoryPage: React.FC<{ onNavigate: (section: string) => void }> = ({ onNavigate }) => (
  <div className="admin-page">
    <div className="page-header">
      <button className="back-btn" onClick={() => onNavigate('dashboard')}>← Back to Dashboard</button>
      <h1>Audit History</h1>
      <p>Track historical changes and analyze trends over time</p>
    </div>
    <AdminAuditHistory />
  </div>
);

export default AdminDashboard;
