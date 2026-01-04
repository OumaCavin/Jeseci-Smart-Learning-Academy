import React, { useState, useEffect, useCallback } from 'react';
import {
  AlertTriangle,
  X,
  CheckCircle,
  Clock,
  AlertCircle,
  Loader,
  ChevronRight,
  Filter,
  Search,
  User,
  Calendar,
  Flag,
  Eye,
  MoreVertical
} from 'lucide-react';
import advancedCollaborationService, {
  ModerationReport
} from '../../services/advancedCollaborationService';

interface ModerationReportsProps {
  onClose?: () => void;
}

const ModerationReports: React.FC<ModerationReportsProps> = ({ onClose }) => {
  const [reports, setReports] = useState<ModerationReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('pending');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedReport, setSelectedReport] = useState<ModerationReport | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchReports = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await advancedCollaborationService.getModerationReports();

      if (response.success && response.data) {
        setReports(response.data as ModerationReport[]);
      } else {
        setError(response.error || 'Failed to load reports');
      }
    } catch (err) {
      setError('An error occurred while loading reports');
      console.error('Error fetching moderation reports:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  const handleDismiss = async (reportId: number) => {
    try {
      setActionLoading(true);
      setError(null);

      const response = await advancedCollaborationService.dismissReport(reportId);

      if (response.success) {
        setSuccessMessage('Report dismissed successfully');
        fetchReports();
        setShowDetailModal(false);
      } else {
        setError(response.error || 'Failed to dismiss report');
      }
    } catch (err) {
      setError('An error occurred while dismissing report');
      console.error('Error dismissing report:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-700',
      reviewed: 'bg-blue-100 text-blue-700',
      resolved: 'bg-green-100 text-green-700',
      dismissed: 'bg-gray-100 text-gray-600'
    };

    const icons: Record<string, React.ReactNode> = {
      pending: <Clock size={12} />,
      reviewed: <Eye size={12} />,
      resolved: <CheckCircle size={12} />,
      dismissed: <X size={12} />
    };

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${styles[status] || 'bg-gray-100 text-gray-700'}`}>
        {icons[status]}
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const getPriorityBadge = (priority: string) => {
    const styles: Record<string, string> = {
      low: 'bg-gray-100 text-gray-600',
      medium: 'bg-yellow-100 text-yellow-700',
      high: 'bg-orange-100 text-orange-700',
      critical: 'bg-red-100 text-red-700'
    };

    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${styles[priority] || 'bg-gray-100 text-gray-700'}`}>
        {priority.charAt(0).toUpperCase() + priority.slice(1)}
      </span>
    );
  };

  const filteredReports = reports.filter(report => {
    const matchesStatus = filterStatus === 'all' || report.status === filterStatus;

    const matchesSearch = !searchQuery ||
      report.reporterUsername?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      report.contentAuthorUsername?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      report.reason?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      report.description?.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesStatus && matchesSearch;
  });

  const statusCounts = {
    pending: reports.filter(r => r.status === 'pending').length,
    reviewed: reports.filter(r => r.status === 'reviewed').length,
    resolved: reports.filter(r => r.status === 'resolved').length,
    dismissed: reports.filter(r => r.status === 'dismissed').length
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader size={40} className="animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg max-w-4xl w-full max-h-[80vh] overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Flag className="text-blue-500" size={24} />
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Moderation Reports</h2>
            <p className="text-sm text-gray-500">Review and manage content reports</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X size={20} className="text-gray-500" />
        </button>
      </div>

      {/* Success/Error Messages */}
      {successMessage && (
        <div className="mx-6 mt-4 p-3 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2">
          <CheckCircle size={18} className="text-green-500" />
          <span className="text-green-700 text-sm">{successMessage}</span>
          <button
            onClick={() => setSuccessMessage(null)}
            className="ml-auto text-green-500 hover:text-green-700"
          >
            <X size={14} />
          </button>
        </div>
      )}

      {error && (
        <div className="mx-6 mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
          <AlertCircle size={18} className="text-red-500" />
          <span className="text-red-700 text-sm">{error}</span>
          <button
            onClick={() => setError(null)}
            className="ml-auto text-red-500 hover:text-red-700"
          >
            <X size={14} />
          </button>
        </div>
      )}

      {/* Filters */}
      <div className="px-6 py-4 border-b border-gray-100">
        <div className="flex flex-wrap gap-3">
          <div className="flex-1 min-w-[200px] relative">
            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search reports..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter size={18} className="text-gray-400" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="pending">Pending ({statusCounts.pending})</option>
              <option value="reviewed">Reviewed ({statusCounts.reviewed})</option>
              <option value="resolved">Resolved ({statusCounts.resolved})</option>
              <option value="dismissed">Dismissed ({statusCounts.dismissed})</option>
              <option value="all">All ({reports.length})</option>
            </select>
          </div>
        </div>
      </div>

      {/* Reports List */}
      <div className="overflow-y-auto max-h-[400px] p-4">
        {filteredReports.length === 0 ? (
          <div className="text-center py-8">
            <Flag size={48} className="mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500">No reports found</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredReports.map((report) => (
              <div
                key={report.id}
                className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all cursor-pointer"
                onClick={() => {
                  setSelectedReport(report);
                  setShowDetailModal(true);
                }}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-gray-900">
                        {report.reason}
                      </span>
                      {getPriorityBadge(report.priority)}
                      {getStatusBadge(report.status)}
                    </div>
                    <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                      {report.description}
                    </p>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <User size={14} />
                        Reported by {report.reporterUsername}
                      </span>
                      <span className="flex items-center gap-1">
                        <AlertTriangle size={14} />
                        Content by {report.contentAuthorUsername}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar size={14} />
                        {new Date(report.createdAt).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <ChevronRight size={20} className="text-gray-400" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Report Detail Modal */}
      {showDetailModal && selectedReport && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
                    <Flag className="text-yellow-500" size={20} />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{selectedReport.reason}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      {getPriorityBadge(selectedReport.priority)}
                      {getStatusBadge(selectedReport.status)}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X size={20} className="text-gray-500" />
                </button>
              </div>

              <div className="space-y-4">
                <div className="py-2 border-b border-gray-100">
                  <span className="text-gray-500 block mb-1">Description</span>
                  <p className="text-gray-900">{selectedReport.description}</p>
                </div>

                <div className="grid grid-cols-2 gap-4 py-2 border-b border-gray-100">
                  <div>
                    <span className="text-gray-500 block mb-1">Reported By</span>
                    <span className="text-gray-900">{selectedReport.reporterUsername}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block mb-1">Content Type</span>
                    <span className="text-gray-900">{selectedReport.contentType}</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 py-2 border-b border-gray-100">
                  <div>
                    <span className="text-gray-500 block mb-1">Content Author</span>
                    <span className="text-gray-900">{selectedReport.contentAuthorUsername}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block mb-1">Content ID</span>
                    <span className="text-gray-900">{selectedReport.contentId}</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 py-2 border-b border-gray-100">
                  <div>
                    <span className="text-gray-500 block mb-1">Created</span>
                    <span className="text-gray-900">
                      {new Date(selectedReport.createdAt).toLocaleString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500 block mb-1">Updated</span>
                    <span className="text-gray-900">
                      {new Date(selectedReport.updatedAt).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>

              {selectedReport.status === 'pending' && (
                <div className="mt-6 pt-4 border-t border-gray-200 space-y-2">
                  <button
                    onClick={() => handleDismiss(selectedReport.id)}
                    disabled={actionLoading}
                    className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Dismiss Report
                  </button>
                  <button
                    onClick={() => {
                      // Take action on content
                    }}
                    className="w-full px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                  >
                    Take Action on Content
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModerationReports;
