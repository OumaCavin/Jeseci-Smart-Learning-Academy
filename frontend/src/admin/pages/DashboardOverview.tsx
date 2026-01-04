/**
 * Dashboard Overview Page - Admin dashboard statistics
 */

import React, { useState, useEffect } from 'react';
import adminApi from '../../services/adminApi';
import '../Admin.css';

interface DashboardOverviewProps {
  activeSection: string;
  onNavigate: (section: string) => void;
}

const DashboardOverview: React.FC<DashboardOverviewProps> = ({ activeSection, onNavigate }) => {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (activeSection === 'dashboard') {
      loadDashboardStats();
    }
  }, [activeSection]);

  const loadDashboardStats = async () => {
    setLoading(true);
    try {
      const response = await adminApi.getDashboardStats();
      if (response.success) {
        setStats(response.stats);
      } else {
        setError('Failed to load dashboard statistics');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="spinner"></div>
        <span>Loading dashboard...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="empty-state">
        <h3>Error Loading Dashboard</h3>
        <p>{error}</p>
        <button className="btn btn-primary" onClick={loadDashboardStats}>
          Try Again
        </button>
      </div>
    );
  }

  const userStats = stats?.user_statistics || {};
  const adminStats = stats?.admin_statistics || {};
  const systemHealth = stats?.system_health || {};

  return (
    <div className="dashboard-overview">
      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-value">{userStats.total_users || 0}</div>
          <div className="stat-label">Total Users</div>
          <div className="stat-change positive">
            +{userStats.new_users_this_week || 0} this week
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-value">{userStats.active_users || 0}</div>
          <div className="stat-label">Active Users</div>
          <div className="stat-change positive">
            {userStats.inactive_users || 0} inactive
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">👑</div>
          <div className="stat-value">{userStats.total_admins || 0}</div>
          <div className="stat-label">Administrators</div>
          <div className="stat-change">
            Role distribution available
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🖥️</div>
          <div className="stat-value">{systemHealth.api_status || 'N/A'}</div>
          <div className="stat-label">System Status</div>
          <div className="stat-change positive">
            Database: {systemHealth.database_status}
          </div>
        </div>
      </div>

      {/* Admin Role Distribution */}
      <div className="admin-card" style={{ marginBottom: '24px' }}>
        <div className="admin-card-header">
          <h2>Admin Role Distribution</h2>
        </div>
        <div className="admin-card-body">
          {Object.keys(adminStats.role_distribution || {}).length > 0 ? (
            <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
              {Object.entries(adminStats.role_distribution).map(([role, count]) => (
                <div key={role} style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '32px', fontWeight: '700', color: '#1f2937' }}>
                    {count as number}
                  </div>
                  <div style={{ fontSize: '14px', color: '#6b7280', textTransform: 'capitalize' }}>
                    {role.replace('_', ' ')}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>No admin users found</p>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="admin-card">
        <div className="admin-card-header">
          <h2>Quick Actions</h2>
        </div>
        <div className="admin-card-body">
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <button
              className="btn btn-primary"
              onClick={() => onNavigate('users')}
            >
              👤 Create Admin User
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => onNavigate('content')}
            >
              📚 Add New Course
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => onNavigate('quizzes')}
            >
              📝 Create Quiz
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => onNavigate('ai')}
            >
              🤖 Generate AI Content
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => onNavigate('analytics')}
            >
              📊 View Full Analytics
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardOverview;
