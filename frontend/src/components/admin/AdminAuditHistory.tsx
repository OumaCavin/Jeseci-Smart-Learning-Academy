/**
 * Admin Audit History Component
 * 
 * Displays audit trail with historical changes and trends analysis
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  History,
  TrendingUp,
  TrendingDown,
  Calendar,
  User,
  Clock,
  Activity,
  BarChart3,
  PieChart,
  Filter,
  RefreshCw,
  ChevronRight,
  FileText,
  ArrowRight,
  Target,
  AlertCircle
} from 'lucide-react';
import advancedCollaborationService from '../../services/advancedCollaborationService';

interface AuditHistoryEntry {
  id: string;
  timestamp: string;
  userId: string;
  username: string;
  action: string;
  previousValue?: string;
  newValue?: string;
  resourceType: string;
  resourceId: string;
  changeSummary: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

interface AuditHistoryStats {
  totalChanges: number;
  changesToday: number;
  changesThisWeek: number;
  criticalChanges: number;
  topActionsByDay: Array<{ date: string; count: number }>;
  topUsers: Array<{ username: string; changesCount: number }>;
  changesByType: Array<{ type: string; count: number }>;
  trend: 'up' | 'down' | 'stable';
  trendPercentage: number;
}

export const AdminAuditHistory: React.FC = () => {
  const [stats, setStats] = useState<AuditHistoryStats | null>(null);
  const [history, setHistory] = useState<AuditHistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState<'day' | 'week' | 'month'>('week');
  const [filterType, setFilterType] = useState<string>('all');
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [expandedEntry, setExpandedEntry] = useState<string | null>(null);

  const loadAuditHistory = useCallback(async () => {
    try {
      setLoading(true);
      const [statsData, historyData] = await Promise.all([
        advancedCollaborationService.getAuditHistoryStats(),
        advancedCollaborationService.getAuditHistory({
          period: selectedPeriod,
          type: filterType !== 'all' ? filterType : undefined,
          severity: filterSeverity !== 'all' ? filterSeverity : undefined,
          limit: 100
        })
      ]);
      setStats(statsData.data);
      setHistory(historyData.data || []);
    } catch (error) {
      console.error('Error loading audit history:', error);
    } finally {
      setLoading(false);
    }
  }, [selectedPeriod, filterType, filterSeverity]);

  useEffect(() => {
    loadAuditHistory();
  }, [loadAuditHistory]);

  const filteredHistory = history;

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getActionIcon = (action: string) => {
    if (action.includes('create')) return <FileText className="w-4 h-4 text-green-500" />;
    if (action.includes('delete')) return <AlertCircle className="w-4 h-4 text-red-500" />;
    if (action.includes('update')) return <RefreshCw className="w-4 h-4 text-blue-500" />;
    return <Activity className="w-4 h-4 text-gray-500" />;
  };

  if (loading && !stats) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
        <div className="animate-pulse flex items-center justify-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
          <span className="ml-3 text-gray-600">Loading audit history...</span>
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
            <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center">
              <History className="w-6 h-6 text-teal-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Audit History</h2>
              <p className="text-sm text-gray-500">Track historical changes and trends</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value as any)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="day">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
            </select>
            <button
              onClick={loadAuditHistory}
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
                <p className="text-sm text-gray-500">Total Changes</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalChanges.toLocaleString()}</p>
              </div>
              <History className="w-8 h-8 text-blue-300" />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">This Period</p>
                <p className="text-2xl font-bold text-green-600">{stats.changesThisWeek.toLocaleString()}</p>
              </div>
              <Calendar className="w-8 h-8 text-green-300" />
            </div>
            <div className={`flex items-center gap-1 mt-2 text-sm ${stats.trend === 'up' ? 'text-green-600' : stats.trend === 'down' ? 'text-red-600' : 'text-gray-600'}`}>
              {stats.trend === 'up' ? <TrendingUp className="w-4 h-4" /> : stats.trend === 'down' ? <TrendingDown className="w-4 h-4" /> : null}
              <span>{stats.trendPercentage}% vs last period</span>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Critical Changes</p>
                <p className="text-2xl font-bold text-red-600">{stats.criticalChanges.toLocaleString()}</p>
              </div>
              <AlertCircle className="w-8 h-8 text-red-300" />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Active Users</p>
                <p className="text-2xl font-bold text-purple-600">{stats.topUsers.length}</p>
              </div>
              <User className="w-8 h-8 text-purple-300" />
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div className="flex flex-wrap gap-4 items-center">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Types</option>
            <option value="user">User Changes</option>
            <option value="content">Content Changes</option>
            <option value="setting">Setting Changes</option>
            <option value="permission">Permission Changes</option>
          </select>
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Severity</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {/* Changes by Type Chart */}
      {stats && stats.changesByType.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <PieChart className="w-5 h-5 text-blue-500" />
            Changes by Type
          </h3>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
            {stats.changesByType.map((item, index) => {
              const maxCount = Math.max(...stats.changesByType.map(i => i.count));
              const percentage = (item.count / maxCount) * 100;
              
              return (
                <div key={item.type} className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900 capitalize">{item.type}</span>
                    <span className="text-sm text-gray-500">{item.count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Top Users */}
      {stats && stats.topUsers.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <User className="w-5 h-5 text-purple-500" />
            Most Active Contributors
          </h3>
          <div className="space-y-3">
            {stats.topUsers.slice(0, 10).map((user, index) => (
              <div key={user.username} className="flex items-center gap-4">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  index === 0 ? 'bg-yellow-100 text-yellow-700' :
                  index === 1 ? 'bg-gray-200 text-gray-700' :
                  index === 2 ? 'bg-orange-100 text-orange-700' :
                  'bg-blue-100 text-blue-700'
                }`}>
                  {index + 1}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-900">{user.username}</span>
                    <span className="text-sm text-gray-500">{user.changesCount} changes</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-1 mt-1">
                    <div
                      className="bg-purple-500 h-1 rounded-full"
                      style={{ width: `${(user.changesCount / stats.topUsers[0].changesCount) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Daily Activity Chart */}
      {stats && stats.topActionsByDay.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-green-500" />
            Daily Activity
          </h3>
          <div className="flex items-end gap-2 h-32">
            {stats.topActionsByDay.map((day, index) => {
              const maxCount = Math.max(...stats.topActionsByDay.map(d => d.count));
              const height = (day.count / maxCount) * 100;
              
              return (
                <div key={index} className="flex-1 flex flex-col items-center">
                  <div
                    className="w-full bg-blue-500 rounded-t transition-all hover:bg-blue-600"
                    style={{ height: `${height}%`, minHeight: '4px' }}
                    title={`${day.date}: ${day.count} changes`}
                  />
                  <span className="text-xs text-gray-500 mt-1 truncate w-full text-center">
                    {new Date(day.date).toLocaleDateString('en', { weekday: 'short' })}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* History Timeline */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b border-gray-100">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2">
            <Activity className="w-5 h-5 text-teal-500" />
            Change Timeline
          </h3>
        </div>

        {filteredHistory.length === 0 ? (
          <div className="p-8 text-center">
            <History className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No changes recorded</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {filteredHistory.slice(0, 50).map((entry) => (
              <div key={entry.id}>
                <div
                  className="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => setExpandedEntry(expandedEntry === entry.id ? null : entry.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 mt-1">
                        {getActionIcon(entry.action)}
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-gray-900">{entry.username}</span>
                          <ArrowRight className="w-3 h-3 text-gray-400" />
                          <span className="text-gray-700">{entry.action}</span>
                          <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${getSeverityColor(entry.severity)}`}>
                            {entry.severity}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600">{entry.changeSummary}</p>
                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {new Date(entry.timestamp).toLocaleString()}
                          </span>
                          <span className="flex items-center gap-1">
                            <Target className="w-3 h-3" />
                            {entry.resourceType}: {entry.resourceId}
                          </span>
                        </div>
                      </div>
                    </div>
                    <ChevronRight className={`w-5 h-5 text-gray-400 transition-transform ${expandedEntry === entry.id ? 'rotate-90' : ''}`} />
                  </div>
                </div>

                {expandedEntry === entry.id && (
                  <div className="px-4 pb-4 ml-9">
                    <div className="bg-gray-50 rounded-lg p-4 space-y-4">
                      {entry.previousValue && (
                        <div>
                          <span className="text-xs font-medium text-gray-500 uppercase">Previous Value</span>
                          <pre className="mt-1 text-sm bg-white p-2 rounded border border-gray-200 overflow-x-auto">
                            {entry.previousValue}
                          </pre>
                        </div>
                      )}
                      {entry.newValue && (
                        <div>
                          <span className="text-xs font-medium text-gray-500 uppercase">New Value</span>
                          <pre className="mt-1 text-sm bg-white p-2 rounded border border-gray-200 overflow-x-auto">
                            {entry.newValue}
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminAuditHistory;
