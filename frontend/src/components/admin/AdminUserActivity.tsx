/**
 * Admin User Activity Component
 * 
 * Displays user activity analytics and metrics for administrators
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Users,
  Activity,
  TrendingUp,
  TrendingDown,
  Clock,
  Eye,
  MessageSquare,
  FileText,
  Award,
  Search,
  Filter,
  Calendar,
  RefreshCw,
  BarChart3,
  PieChart,
  UserCheck,
  UserX,
  Download
} from 'lucide-react';
import advancedCollaborationService from '../../services/advancedCollaborationService';
import adminApi from '../../services/adminApi';

interface UserActivityStats {
  totalUsers: number;
  activeUsers: number;
  newUsersToday: number;
  newUsersThisWeek: number;
  avgSessionDuration: number;
  topActiveUsers: Array<{
    userId: string;
    username: string;
    actionsCount: number;
    lastActive: string;
  }>;
  usersByRole: Array<{
    role: string;
    count: number;
  }>;
  activityByHour: Array<{
    hour: number;
    count: number;
  }>;
}

interface UserActivityLog {
  userId: string;
  username: string;
  action: string;
  details: string;
  timestamp: string;
  ipAddress: string;
}

export const AdminUserActivity: React.FC = () => {
  const [stats, setStats] = useState<UserActivityStats | null>(null);
  const [activityLog, setActivityLog] = useState<UserActivityLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterAction, setFilterAction] = useState<string>('all');
  const [dateRange, setDateRange] = useState<'today' | 'week' | 'month'>('week');

  const loadUserActivity = useCallback(async () => {
    try {
      setLoading(true);
      const [statsData, logData] = await Promise.all([
        advancedCollaborationService.getUserActivityStats(),
        advancedCollaborationService.getUserActivityLog({ limit: 100, dateRange })
      ]);
      setStats(statsData.data);
      setActivityLog(logData.data || []);
    } catch (error) {
      console.error('Error loading user activity:', error);
    } finally {
      setLoading(false);
    }
  }, [dateRange]);

  const handleExport = async (format: 'csv' | 'json') => {
    try {
      let response;
      if (format === 'csv') {
        response = await adminApi.exportUserActivityCsv();
      } else {
        response = await adminApi.exportUserActivityJson();
      }

      if (response.success) {
        const blob = new Blob([response.data], {
          type: format === 'csv' ? 'text/csv' : 'application/json'
        });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `user_activity_export_${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        alert('Export downloaded successfully!');
      } else {
        alert('Failed to export: ' + response.error);
      }
    } catch (err: any) {
      alert('Error: ' + err.message);
    }
  };

  useEffect(() => {
    loadUserActivity();
  }, [loadUserActivity]);

  const filteredActivity = activityLog.filter(log => {
    if (filterAction !== 'all' && log.action !== filterAction) return false;
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return log.username.toLowerCase().includes(query) || 
             log.action.toLowerCase().includes(query) ||
             log.details.toLowerCase().includes(query);
    }
    return true;
  });

  if (loading && !stats) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
        <div className="animate-pulse flex items-center justify-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
          <span className="ml-3 text-gray-600">Loading user activity...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">User Activity</h2>
              <p className="text-sm text-gray-500">Monitor user engagement and activity metrics</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value as any)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
            </select>
            <button
              className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 flex items-center gap-2"
              onClick={() => handleExport('csv')}
              title="Export to CSV"
            >
              <Download className="w-4 h-4" />
              CSV
            </button>
            <button
              className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 flex items-center gap-2"
              onClick={() => handleExport('json')}
              title="Export to JSON"
            >
              <Download className="w-4 h-4" />
              JSON
            </button>
            <button
              onClick={loadUserActivity}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Users</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalUsers.toLocaleString()}</p>
              </div>
              <Users className="w-8 h-8 text-blue-300" />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Active Users</p>
                <p className="text-2xl font-bold text-green-600">{stats.activeUsers.toLocaleString()}</p>
              </div>
              <Activity className="w-8 h-8 text-green-300" />
            </div>
            <div className="flex items-center gap-1 mt-2 text-sm text-green-600">
              <TrendingUp className="w-4 h-4" />
              <span>{((stats.activeUsers / stats.totalUsers) * 100).toFixed(1)}% engagement</span>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">New This Week</p>
                <p className="text-2xl font-bold text-purple-600">{stats.newUsersThisWeek.toLocaleString()}</p>
              </div>
              <UserCheck className="w-8 h-8 text-purple-300" />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Avg Session</p>
                <p className="text-2xl font-bold text-gray-900">{Math.round(stats.avgSessionDuration / 60)}min</p>
              </div>
              <Clock className="w-8 h-8 text-gray-300" />
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search users or actions..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <select
            value={filterAction}
            onChange={(e) => setFilterAction(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Actions</option>
            <option value="login">Login</option>
            <option value="logout">Logout</option>
            <option value="create">Create Content</option>
            <option value="edit">Edit Content</option>
            <option value="delete">Delete Content</option>
            <option value="comment">Comment</option>
          </select>
        </div>
      </div>

      {/* Activity Log */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b border-gray-100">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-500" />
            Recent Activity
          </h3>
        </div>
        {filteredActivity.length === 0 ? (
          <div className="p-8 text-center">
            <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No activity found</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {filteredActivity.slice(0, 50).map((log, index) => (
              <div key={index} className="p-4 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                      <Users className="w-5 h-5 text-gray-500" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">
                        <span className="text-blue-600">{log.username}</span>
                        <span className="text-gray-500"> performed </span>
                        <span className="font-medium">{log.action}</span>
                      </p>
                      <p className="text-sm text-gray-600 mt-1">{log.details}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {new Date(log.timestamp).toLocaleString()}
                        </span>
                        <span className="flex items-center gap-1">
                          <Activity className="w-3 h-3" />
                          {log.ipAddress}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Top Active Users */}
      {stats && stats.topActiveUsers.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Award className="w-5 h-5 text-yellow-500" />
            Top Active Users
          </h3>
          <div className="space-y-3">
            {stats.topActiveUsers.slice(0, 10).map((user, index) => (
              <div key={user.userId} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  index === 0 ? 'bg-yellow-100 text-yellow-700' :
                  index === 1 ? 'bg-gray-200 text-gray-700' :
                  index === 2 ? 'bg-orange-100 text-orange-700' :
                  'bg-blue-100 text-blue-700'
                }`}>
                  {index + 1}
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{user.username}</p>
                  <p className="text-sm text-gray-500">Last active: {new Date(user.lastActive).toLocaleString()}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900">{user.actionsCount}</p>
                  <p className="text-xs text-gray-500">actions</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminUserActivity;
