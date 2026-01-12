/**
 * Dashboard Overview Page - Admin dashboard statistics
 * Shows role-appropriate stats and quick actions based on user permissions
 */

import React, { useState, useEffect, useContext } from 'react';
import adminApi from '../../services/adminApi';
import AdminContext, { AdminPermissions } from '../../contexts/AdminContext';
import '../Admin.css';

interface DashboardOverviewProps {
  activeSection: string;
  onNavigate: (section: string) => void;
}

const DashboardOverview: React.FC<DashboardOverviewProps> = ({ activeSection, onNavigate }) => {
  const { permissions } = useContext(AdminContext);
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

  // Define quick actions based on permissions
  const getQuickActions = (perms: AdminPermissions | null) => {
    const actions = [];

    if (perms?.canManageUsers) {
      actions.push(
        { id: 'users', label: '👤 Create Admin User', type: 'primary' },
        { id: 'user-activity', label: '📊 View User Activity', type: 'secondary' }
      );
    }

    if (perms?.canManageContent) {
      actions.push(
        { id: 'content', label: '📚 Add New Course', type: 'secondary' },
        { id: 'table-activity', label: '🗄️ Database Activity', type: 'secondary' }
      );
    }

    if (perms?.canManageQuizzes) {
      actions.push(
        { id: 'quizzes', label: '📝 Create Quiz', type: 'secondary' }
      );
    }

    if (perms?.canAccessAI) {
      actions.push(
        { id: 'ai', label: '🤖 Generate AI Content', type: 'secondary' }
      );
    }

    if (perms?.canViewAnalytics) {
      actions.push(
        { id: 'analytics', label: '📊 View Full Analytics', type: 'secondary' }
      );
    }

    if (perms?.canViewAuditLogs) {
      actions.push(
        { id: 'audit-logs', label: '📋 View Audit Logs', type: 'secondary' }
      );
    }

    if (perms?.canViewAuditHistory) {
      actions.push(
        { id: 'audit-history', label: '📜 View Audit History', type: 'secondary' }
      );
    }

    if (perms?.canManageCache) {
      actions.push(
        { id: 'cache-management', label: '💾 Manage Cache', type: 'secondary' }
      );
    }

    return actions;
  };

  // Define stat cards based on permissions
  const getStatCards = (perms: AdminPermissions | null) => {
    const cards = [];

    // User statistics - visible to all with user management or view activity permissions
    if (perms?.canManageUsers || perms?.canViewUserActivity) {
      cards.push(
        { icon: '👥', value: userStats.total_users || 0, label: 'Total Users', change: `+${userStats.new_users_this_week || 0} this week`, type: 'user' },
        { icon: '✅', value: userStats.active_users || 0, label: 'Active Users', change: `${userStats.inactive_users || 0} inactive`, type: 'active' }
      );

      if (perms?.canManageUsers) {
        cards.push({ icon: '👑', value: userStats.total_admins || 0, label: 'Administrators', change: 'Role distribution', type: 'admin' });
      }
    }

    // System status - visible to all
    cards.push({ icon: '🖥️', value: systemHealth.api_status || 'N/A', label: 'System Status', change: `Database: ${systemHealth.database_status || 'Unknown'}`, type: 'system' });

    return cards;
  };

  const quickActions = getQuickActions(permissions);
  const statCards = getStatCards(permissions);

  return (
    <div className="dashboard-overview">
      {/* Stats Grid */}
      <div className="stats-grid">
        {statCards.map((card, index) => (
          <div key={index} className="stat-card">
            <div className="stat-icon">{card.icon}</div>
            <div className="stat-value">{card.value}</div>
            <div className="stat-label">{card.label}</div>
            <div className="stat-change positive">
              {card.change}
            </div>
          </div>
        ))}
      </div>

      {/* Admin Role Distribution - Only visible to users who can manage other admins */}
      {permissions?.canManageUsers && Object.keys(adminStats.role_distribution || {}).length > 0 && (
        <div className="admin-card" style={{ marginBottom: '24px' }}>
          <div className="admin-card-header">
            <h2>Admin Role Distribution</h2>
          </div>
          <div className="admin-card-body">
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
          </div>
        </div>
      )}

      {/* Quick Actions - Shows only actions user has permission for */}
      {quickActions.length > 0 && (
        <div className="admin-card">
          <div className="admin-card-header">
            <h2>Quick Actions</h2>
          </div>
          <div className="admin-card-body">
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              {quickActions.map((action) => (
                <button
                  key={action.id}
                  className={action.type === 'primary' ? 'btn btn-primary' : 'btn btn-secondary'}
                  onClick={() => onNavigate(action.id)}
                >
                  {action.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Permission Notice for users with limited access */}
      {!permissions?.canManageUsers && !permissions?.canManageContent && !permissions?.canManageQuizzes && (
        <div className="admin-card" style={{ marginTop: '24px' }}>
          <div className="admin-card-header">
            <h2>Your Access Level</h2>
          </div>
          <div className="admin-card-body">
            <p style={{ color: '#6b7280' }}>
              You have read-only access to this admin panel. Contact a super administrator if you need additional permissions.
            </p>
            {permissions?.canViewAnalytics && (
              <div style={{ marginTop: '16px' }}>
                <button className="btn btn-secondary" onClick={() => onNavigate('analytics')}>
                  📊 View Analytics
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardOverview;
