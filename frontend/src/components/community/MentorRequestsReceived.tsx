import React, { useState, useEffect, useCallback } from 'react';
import {
  Users,
  User,
  X,
  CheckCircle,
  Clock,
  AlertCircle,
  Loader,
  MessageSquare,
  ChevronDown,
  Filter,
  Search,
  Calendar,
  TrendingUp,
  Check,
  XCircle
} from 'lucide-react';
import advancedCollaborationService, {
  MentorshipRequest
} from '../../services/advancedCollaborationService';

interface MentorRequestsReceivedProps {
  onClose?: () => void;
}

const MentorRequestsReceived: React.FC<MentorRequestsReceivedProps> = ({ onClose }) => {
  const [requests, setRequests] = useState<MentorshipRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('pending');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRequest, setSelectedRequest] = useState<MentorshipRequest | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showRespondModal, setShowRespondModal] = useState(false);
  const [responseMessage, setResponseMessage] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  const fetchRequests = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await advancedCollaborationService.getMentorshipRequests();

      if (response.success && response.data) {
        setRequests(response.data as MentorshipRequest[]);
      } else {
        setError(response.error || 'Failed to load requests');
      }
    } catch (err) {
      setError('An error occurred while loading requests');
      console.error('Error fetching mentorship requests:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRequests();
  }, [fetchRequests]);

  const handleRespond = async (requestId: string, status: 'accepted' | 'rejected') => {
    try {
      setActionLoading(true);
      setError(null);

      const response = await advancedCollaborationService.respondToMentorshipRequest(
        requestId,
        status,
        responseMessage
      );

      if (response.success) {
        setSuccessMessage(`Request ${status} successfully`);
        setShowRespondModal(false);
        setResponseMessage('');
        fetchRequests();
      } else {
        setError(response.error || 'Failed to respond to request');
      }
    } catch (err) {
      setError('An error occurred while responding to request');
      console.error('Error responding to request:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-700',
      accepted: 'bg-green-100 text-green-700',
      rejected: 'bg-red-100 text-red-700',
      completed: 'bg-blue-100 text-blue-700',
      cancelled: 'bg-gray-100 text-gray-600'
    };

    const icons: Record<string, React.ReactNode> = {
      pending: <Clock size={12} />,
      accepted: <CheckCircle size={12} />,
      rejected: <X size={12} />,
      completed: <CheckCircle size={12} />,
      cancelled: <X size={12} />
    };

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${styles[status] || 'bg-gray-100 text-gray-700'}`}>
        {icons[status]}
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const filteredRequests = requests.filter(request => {
    const matchesStatus = filterStatus === 'all' || request.status === filterStatus;

    const matchesSearch = !searchQuery ||
      request.mentee_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      request.mentee_username?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      request.topic?.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesStatus && matchesSearch;
  });

  const statusCounts = {
    pending: requests.filter(r => r.status === 'pending').length,
    accepted: requests.filter(r => r.status === 'accepted').length,
    rejected: requests.filter(r => r.status === 'rejected').length,
    completed: requests.filter(r => r.status === 'completed').length,
    cancelled: requests.filter(r => r.status === 'cancelled').length
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader size={40} className="animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg max-w-3xl w-full max-h-[80vh] overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Users className="text-blue-500" size={24} />
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Requests Received</h2>
            <p className="text-sm text-gray-500">Review and respond to mentorship requests</p>
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
              placeholder="Search by mentee name..."
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
              <option value="accepted">Accepted ({statusCounts.accepted})</option>
              <option value="rejected">Rejected ({statusCounts.rejected})</option>
              <option value="all">All ({requests.length})</option>
            </select>
          </div>
        </div>
      </div>

      {/* Requests List */}
      <div className="overflow-y-auto max-h-[400px] p-4">
        {filteredRequests.length === 0 ? (
          <div className="text-center py-8">
            <Users size={48} className="mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500">No mentorship requests found</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredRequests.map((request) => (
              <div
                key={request.request_id}
                className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                      <User className="text-green-500" size={20} />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">
                        {request.mentee_name || request.mentee_username || 'Unknown Mentee'}
                      </h4>
                      <p className="text-sm text-gray-500">{request.topic}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(request.status)}
                  </div>
                </div>

                {request.message && (
                  <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                    "{request.message}"
                  </p>
                )}

                <div className="mt-3 flex items-center justify-between">
                  <span className="text-sm text-gray-500 flex items-center gap-1">
                    <Calendar size={14} />
                    {new Date(request.requested_at).toLocaleDateString()}
                  </span>

                  {request.status === 'pending' && (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => {
                          setSelectedRequest(request);
                          setShowRespondModal(true);
                        }}
                        className="flex items-center gap-1 px-3 py-1 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm"
                      >
                        <Check size={14} />
                        Review
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Respond Modal */}
      {showRespondModal && selectedRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                    <User className="text-green-500" size={24} />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {selectedRequest.mentee_name || selectedRequest.mentee_username || 'Unknown Mentee'}
                    </h3>
                    <p className="text-gray-500">@{selectedRequest.mentee_username}</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowRespondModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X size={20} className="text-gray-500" />
                </button>
              </div>

              <div className="space-y-4">
                <div className="py-2 border-b border-gray-100">
                  <span className="text-gray-500 block mb-1">Topic</span>
                  <span className="text-gray-900">{selectedRequest.topic}</span>
                </div>

                {selectedRequest.goals && (
                  <div className="py-2 border-b border-gray-100">
                    <span className="text-gray-500 block mb-1">Goals</span>
                    <span className="text-gray-900">{selectedRequest.goals}</span>
                  </div>
                )}

                {selectedRequest.message && (
                  <div className="py-2 border-b border-gray-100">
                    <span className="text-gray-500 block mb-1">Message from Mentee</span>
                    <p className="text-gray-900">{selectedRequest.message}</p>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Your Response Message (optional)
                  </label>
                  <textarea
                    value={responseMessage}
                    onChange={(e) => setResponseMessage(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Add a personal message to your response..."
                    rows={3}
                  />
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-gray-200 flex gap-3">
                <button
                  onClick={() => handleRespond(selectedRequest.request_id, 'rejected')}
                  disabled={actionLoading}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                >
                  <XCircle size={18} />
                  {actionLoading ? 'Processing...' : 'Decline'}
                </button>
                <button
                  onClick={() => handleRespond(selectedRequest.request_id, 'accepted')}
                  disabled={actionLoading}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                >
                  <CheckCircle size={18} />
                  {actionLoading ? 'Processing...' : 'Accept'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MentorRequestsReceived;
