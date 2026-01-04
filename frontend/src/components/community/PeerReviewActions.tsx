import React, { useState, useEffect, useCallback } from 'react';
import {
  CheckCircle,
  XCircle,
  Clock,
  Star,
  FileText,
  MessageSquare,
  AlertCircle,
  Loader,
  ChevronRight,
  ThumbsUp,
  Edit3,
  Eye,
  User,
  X
} from 'lucide-react';
import advancedCollaborationService, {
  PeerReviewAssignment
} from '../../services/advancedCollaborationService';

interface PeerReviewActionsProps {
  onClose?: () => void;
}

const PeerReviewActions: React.FC<PeerReviewActionsProps> = ({ onClose }) => {
  const [assignments, setAssignments] = useState<PeerReviewAssignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [selectedAssignment, setSelectedAssignment] = useState<PeerReviewAssignment | null>(null);
  const [showCompleteModal, setShowCompleteModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  // Complete review form state
  const [reviewContent, setReviewContent] = useState('');
  const [rating, setRating] = useState(3);
  const [feedback, setFeedback] = useState<{
    strengths: string;
    improvements: string;
    comments: string;
  }>({
    strengths: '',
    improvements: '',
    comments: ''
  });

  const fetchAssignments = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await advancedCollaborationService.getMyReviewAssignments();

      if (response.success && response.data) {
        setAssignments(response.data as PeerReviewAssignment[]);
      } else {
        setError(response.error || 'Failed to load assignments');
      }
    } catch (err) {
      setError('An error occurred while loading assignments');
      console.error('Error fetching review assignments:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAssignments();
  }, [fetchAssignments]);

  const handleAcceptAssignment = async (assignment: PeerReviewAssignment) => {
    try {
      setActionLoading(true);
      setError(null);

      const response = await advancedCollaborationService.acceptPeerReviewAssignment(
        assignment.assignment_id
      );

      if (response.success) {
        setSuccessMessage('Assignment accepted successfully');
        fetchAssignments();
      } else {
        setError(response.error || 'Failed to accept assignment');
      }
    } catch (err) {
      setError('An error occurred while accepting assignment');
      console.error('Error accepting assignment:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCompleteReview = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedAssignment) return;

    try {
      setActionLoading(true);
      setError(null);

      const response = await advancedCollaborationService.submitPeerReviewFeedback(
        selectedAssignment.assignment_id,
        rating,
        feedback.strengths,
        feedback.improvements,
        feedback.comments
      );

      if (response.success) {
        setSuccessMessage('Review submitted successfully!');
        setShowCompleteModal(false);
        setReviewContent('');
        setRating(3);
        setFeedback({ strengths: '', improvements: '', comments: '' });
        fetchAssignments();
      } else {
        setError(response.error || 'Failed to submit review');
      }
    } catch (err) {
      setError('An error occurred while submitting review');
      console.error('Error completing review:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      assigned: 'bg-blue-100 text-blue-700',
      in_progress: 'bg-yellow-100 text-yellow-700',
      completed: 'bg-green-100 text-green-700',
      declined: 'bg-red-100 text-red-700'
    };

    const icons: Record<string, React.ReactNode> = {
      assigned: <Clock size={12} />,
      in_progress: <Edit3 size={12} />,
      completed: <CheckCircle size={12} />,
      declined: <XCircle size={12} />
    };

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${styles[status] || 'bg-gray-100 text-gray-700'}`}>
        {icons[status]}
        {status.replace('_', ' ').charAt(0).toUpperCase() + status.replace('_', ' ').slice(1)}
      </span>
    );
  };

  const openCompleteModal = (assignment: PeerReviewAssignment) => {
    setSelectedAssignment(assignment);
    setShowCompleteModal(true);
  };

  const filteredAssignments = assignments.filter(assignment => {
    return filterStatus === 'all' || assignment.status === filterStatus;
  });

  const pendingCount = assignments.filter(a => a.status === 'assigned').length;
  const inProgressCount = assignments.filter(a => a.status === 'in_progress').length;
  const completedCount = assignments.filter(a => a.status === 'completed').length;

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
          <FileText className="text-blue-500" size={24} />
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Review Assignments</h2>
            <p className="text-sm text-gray-500">Accept and complete peer review tasks</p>
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
        <div className="flex gap-2">
          <button
            onClick={() => setFilterStatus('all')}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              filterStatus === 'all'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All ({assignments.length})
          </button>
          <button
            onClick={() => setFilterStatus('assigned')}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              filterStatus === 'assigned'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Pending ({pendingCount})
          </button>
          <button
            onClick={() => setFilterStatus('in_progress')}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              filterStatus === 'in_progress'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            In Progress ({inProgressCount})
          </button>
          <button
            onClick={() => setFilterStatus('completed')}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              filterStatus === 'completed'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Completed ({completedCount})
          </button>
        </div>
      </div>

      {/* Assignments List */}
      <div className="overflow-y-auto max-h-[400px] p-4">
        {filteredAssignments.length === 0 ? (
          <div className="text-center py-8">
            <FileText size={48} className="mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500">No review assignments found</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredAssignments.map((assignment) => (
              <div
                key={assignment.assignment_id}
                className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium text-gray-900">
                        {assignment.submission_title}
                      </h4>
                      {getStatusBadge(assignment.status)}
                    </div>
                    <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                      {assignment.submission_description}
                    </p>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <User size={14} />
                        {assignment.author_username}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock size={14} />
                        {new Date(assignment.assigned_at).toLocaleDateString()}
                      </span>
                      {assignment.deadline && (
                        <span className="text-red-500">
                          Due: {new Date(assignment.deadline).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {assignment.status === 'assigned' && (
                      <button
                        onClick={() => handleAcceptAssignment(assignment)}
                        disabled={actionLoading}
                        className="flex items-center gap-1 px-3 py-1 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm"
                      >
                        <CheckCircle size={14} />
                        Accept
                      </button>
                    )}
                    {assignment.status === 'in_progress' && (
                      <button
                        onClick={() => openCompleteModal(assignment)}
                        className="flex items-center gap-1 px-3 py-1 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm"
                      >
                        <Edit3 size={14} />
                        Complete
                      </button>
                    )}
                    <button
                      onClick={() => {
                        setSelectedAssignment(assignment);
                        // View submission details
                      }}
                      className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <Eye size={18} className="text-gray-500" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Complete Review Modal */}
      {showCompleteModal && selectedAssignment && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Complete Review</h3>
                  <p className="text-sm text-gray-500 mt-1">{selectedAssignment.submission_title}</p>
                </div>
                <button
                  onClick={() => setShowCompleteModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X size={20} className="text-gray-500" />
                </button>
              </div>

              <form onSubmit={handleCompleteReview} className="space-y-4">
                {/* Rating */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Overall Rating
                  </label>
                  <div className="flex items-center gap-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        type="button"
                        onClick={() => setRating(star)}
                        className={`p-1 ${rating >= star ? 'text-yellow-500' : 'text-gray-300'}`}
                      >
                        <Star size={24} fill={rating >= star ? 'currentColor' : 'none'} />
                      </button>
                    ))}
                    <span className="ml-2 text-sm text-gray-600">{rating}/5</span>
                  </div>
                </div>

                {/* Strengths */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Strengths
                  </label>
                  <textarea
                    value={feedback.strengths}
                    onChange={(e) => setFeedback({ ...feedback, strengths: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="What are the strengths of this submission?"
                    rows={3}
                    required
                  />
                </div>

                {/* Improvements */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Areas for Improvement
                  </label>
                  <textarea
                    value={feedback.improvements}
                    onChange={(e) => setFeedback({ ...feedback, improvements: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="What could be improved?"
                    rows={3}
                    required
                  />
                </div>

                {/* Comments */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Additional Comments
                  </label>
                  <textarea
                    value={feedback.comments}
                    onChange={(e) => setFeedback({ ...feedback, comments: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Any additional feedback..."
                    rows={2}
                  />
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowCompleteModal(false)}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={actionLoading}
                    className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
                  >
                    {actionLoading ? 'Submitting...' : 'Submit Review'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PeerReviewActions;
