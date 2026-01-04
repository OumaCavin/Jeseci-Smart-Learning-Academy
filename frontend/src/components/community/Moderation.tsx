import React, { useState, useEffect, useCallback } from 'react';
import {
  AlertTriangle,
  CheckCircle,
  XCircle,
  Flag,
  Clock,
  User,
  MessageSquare,
  FileText,
  Eye,
  Ban,
  AlertOctagon,
  ThumbsDown,
  MoreHorizontal,
  Filter,
  Search,
  SortAsc,
  SortDesc,
  RefreshCw,
  Shield,
  Activity,
  TrendingUp,
  Users,
  Info
} from 'lucide-react';
import advancedCollaborationService, {
  ModerationReport as ServiceModerationReport,
  ModerationAction as ServiceModerationAction,
  ModerationStats as ServiceModerationStats,
  ModerationQueueItem
} from '../../services/advancedCollaborationService';
import ModerationReports from './ModerationReports';
import ModerationActionsHistory from './ModerationActionsHistory';

// Type definitions (using service types)
interface ModerationReport extends ServiceModerationReport {}
interface ModerationAction extends ServiceModerationAction {}
interface ModerationStats extends ServiceModerationStats {}

interface ModerationQueue {
  totalPending: number;
  highPriorityCount: number;
  recentActions: number;
}

interface ReportedContent {
  type: string;
  id: number;
  content: string;
  author: {
    id: number;
    username: string;
    reputation: number;
  };
  reportedAt: string;
  reportCount: number;
}

const Moderation: React.FC = () => {
  // State management
  const [activeTab, setActiveTab] = useState<'queue' | 'reports' | 'actions_history' | 'stats'>('queue');
  const [reports, setReports] = useState<ModerationReport[]>([]);
  const [actions, setActions] = useState<ModerationAction[]>([]);
  const [stats, setStats] = useState<ModerationStats | null>(null);
  const [queue, setQueue] = useState<ModerationQueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedReport, setSelectedReport] = useState<ModerationReport | null>(null);
  const [actionType, setActionType] = useState<string>('warning');
  const [actionReason, setActionReason] = useState('');
  const [actionDuration, setActionDuration] = useState<string>('');
  const [showActionModal, setShowActionModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterPriority, setFilterPriority] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<string>('createdAt');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Fetch moderation data
  const fetchModerationData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [reportsData, actionsData, statsData, queueData] = await Promise.all([
        advancedCollaborationService.getModerationReports(),
        advancedCollaborationService.getModerationActions(),
        advancedCollaborationService.getModerationStats(),
        advancedCollaborationService.getModerationQueue()
      ]);

      setReports(reportsData.data || []);
      setActions(actionsData.data || []);
      setStats(statsData.data);
      setQueue(queueData.data || []);
    } catch (err) {
      setError('Failed to load moderation data');
      console.error('Error fetching moderation data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchModerationData();
  }, [fetchModerationData]);

  // Handle moderation action
  const handleTakeAction = async () => {
    if (!selectedReport || !actionReason.trim()) return;

    try {
      await advancedCollaborationService.takeModerationAction(
        selectedReport.id,
        {
          actionType,
          reason: actionReason,
          duration: actionDuration ? parseInt(actionDuration) : null
        }
      );

      setShowActionModal(false);
      setSelectedReport(null);
      setActionType('warning');
      setActionReason('');
      setActionDuration('');
      fetchModerationData();
    } catch (err) {
      setError('Failed to take moderation action');
      console.error('Error taking moderation action:', err);
    }
  };

  // Handle report dismissal
  const handleDismissReport = async (reportId: number) => {
    try {
      await advancedCollaborationService.dismissReport(reportId);
      fetchModerationData();
    } catch (err) {
      setError('Failed to dismiss report');
      console.error('Error dismissing report:', err);
    }
  };

  // Filter and sort reports
  const filteredReports = reports
    .filter(report => {
      if (filterStatus !== 'all' && report.status !== filterStatus) return false;
      if (filterPriority !== 'all' && report.priority !== filterPriority) return false;
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          report.contentAuthorUsername.toLowerCase().includes(query) ||
          report.reason.toLowerCase().includes(query) ||
          report.description.toLowerCase().includes(query)
        );
      }
      return true;
    })
    .sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case 'createdAt':
          comparison = new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
          break;
        case 'priority':
          const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
          comparison = priorityOrder[a.priority] - priorityOrder[b.priority];
          break;
        case 'status':
          comparison = a.status.localeCompare(b.status);
          break;
        default:
          comparison = 0;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

  // Get priority badge color
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // Get status badge color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-blue-100 text-blue-800';
      case 'reviewed': return 'bg-purple-100 text-purple-800';
      case 'resolved': return 'bg-green-100 text-green-800';
      case 'dismissed': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Get action type icon
  const getActionTypeIcon = (actionType: string) => {
    switch (actionType) {
      case 'ban': return <Ban className="w-4 h-4 text-red-500" />;
      case 'warning': return <AlertOctagon className="w-4 h-4 text-yellow-500" />;
      case 'delete': return <XCircle className="w-4 h-4 text-orange-500" />;
      case 'approve': return <CheckCircle className="w-4 h-4 text-green-500" />;
      default: return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };

  // Loading state
  if (loading && !reports.length) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading moderation data...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !reports.length) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchModerationData}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield className="w-8 h-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">Content Moderation</h1>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={fetchModerationData}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                title="Refresh data"
              >
                <RefreshCw className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Stats Overview */}
          {stats && (
            <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-blue-600 font-medium">Pending Reviews</p>
                    <p className="text-2xl font-bold text-blue-900">{stats.pending_reports}</p>
                  </div>
                  <Clock className="w-8 h-8 text-blue-300" />
                </div>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-green-600 font-medium">Resolved</p>
                    <p className="text-2xl font-bold text-green-900">{stats.resolved_reports}</p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-green-300" />
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 font-medium">Dismissed</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.dismissed_reports}</p>
                  </div>
                  <XCircle className="w-8 h-8 text-gray-300" />
                </div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-purple-600 font-medium">Avg Resolution</p>
                    <p className="text-2xl font-bold text-purple-900">{stats.avg_resolution_time}h</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-purple-300" />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Tabs */}
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg mb-6 w-fit">
          <button
            onClick={() => setActiveTab('queue')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'queue'
                ? 'bg-white text-gray-900 shadow'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center gap-2">
              <Flag className="w-4 h-4" />
              Review Queue
              {queue && queue.filter(q => q.status === 'pending').length > 0 && (
                <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                  {queue.filter(q => q.status === 'pending').length}
                </span>
              )}
            </div>
          </button>
          <button
            onClick={() => setActiveTab('reports')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'reports'
                ? 'bg-white text-gray-900 shadow'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              All Reports
            </div>
          </button>
          <button
            onClick={() => setActiveTab('actions_history')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'actions_history'
                ? 'bg-white text-gray-900 shadow'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Actions History
            </div>
          </button>
          <button
            onClick={() => setActiveTab('stats')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'stats'
                ? 'bg-white text-gray-900 shadow'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Statistics
            </div>
          </button>
        </div>

        {/* Queue Tab */}
        {activeTab === 'queue' && (
          <div className="space-y-4">
            {/* Filters */}
            <div className="bg-white rounded-lg shadow p-4 flex flex-wrap gap-4 items-center">
              <div className="flex-1 min-w-[200px]">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search by username or reason..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
              <select
                value={filterPriority}
                onChange={(e) => setFilterPriority(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Priorities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="createdAt">Sort by Date</option>
                <option value="priority">Sort by Priority</option>
                <option value="status">Sort by Status</option>
              </select>
              <button
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                {sortOrder === 'asc' ? <SortAsc className="w-5 h-5" /> : <SortDesc className="w-5 h-5" />}
              </button>
            </div>

            {/* Reports List */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
              {filteredReports.length === 0 ? (
                <div className="p-8 text-center">
                  <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
                  <p className="text-gray-600">No reports matching your criteria</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {filteredReports.map((report) => (
                    <div
                      key={report.id}
                      className="p-4 hover:bg-gray-50 transition-colors cursor-pointer"
                      onClick={() => setSelectedReport(report)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getPriorityColor(report.priority)}`}>
                              {report.priority.toUpperCase()}
                            </span>
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(report.status)}`}>
                              {report.status}
                            </span>
                            <span className="text-sm text-gray-500">
                              {new Date(report.createdAt).toLocaleDateString()}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 mb-2">
                            <Flag className="w-4 h-4 text-red-500" />
                            <span className="font-medium text-gray-900">
                              Reported: {report.contentAuthorUsername}
                            </span>
                            <span className="text-gray-500">for</span>
                            <span className="text-gray-700">{report.reason}</span>
                          </div>
                          {report.description && (
                            <p className="text-gray-600 text-sm mt-1">{report.description}</p>
                          )}
                          <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                            <span className="flex items-center gap-1">
                              <User className="w-4 h-4" />
                              Reporter: {report.reporterUsername}
                            </span>
                            <span className="flex items-center gap-1">
                              <FileText className="w-4 h-4" />
                              {report.contentType}
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 ml-4">
                          {report.status === 'pending' && (
                            <>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setSelectedReport(report);
                                  setShowActionModal(true);
                                }}
                                className="px-3 py-1 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600 transition-colors"
                              >
                                Review
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDismissReport(report.id);
                                }}
                                className="px-3 py-1 bg-gray-200 text-gray-700 text-sm rounded-lg hover:bg-gray-300 transition-colors"
                              >
                                Dismiss
                              </button>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Reports Tab */}
        {activeTab === 'reports' && (
          <ModerationReports />
        )}

        {/* Actions History Tab */}
        {activeTab === 'actions_history' && (
          <ModerationActionsHistory />
        )}

        {/* Stats Tab */}
        {activeTab === 'stats' && stats && (
          <div className="space-y-6">
            {/* Top Reasons */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Top Report Reasons</h3>
              <div className="space-y-3">
                {(stats.top_reasons || []).map((item, index) => (
                  <div key={index} className="flex items-center gap-4">
                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-sm font-medium text-blue-600">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-gray-700">{item.reason}</span>
                        <span className="text-sm text-gray-500">{item.count} reports</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full transition-all"
                          style={{
                            width: `${(item.count / (stats as any).total_reports) * 100}%`
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Resolution Metrics */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Resolution Metrics</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <p className="text-3xl font-bold text-blue-600">{(stats as any).total_reports || 0}</p>
                  <p className="text-sm text-gray-600 mt-1">Total Reports</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-green-600">
                    {(stats as any).total_reports > 0
                      ? Math.round(((stats as any).resolved_reports || 0) / (stats as any).total_reports * 100)
                      : 0}%
                  </p>
                  <p className="text-sm text-gray-600 mt-1">Resolution Rate</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-purple-600">{(stats as any).avg_resolution_time || 0}h</p>
                  <p className="text-sm text-gray-600 mt-1">Avg Resolution Time</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Action Modal */}
      {showActionModal && selectedReport && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Take Moderation Action</h3>
                <button
                  onClick={() => setShowActionModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="w-6 h-6" />
                </button>
              </div>

              {/* Report Summary */}
              <div className="bg-gray-50 rounded-lg p-4 mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getPriorityColor(selectedReport.priority)}`}>
                    {selectedReport.priority}
                  </span>
                  <span className="text-sm text-gray-500">
                    Reported {new Date(selectedReport.createdAt).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-gray-900 font-medium">{selectedReport.reason}</p>
                {selectedReport.description && (
                  <p className="text-gray-600 text-sm mt-1">{selectedReport.description}</p>
                )}
              </div>

              {/* Action Type Selection */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Action Type
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { value: 'warning', label: 'AlertOctagon', icon: AlertOctagon, color: 'yellow' },
                    { value: 'delete', label: 'Delete Content', icon: XCircle, color: 'orange' },
                    { value: 'ban', label: 'Ban User', icon: Ban, color: 'red' },
                    { value: 'approve', label: 'Approve Content', icon: CheckCircle, color: 'green' }
                  ].map((action) => (
                    <button
                      key={action.value}
                      onClick={() => setActionType(action.value)}
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg border-2 transition-colors ${
                        actionType === action.value
                          ? `border-${action.color}-500 bg-${action.color}-50`
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <action.icon className={`w-4 h-4 text-${action.color}-500`} />
                      <span className="text-sm font-medium">{action.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Duration (for ban) */}
              {actionType === 'ban' && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Ban Duration (days)
                  </label>
                  <input
                    type="number"
                    value={actionDuration}
                    onChange={(e) => setActionDuration(e.target.value)}
                    placeholder="Leave empty for permanent ban"
                    min="1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              )}

              {/* Reason */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Action Reason
                </label>
                <textarea
                  value={actionReason}
                  onChange={(e) => setActionReason(e.target.value)}
                  placeholder="Explain the reason for this action..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => setShowActionModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleTakeAction}
                  disabled={!actionReason.trim()}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Take Action
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Moderation;
