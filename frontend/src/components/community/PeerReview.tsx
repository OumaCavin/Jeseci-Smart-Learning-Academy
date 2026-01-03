import React, { useState, useEffect, useCallback } from 'react';
import { 
  Star, 
  CheckCircle, 
  XCircle, 
  Clock, 
  User, 
  FileText, 
  MessageSquare,
  Eye,
  Send,
  Award,
  TrendingUp,
  Target,
  Users,
  BookOpen,
  AlertCircle,
  RefreshCw,
  ChevronRight,
  ThumbsUp,
  Edit3,
  Eye as ViewIcon,
  Filter,
  Search,
  SortAsc,
  SortDesc
} from 'lucide-react';
import advancedCollaborationService from '../../services/advancedCollaborationService';

// Type definitions
interface PeerReviewSubmission {
  id: number;
  authorId: number;
  authorUsername: string;
  authorReputation: number;
  title: string;
  description: string;
  contentType: string;
  contentUrl: string;
  status: 'pending' | 'assigned' | 'in_review' | 'completed' | 'approved' | 'needs_revision' | 'rejected';
  reviewerId: number | null;
  reviewerUsername: string | null;
  averageRating: number | null;
  createdAt: string;
  updatedAt: string;
  dueDate: string | null;
}

interface PeerReviewAssignment {
  id: number;
  submissionId: number;
  reviewerId: number;
  reviewerUsername: string;
  status: 'pending' | 'accepted' | 'completed' | 'declined';
  assignedAt: string;
  completedAt: string | null;
  feedbackRating: number | null;
}

interface PeerReviewFeedback {
  id: number;
  submissionId: number;
  reviewerId: number;
  reviewerUsername: string;
  rating: number;
  strengths: string;
  improvements: string;
  comments: string;
  createdAt: string;
}

interface ReviewStats {
  totalSubmissions: number;
  pendingReviews: number;
  averageRating: number;
  reviewsGiven: number;
  reviewsReceived: number;
  topReviewers: Array<{ username: string; reviewsCount: number; averageRating: number }>;
}

interface ContentItem {
  type: string;
  id: number;
  title: string;
  description: string;
  content: string;
}

const PeerReview: React.FC = () => {
  // State management
  const [activeTab, setActiveTab] = useState<'submissions' | 'assignments' | 'feedback' | 'stats'>('submissions');
  const [submissions, setSubmissions] = useState<PeerReviewSubmission[]>([]);
  const [assignments, setAssignments] = useState<PeerReviewAssignment[]>([]);
  const [feedback, setFeedback] = useState<PeerReviewFeedback[]>([]);
  const [stats, setStats] = useState<ReviewStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSubmission, setSelectedSubmission] = useState<PeerReviewSubmission | null>(null);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<string>('createdAt');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Feedback form state
  const [feedbackRating, setFeedbackRating] = useState(3);
  const [feedbackStrengths, setFeedbackStrengths] = useState('');
  const [feedbackImprovements, setFeedbackImprovements] = useState('');
  const [feedbackComments, setFeedbackComments] = useState('');

  // Submit form state
  const [submitTitle, setSubmitTitle] = useState('');
  const [submitDescription, setSubmitDescription] = useState('');
  const [submitContentType, setSubmitContentType] = useState('study_note');
  const [submitContent, setSubmitContent] = useState('');

  // Fetch peer review data
  const fetchPeerReviewData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [submissionsData, assignmentsData, feedbackData, statsData] = await Promise.all([
        advancedCollaborationService.getPeerReviewSubmissions(),
        advancedCollaborationService.getPeerReviewAssignments(),
        advancedCollaborationService.getPeerReviewFeedback(),
        advancedCollaborationService.getReviewStats()
      ]);

      setSubmissions(submissionsData.data || []);
      setAssignments(assignmentsData.data || []);
      setFeedback(feedbackData.data || []);
      setStats(statsData.data);
    } catch (err) {
      setError('Failed to load peer review data');
      console.error('Error fetching peer review data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPeerReviewData();
  }, [fetchPeerReviewData]);

  // Handle feedback submission
  const handleSubmitFeedback = async () => {
    if (!selectedSubmission || !feedbackStrengths.trim() || !feedbackImprovements.trim()) return;

    try {
      await advancedCollaborationService.submitPeerReviewFeedback(
        selectedSubmission.id,
        {
          rating: feedbackRating,
          strengths: feedbackStrengths,
          improvements: feedbackImprovements,
          comments: feedbackComments
        }
      );

      setShowFeedbackModal(false);
      setSelectedSubmission(null);
      setFeedbackRating(3);
      setFeedbackStrengths('');
      setFeedbackImprovements('');
      setFeedbackComments('');
      fetchPeerReviewData();
    } catch (err) {
      setError('Failed to submit feedback');
      console.error('Error submitting feedback:', err);
    }
  };

  // Handle assignment acceptance
  const handleAcceptAssignment = async (assignmentId: string) => {
    try {
      await advancedCollaborationService.acceptPeerReviewAssignment(assignmentId);
      fetchPeerReviewData();
    } catch (err) {
      setError('Failed to accept assignment');
      console.error('Error accepting assignment:', err);
    }
  };

  // Handle assignment completion
  const handleCompleteAssignment = async (assignmentId: string) => {
    try {
      await advancedCollaborationService.completePeerReviewAssignment(assignmentId);
      fetchPeerReviewData();
    } catch (err) {
      setError('Failed to complete assignment');
      console.error('Error completing assignment:', err);
    }
  };

  // Handle new submission
  const handleSubmitContent = async () => {
    if (!submitTitle.trim() || !submitDescription.trim() || !submitContent.trim()) return;

    try {
      await advancedCollaborationService.createPeerReviewSubmission({
        title: submitTitle,
        description: submitDescription,
        contentType: submitContentType,
        content: submitContent
      });

      setShowSubmitModal(false);
      setSubmitTitle('');
      setSubmitDescription('');
      setSubmitContent('');
      setSubmitContentType('study_note');
      fetchPeerReviewData();
    } catch (err) {
      setError('Failed to submit content for review');
      console.error('Error submitting content:', err);
    }
  };

  // Get status badge color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'assigned': return 'bg-blue-100 text-blue-800';
      case 'in_review': return 'bg-purple-100 text-purple-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'approved': return 'bg-emerald-100 text-emerald-800';
      case 'needs_revision': return 'bg-orange-100 text-orange-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'accepted': return 'bg-green-100 text-green-800';
      case 'declined': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Render star rating
  const renderStarRating = (rating: number, interactive = false) => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => interactive && setFeedbackRating(star)}
            disabled={!interactive}
            className={`${interactive ? 'cursor-pointer hover:scale-110 transition-transform' : ''}`}
          >
            <Star
              className={`w-5 h-5 ${
                star <= rating
                  ? 'text-yellow-400 fill-yellow-400'
                  : 'text-gray-300'
              }`}
            />
          </button>
        ))}
      </div>
    );
  };

  // Filter and sort submissions
  const filteredSubmissions = submissions
    .filter(sub => {
      if (filterStatus !== 'all' && sub.status !== filterStatus) return false;
      if (filterType !== 'all' && sub.contentType !== filterType) return false;
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          sub.title.toLowerCase().includes(query) ||
          sub.authorUsername.toLowerCase().includes(query) ||
          sub.description.toLowerCase().includes(query)
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
        case 'title':
          comparison = a.title.localeCompare(b.title);
          break;
        case 'rating':
          const ratingA = a.averageRating || 0;
          const ratingB = b.averageRating || 0;
          comparison = ratingA - ratingB;
          break;
        default:
          comparison = 0;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

  // Loading state
  if (loading && !submissions.length) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading peer review data...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !submissions.length) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchPeerReviewData}
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
              <BookOpen className="w-8 h-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">Peer Review System</h1>
            </div>
            <button
              onClick={() => setShowSubmitModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              <Send className="w-4 h-4" />
              Submit for Review
            </button>
          </div>

          {/* Stats Overview */}
          {stats && (
            <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-blue-600 font-medium">My Submissions</p>
                    <p className="text-2xl font-bold text-blue-900">{stats.totalSubmissions}</p>
                  </div>
                  <FileText className="w-8 h-8 text-blue-300" />
                </div>
              </div>
              <div className="bg-yellow-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-yellow-600 font-medium">Pending Reviews</p>
                    <p className="text-2xl font-bold text-yellow-900">{stats.pendingReviews}</p>
                  </div>
                  <Clock className="w-8 h-8 text-yellow-300" />
                </div>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-green-600 font-medium">Average Rating</p>
                    <p className="text-2xl font-bold text-green-900">
                      {stats.averageRating > 0 ? stats.averageRating.toFixed(1) : 'N/A'}
                    </p>
                  </div>
                  <Star className="w-8 h-8 text-green-300 fill-green-300" />
                </div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-purple-600 font-medium">Reviews Given</p>
                    <p className="text-2xl font-bold text-purple-900">{stats.reviewsGiven}</p>
                  </div>
                  <Users className="w-8 h-8 text-purple-300" />
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
            onClick={() => setActiveTab('submissions')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'submissions'
                ? 'bg-white text-gray-900 shadow'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              My Submissions
            </div>
          </button>
          <button
            onClick={() => setActiveTab('assignments')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'assignments'
                ? 'bg-white text-gray-900 shadow'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4" />
              Review Assignments
              {assignments.filter(a => a.status === 'pending').length > 0 && (
                <span className="bg-yellow-500 text-white text-xs px-2 py-0.5 rounded-full">
                  {assignments.filter(a => a.status === 'pending').length}
                </span>
              )}
            </div>
          </button>
          <button
            onClick={() => setActiveTab('feedback')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'feedback'
                ? 'bg-white text-gray-900 shadow'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Feedback Received
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

        {/* Submissions Tab */}
        {activeTab === 'submissions' && (
          <div className="space-y-4">
            {/* Filters */}
            <div className="bg-white rounded-lg shadow p-4 flex flex-wrap gap-4 items-center">
              <div className="flex-1 min-w-[200px]">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search submissions..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="assigned">Assigned</option>
                <option value="in_review">In Review</option>
                <option value="completed">Completed</option>
                <option value="approved">Approved</option>
                <option value="needs_revision">Needs Revision</option>
                <option value="rejected">Rejected</option>
              </select>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Types</option>
                <option value="study_note">Study Note</option>
                <option value="solution">Solution</option>
                <option value="explanation">Explanation</option>
                <option value="summary">Summary</option>
              </select>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="createdAt">Sort by Date</option>
                <option value="title">Sort by Title</option>
                <option value="rating">Sort by Rating</option>
              </select>
              <button
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                {sortOrder === 'asc' ? <SortAsc className="w-5 h-5" /> : <SortDesc className="w-5 h-5" />}
              </button>
            </div>

            {/* Submissions List */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
              {filteredSubmissions.length === 0 ? (
                <div className="p-8 text-center">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 mb-4">No submissions found</p>
                  <button
                    onClick={() => setShowSubmitModal(true)}
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                  >
                    Submit Your First Content
                  </button>
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {filteredSubmissions.map((submission) => (
                    <div
                      key={submission.id}
                      className="p-4 hover:bg-gray-50 transition-colors cursor-pointer"
                      onClick={() => setSelectedSubmission(submission)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(submission.status)}`}>
                              {submission.status.replace('_', ' ').toUpperCase()}
                            </span>
                            <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-700 capitalize">
                              {submission.contentType.replace('_', ' ')}
                            </span>
                            <span className="text-sm text-gray-500">
                              {new Date(submission.createdAt).toLocaleDateString()}
                            </span>
                          </div>
                          <h3 className="font-medium text-gray-900 mb-1">{submission.title}</h3>
                          <p className="text-gray-600 text-sm mb-2 line-clamp-2">{submission.description}</p>
                          <div className="flex items-center gap-4 text-sm text-gray-500">
                            <span className="flex items-center gap-1">
                              <User className="w-4 h-4" />
                              {submission.authorUsername}
                            </span>
                            {submission.averageRating !== null && (
                              <span className="flex items-center gap-1">
                                <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                                {submission.averageRating.toFixed(1)}
                              </span>
                            )}
                            {submission.reviewerUsername && (
                              <span className="flex items-center gap-1">
                                <Eye className="w-4 h-4" />
                                Reviewer: {submission.reviewerUsername}
                              </span>
                            )}
                          </div>
                        </div>
                        <ChevronRight className="w-5 h-5 text-gray-400" />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Assignments Tab */}
        {activeTab === 'assignments' && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Review Assignments</h3>
              <p className="text-sm text-gray-500 mt-1">Content assigned to you for peer review</p>
            </div>
            {assignments.length === 0 ? (
              <div className="p-8 text-center">
                <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No review assignments pending</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {assignments.map((assignment) => {
                  const submission = submissions.find(s => s.id === assignment.submissionId);
                  return (
                    <div key={assignment.id} className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(assignment.status)}`}>
                              {assignment.status.toUpperCase()}
                            </span>
                            <span className="text-sm text-gray-500">
                              Assigned {new Date(assignment.assignedAt).toLocaleDateString()}
                            </span>
                          </div>
                          {submission && (
                            <>
                              <h4 className="font-medium text-gray-900 mb-1">{submission.title}</h4>
                              <p className="text-gray-600 text-sm mb-2">{submission.description}</p>
                            </>
                          )}
                          <div className="flex items-center gap-4 text-sm text-gray-500">
                            <span className="flex items-center gap-1">
                              <User className="w-4 h-4" />
                              Author: {submission?.authorUsername}
                            </span>
                            {assignment.feedbackRating !== null && (
                              <span className="flex items-center gap-1">
                                <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                                Your rating: {assignment.feedbackRating}
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2 ml-4">
                          {assignment.status === 'pending' && (
                            <button
                              onClick={() => handleAcceptAssignment(assignment.id)}
                              className="px-3 py-1 bg-green-500 text-white text-sm rounded-lg hover:bg-green-600 transition-colors"
                            >
                              Accept
                            </button>
                          )}
                          {assignment.status === 'accepted' && (
                            <button
                              onClick={() => {
                                const sub = submissions.find(s => s.id === assignment.submissionId);
                                if (sub) {
                                  setSelectedSubmission(sub);
                                  setShowFeedbackModal(true);
                                }
                              }}
                              className="px-3 py-1 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600 transition-colors"
                            >
                              Start Review
                            </button>
                          )}
                          {assignment.status === 'completed' && (
                            <span className="flex items-center gap-1 text-green-600 text-sm">
                              <CheckCircle className="w-4 h-4" />
                              Completed
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Feedback Tab */}
        {activeTab === 'feedback' && (
          <div className="space-y-4">
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="p-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Feedback Received</h3>
                <p className="text-sm text-gray-500 mt-1">Reviews and ratings from other community members</p>
              </div>
              {feedback.length === 0 ? (
                <div className="p-8 text-center">
                  <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No feedback received yet</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {feedback.map((item) => {
                    const submission = submissions.find(s => s.id === item.submissionId);
                    return (
                      <div key={item.id} className="p-4">
                        <div className="flex items-start gap-4">
                          <div className="flex-shrink-0">
                            <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                              <User className="w-5 h-5 text-blue-600" />
                            </div>
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="font-medium text-gray-900">
                                {item.reviewerUsername}
                              </span>
                              <span className="text-gray-500">reviewed</span>
                              <span className="font-medium text-blue-600">
                                {submission?.title}
                              </span>
                            </div>
                            <div className="flex items-center gap-2 mb-3">
                              {renderStarRating(item.rating)}
                              <span className="text-sm text-gray-500">
                                {new Date(item.createdAt).toLocaleDateString()}
                              </span>
                            </div>
                            <div className="bg-green-50 rounded-lg p-3 mb-2">
                              <div className="flex items-center gap-2 mb-1">
                                <ThumbsUp className="w-4 h-4 text-green-600" />
                                <span className="text-sm font-medium text-green-700">Strengths</span>
                              </div>
                              <p className="text-sm text-green-800">{item.strengths}</p>
                            </div>
                            <div className="bg-yellow-50 rounded-lg p-3 mb-2">
                              <div className="flex items-center gap-2 mb-1">
                                <Edit3 className="w-4 h-4 text-yellow-600" />
                                <span className="text-sm font-medium text-yellow-700">Areas for Improvement</span>
                              </div>
                              <p className="text-sm text-yellow-800">{item.improvements}</p>
                            </div>
                            {item.comments && (
                              <div className="bg-gray-50 rounded-lg p-3">
                                <div className="flex items-center gap-2 mb-1">
                                  <MessageSquare className="w-4 h-4 text-gray-600" />
                                  <span className="text-sm font-medium text-gray-700">Additional Comments</span>
                                </div>
                                <p className="text-sm text-gray-800">{item.comments}</p>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Stats Tab */}
        {activeTab === 'stats' && stats && (
          <div className="space-y-6">
            {/* Top Reviewers */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Top Contributors</h3>
              <div className="space-y-4">
                {stats.topReviewers.map((reviewer, index) => (
                  <div key={index} className="flex items-center gap-4">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                      index === 0 ? 'bg-yellow-100 text-yellow-700' :
                      index === 1 ? 'bg-gray-100 text-gray-700' :
                      index === 2 ? 'bg-orange-100 text-orange-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{reviewer.username}</p>
                      <p className="text-sm text-gray-500">{reviewer.reviewsCount} reviews given</p>
                    </div>
                    <div className="flex items-center gap-2">
                      {renderStarRating(reviewer.averageRating)}
                      <span className="text-sm text-gray-500">
                        ({reviewer.averageRating.toFixed(1)})
                      </span>
                    </div>
                  </div>
                ))}
                {stats.topReviewers.length === 0 && (
                  <p className="text-gray-500 text-center py-4">No reviewers yet</p>
                )}
              </div>
            </div>

            {/* Review Metrics */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Review Metrics</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-3xl font-bold text-blue-600">{stats.totalSubmissions}</p>
                  <p className="text-sm text-gray-600 mt-1">Total Submissions</p>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-3xl font-bold text-green-600">{stats.reviewsReceived}</p>
                  <p className="text-sm text-gray-600 mt-1">Reviews Received</p>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <p className="text-3xl font-bold text-purple-600">{stats.reviewsGiven}</p>
                  <p className="text-sm text-gray-600 mt-1">Reviews Given</p>
                </div>
              </div>
            </div>

            {/* Community Impact */}
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg shadow p-6 text-white">
              <div className="flex items-center gap-3 mb-4">
                <Award className="w-8 h-8" />
                <h3 className="text-lg font-medium">Community Impact</h3>
              </div>
              <p className="text-white/80 mb-4">
                By participating in peer reviews, you help maintain quality content and build
                a collaborative learning community. Keep reviewing and contributing!
              </p>
              <div className="flex items-center gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold">
                    {stats.reviewsGiven > 0 ? '+' : ''}{(stats.reviewsGiven * 5).toFixed(0)}
                  </p>
                  <p className="text-sm text-white/70">Reputation Earned</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold">{stats.reviewsGiven}</p>
                  <p className="text-sm text-white/70">Reviews Completed</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Feedback Modal */}
      {showFeedbackModal && selectedSubmission && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Submit Review</h3>
                <button
                  onClick={() => setShowFeedbackModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="w-6 h-6" />
                </button>
              </div>

              {/* Content Preview */}
              <div className="bg-gray-50 rounded-lg p-4 mb-4">
                <h4 className="font-medium text-gray-900 mb-1">{selectedSubmission.title}</h4>
                <p className="text-gray-600 text-sm mb-2">{selectedSubmission.description}</p>
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <span>By {selectedSubmission.authorUsername}</span>
                  <span>•</span>
                  <span className="capitalize">{selectedSubmission.contentType.replace('_', ' ')}</span>
                </div>
              </div>

              {/* Rating */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Overall Rating
                </label>
                <div className="flex items-center gap-4">
                  {renderStarRating(feedbackRating, true)}
                  <span className="text-sm text-gray-500">
                    {feedbackRating >= 4 ? 'Excellent' :
                     feedbackRating >= 3 ? 'Good' :
                     feedbackRating >= 2 ? 'Fair' : 'Poor'}
                  </span>
                </div>
              </div>

              {/* Strengths */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What are the strengths of this content?
                </label>
                <textarea
                  value={feedbackStrengths}
                  onChange={(e) => setFeedbackStrengths(e.target.value)}
                  placeholder="Highlight the positive aspects..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Improvements */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What areas need improvement?
                </label>
                <textarea
                  value={feedbackImprovements}
                  onChange={(e) => setFeedbackImprovements(e.target.value)}
                  placeholder="Suggest specific improvements..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Additional Comments */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Additional Comments (Optional)
                </label>
                <textarea
                  value={feedbackComments}
                  onChange={(e) => setFeedbackComments(e.target.value)}
                  placeholder="Any other thoughts or suggestions..."
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => setShowFeedbackModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmitFeedback}
                  disabled={!feedbackStrengths.trim() || !feedbackImprovements.trim()}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Submit Review
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Submit Content Modal */}
      {showSubmitModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Submit Content for Review</h3>
                <button
                  onClick={() => setShowSubmitModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="w-6 h-6" />
                </button>
              </div>

              {/* Content Type */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Content Type
                </label>
                <select
                  value={submitContentType}
                  onChange={(e) => setSubmitContentType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="study_note">Study Note</option>
                  <option value="solution">Solution</option>
                  <option value="explanation">Explanation</option>
                  <option value="summary">Summary</option>
                </select>
              </div>

              {/* Title */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Title
                </label>
                <input
                  type="text"
                  value={submitTitle}
                  onChange={(e) => setSubmitTitle(e.target.value)}
                  placeholder="Enter a descriptive title"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Description */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Brief Description
                </label>
                <textarea
                  value={submitDescription}
                  onChange={(e) => setSubmitDescription(e.target.value)}
                  placeholder="Summarize your content in 1-2 sentences"
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Content */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Content
                </label>
                <textarea
                  value={submitContent}
                  onChange={(e) => setSubmitContent(e.target.value)}
                  placeholder="Enter your content here..."
                  rows={10}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                />
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => setShowSubmitModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmitContent}
                  disabled={!submitTitle.trim() || !submitDescription.trim() || !submitContent.trim()}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Submit for Review
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PeerReview;
