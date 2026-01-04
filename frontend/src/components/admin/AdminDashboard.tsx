/**
 * Admin Dashboard - Comprehensive admin dashboard integrating all admin components
 */

import React, { useState } from 'react';
import { useAdmin } from '../../contexts/AdminContext';
import { AdminUserActivity } from './AdminUserActivity';
import { AdminTableActivity } from './AdminTableActivity';
import { AdminCacheManagement } from './AdminCacheManagement';
import { AdminAuditLogs } from './AdminAuditLogs';
import { AdminAuditHistory } from './AdminAuditHistory';
import './AdminDashboard.css';

interface AdminDashboardProps {
  activeSection: string;
  onNavigate: (section: string) => void;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ activeSection, onNavigate }) => {
  const { adminUser } = useAdmin();
  const [dateRange, setDateRange] = useState<'day' | 'week' | 'month'>('week');

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

      {/* Quick Stats Overview */}
      <div className="stats-overview">
        <div className="stat-card users">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <span className="stat-label">Total Users</span>
            <span className="stat-value">1,234</span>
            <span className="stat-change positive">+12% this week</span>
          </div>
        </div>
        <div className="stat-card content">
          <div className="stat-icon">📚</div>
          <div className="stat-content">
            <span className="stat-label">Content Items</span>
            <span className="stat-value">5,678</span>
            <span className="stat-change positive">+8% this week</span>
          </div>
        </div>
        <div className="stat-card activity">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <span className="stat-label">Daily Activity</span>
            <span className="stat-value">892</span>
            <span className="stat-change positive">+5% this week</span>
          </div>
        </div>
        <div className="stat-card issues">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <span className="stat-label">Pending Issues</span>
            <span className="stat-value">12</span>
            <span className="stat-change negative">3 critical</span>
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
              <p><strong>User Management</strong> - 3 new users registered</p>
              <span className="activity-time">5 minutes ago</span>
            </div>
          </div>
          <div className="activity-item">
            <span className="activity-icon">📝</span>
            <div className="activity-content">
              <p><strong>Content Moderation</strong> - 2 items approved, 1 rejected</p>
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
