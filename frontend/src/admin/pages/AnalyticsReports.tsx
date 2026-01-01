/**
 * Analytics Reports Page - Admin analytics dashboard
 */

import React, { useState, useEffect } from 'react';
import adminApi from '../../services/adminApi';
import '../Admin.css';

interface AnalyticsReportsProps {
  activeSection: string;
}

const AnalyticsReports: React.FC<AnalyticsReportsProps> = ({ activeSection }) => {
  const [userAnalytics, setUserAnalytics] = useState<any>(null);
  const [learningAnalytics, setLearningAnalytics] = useState<any>(null);
  const [contentAnalytics, setContentAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (activeSection === 'analytics') {
      loadAnalytics();
    }
  }, [activeSection]);

  const loadAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const [userRes, learningRes, contentRes] = await Promise.all([
        adminApi.getUserAnalytics().catch(() => ({ success: false } as const)),
        adminApi.getLearningAnalytics().catch(() => ({ success: false } as const)),
        adminApi.getContentAnalytics().catch(() => ({ success: false } as const)),
      ]);

      if (userRes.success && 'analytics' in userRes) setUserAnalytics(userRes.analytics);
      if (learningRes.success && 'analytics' in learningRes) setLearningAnalytics(learningRes.analytics);
      if (contentRes.success && 'analytics' in contentRes) setContentAnalytics(contentRes.analytics);
    } catch (err: any) {
      setError(err.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await adminApi.refreshAnalytics();
      await loadAnalytics();
      alert('Analytics refreshed successfully!');
    } catch (err: any) {
      alert('Failed to refresh: ' + err.message);
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="spinner"></div>
        <span>Loading analytics...</span>
      </div>
    );
  }

  return (
    <div className="analytics-reports">
      {/* Actions */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2 style={{ margin: 0 }}>Platform Analytics</h2>
        <button 
          className="btn btn-primary" 
          onClick={handleRefresh}
          disabled={refreshing}
        >
          {refreshing ? '🔄 Refreshing...' : '🔄 Refresh Analytics'}
        </button>
      </div>

      {/* Overview Stats */}
      <div className="stats-grid" style={{ marginBottom: '24px' }}>
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-value">{userAnalytics?.total_users || 0}</div>
          <div className="stat-label">Total Users</div>
          <div className="stat-change positive">
            {userAnalytics?.active_users || 0} active
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📚</div>
          <div className="stat-value">{contentAnalytics?.total_courses || 0}</div>
          <div className="stat-label">Total Courses</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-value">{learningAnalytics?.completed_courses || 0}</div>
          <div className="stat-label">Completed Courses</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-value">{learningAnalytics?.average_progress?.toFixed(1) || 0}%</div>
          <div className="stat-label">Avg Progress</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* User Growth */}
        <div className="admin-card">
          <div className="admin-card-header">
            <h2>User Growth</h2>
          </div>
          <div className="admin-card-body">
            {userAnalytics?.user_growth && userAnalytics.user_growth.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {userAnalytics.user_growth.slice(-10).map((item: any, index: number) => (
                  <div key={index} style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    padding: '12px',
                    background: '#f9fafb',
                    borderRadius: '8px',
                  }}>
                    <span style={{ color: '#6b7280' }}>
                      {new Date(item.date).toLocaleDateString()}
                    </span>
                    <span style={{ fontWeight: '600', color: '#2563eb' }}>
                      +{item.count} new users
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <p>No user growth data available</p>
              </div>
            )}
          </div>
        </div>

        {/* Learning Trends */}
        <div className="admin-card">
          <div className="admin-card-header">
            <h2>Learning Trends</h2>
          </div>
          <div className="admin-card-body">
            {learningAnalytics?.learning_trends && learningAnalytics.learning_trends.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {learningAnalytics.learning_trends.slice(-10).map((item: any, index: number) => (
                  <div key={index} style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    padding: '12px',
                    background: '#f9fafb',
                    borderRadius: '8px',
                  }}>
                    <span style={{ color: '#6b7280' }}>
                      {new Date(item.date).toLocaleDateString()}
                    </span>
                    <span style={{ fontWeight: '600', color: '#10b981' }}>
                      {item.sessions} sessions
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <p>No learning trend data available</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Content Analytics */}
      <div className="admin-card" style={{ marginTop: '24px' }}>
        <div className="admin-card-header">
          <h2>Content Analytics</h2>
        </div>
        <div className="admin-card-body">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
            <div>
              <h3 style={{ marginBottom: '16px' }}>Content by Difficulty</h3>
              {contentAnalytics?.content_by_difficulty ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {Object.entries(contentAnalytics.content_by_difficulty).map(([difficulty, count]) => (
                    <div key={difficulty} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span className={`badge ${
                        difficulty === 'beginner' ? 'badge-success' :
                        difficulty === 'intermediate' ? 'badge-warning' : 'badge-danger'
                      }`} style={{ minWidth: '100px' }}>
                        {difficulty}
                      </span>
                      <div style={{ flex: 1, height: '24px', background: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                        <div style={{ 
                          width: `${Math.min((count as number) / Math.max(...Object.values(contentAnalytics.content_by_difficulty) as number[]) * 100, 100)}%`,
                          height: '100%',
                          background: '#2563eb',
                          borderRadius: '4px',
                        }} />
                      </div>
                      <span style={{ fontWeight: '500', minWidth: '40px' }}>{count as number}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ color: '#6b7280' }}>No difficulty data available</p>
              )}
            </div>

            <div>
              <h3 style={{ marginBottom: '16px' }}>Popular Content</h3>
              {contentAnalytics?.popular_content && contentAnalytics.popular_content.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {contentAnalytics.popular_content.slice(0, 5).map((item: any, index: number) => (
                    <div key={index} style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      padding: '8px 12px',
                      background: '#f9fafb',
                      borderRadius: '6px',
                    }}>
                      <span style={{ flex: 1, fontSize: '14px' }}>{item.title}</span>
                      <span style={{ fontWeight: '600', color: '#2563eb' }}>{item.views} views</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ color: '#6b7280' }}>No popular content data</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="admin-card" style={{ marginTop: '24px' }}>
        <div className="admin-card-header">
          <h2>Summary Statistics</h2>
        </div>
        <div className="admin-card-body">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '24px' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '32px', fontWeight: '700', color: '#1f2937' }}>
                {learningAnalytics?.total_sessions || 0}
              </div>
              <div style={{ fontSize: '14px', color: '#6b7280' }}>Total Learning Sessions</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '32px', fontWeight: '700', color: '#1f2937' }}>
                {contentAnalytics?.total_concepts || 0}
              </div>
              <div style={{ fontSize: '14px', color: '#6b7280' }}>Total Concepts</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '32px', fontWeight: '700', color: '#1f2937' }}>
                {userAnalytics?.new_users?.reduce((a: number, b: number) => a + b, 0) || 0}
              </div>
              <div style={{ fontSize: '14px', color: '#6b7280' }}>New Users (Period)</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '32px', fontWeight: '700', color: '#1f2937' }}>
                {learningAnalytics?.average_progress?.toFixed(0) || 0}%
              </div>
              <div style={{ fontSize: '14px', color: '#6b7280' }}>Average Progress</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsReports;
