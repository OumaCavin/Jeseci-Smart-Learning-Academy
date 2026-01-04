import React, { useState, useEffect, useCallback } from 'react';
import {
  History,
  X,
  CheckCircle,
  AlertCircle,
  Loader,
  Filter,
  Search,
  User,
  Calendar,
  Clock,
  RotateCcw,
  MoreVertical
} from 'lucide-react';
import advancedCollaborationService, {
  ModerationAction
} from '../../services/advancedCollaborationService';

interface ModerationActionsHistoryProps {
  onClose?: () => void;
}

const ModerationActionsHistory: React.FC<ModerationActionsHistoryProps> = ({ onClose }) => {
  const [actions, setActions] = useState<ModerationAction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterActionType, setFilterActionType] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAction, setSelectedAction] = useState<ModerationAction | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  const fetchActions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await advancedCollaborationService.getModerationActions();

      if (response.success && response.data) {
        setActions(response.data as ModerationAction[]);
      } else {
        setError(response.error || 'Failed to load actions');
      }
    } catch (err) {
      setError('An error occurred while loading actions');
      console.error('Error fetching moderation actions:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchActions();
  }, [fetchActions]);

  const getActionTypeBadge = (actionType: string) => {
    const styles: Record<string, string> = {
      content_removed: 'bg-red-100 text-red-700',
      content_hidden: 'bg-orange-100 text-orange-700',
      user_warned: 'bg-yellow-100 text-yellow-700',
      user_suspended: 'bg-orange-100 text-orange-700',
      user_banned: 'bg-red-100 text-red-700',
      report_dismissed: 'bg-gray-100 text-gray-700',
      content_edited: 'bg-blue-100 text-blue-700'
    };

    const labels: Record<string, string> = {
      content_removed: 'Content Removed',
      content_hidden: 'Content Hidden',
      user_warned: 'User Warned',
      user_suspended: 'User Suspended',
      user_banned: 'User Banned',
      report_dismissed: 'Report Dismissed',
      content_edited: 'Content Edited'
    };

    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${styles[actionType] || 'bg-gray-100 text-gray-700'}`}>
        {labels[actionType] || actionType}
      </span>
    );
  };

  const filteredActions = actions.filter(action => {
    const matchesActionType = filterActionType === 'all' || action.action_type === filterActionType;

    const matchesSearch = !searchQuery ||
      action.moderator_username?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      action.reason?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      action.content_id?.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesActionType && matchesSearch;
  });

  const actionTypeCounts = {
    content_removed: actions.filter(a => a.action_type === 'content_removed').length,
    content_hidden: actions.filter(a => a.action_type === 'content_hidden').length,
    user_warned: actions.filter(a => a.action_type === 'user_warned').length,
    user_suspended: actions.filter(a => a.action_type === 'user_suspended').length,
    user_banned: actions.filter(a => a.action_type === 'user_banned').length,
    report_dismissed: actions.filter(a => a.action_type === 'report_dismissed').length,
    content_edited: actions.filter(a => a.action_type === 'content_edited').length
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
          <History className="text-blue-500" size={24} />
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Moderation History</h2>
            <p className="text-sm text-gray-500">View all moderation actions taken</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X size={20} className="text-gray-500" />
        </button>
      </div>

      {/* Error Message */}
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
              placeholder="Search actions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter size={18} className="text-gray-400" />
            <select
              value={filterActionType}
              onChange={(e) => setFilterActionType(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Actions ({actions.length})</option>
              <option value="content_removed">Removed ({actionTypeCounts.content_removed})</option>
              <option value="content_hidden">Hidden ({actionTypeCounts.content_hidden})</option>
              <option value="user_warned">Warned ({actionTypeCounts.user_warned})</option>
              <option value="user_suspended">Suspended ({actionTypeCounts.user_suspended})</option>
              <option value="user_banned">Banned ({actionTypeCounts.user_banned})</option>
              <option value="report_dismissed">Dismissed ({actionTypeCounts.report_dismissed})</option>
              <option value="content_edited">Edited ({actionTypeCounts.content_edited})</option>
            </select>
          </div>
        </div>
      </div>

      {/* Actions List */}
      <div className="overflow-y-auto max-h-[400px] p-4">
        {filteredActions.length === 0 ? (
          <div className="text-center py-8">
            <History size={48} className="mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500">No moderation actions found</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredActions.map((action) => (
              <div
                key={action.action_id}
                className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all cursor-pointer"
                onClick={() => {
                  setSelectedAction(action);
                  setShowDetailModal(true);
                }}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      {getActionTypeBadge(action.action_type)}
                      {action.is_reversed && (
                        <span className="flex items-center gap-1 px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs">
                          <RotateCcw size={12} />
                          Reversed
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{action.reason}</p>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <User size={14} />
                        {action.moderator_username || 'Unknown'}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar size={14} />
                        {new Date(action.created_at).toLocaleDateString()}
                      </span>
                      {action.duration && (
                        <span className="text-orange-600">
                          Duration: {action.duration} days
                        </span>
                      )}
                    </div>
                  </div>
                  <MoreVertical size={20} className="text-gray-400" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Action Detail Modal */}
      {showDetailModal && selectedAction && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <History className="text-blue-500" size={20} />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      Moderation Action Details
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                      {getActionTypeBadge(selectedAction.action_type)}
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
                  <span className="text-gray-500 block mb-1">Action Type</span>
                  <span className="text-gray-900">{selectedAction.action_type}</span>
                </div>

                <div className="py-2 border-b border-gray-100">
                  <span className="text-gray-500 block mb-1">Reason</span>
                  <p className="text-gray-900">{selectedAction.reason}</p>
                </div>

                {selectedAction.notes && (
                  <div className="py-2 border-b border-gray-100">
                    <span className="text-gray-500 block mb-1">Notes</span>
                    <p className="text-gray-900">{selectedAction.notes}</p>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4 py-2 border-b border-gray-100">
                  <div>
                    <span className="text-gray-500 block mb-1">Moderator</span>
                    <span className="text-gray-900">{selectedAction.moderator_username || 'Unknown'}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block mb-1">Content Type</span>
                    <span className="text-gray-900">{selectedAction.content_type}</span>
                  </div>
                </div>

                <div className="py-2 border-b border-gray-100">
                  <span className="text-gray-500 block mb-1">Content ID</span>
                  <span className="text-gray-900">{selectedAction.content_id}</span>
                </div>

                <div className="grid grid-cols-2 gap-4 py-2 border-b border-gray-100">
                  <div>
                    <span className="text-gray-500 block mb-1">Created</span>
                    <span className="text-gray-900">
                      {new Date(selectedAction.created_at).toLocaleString()}
                    </span>
                  </div>
                  {selectedAction.duration && (
                    <div>
                      <span className="text-gray-500 block mb-1">Duration</span>
                      <span className="text-gray-900">{selectedAction.duration} days</span>
                    </div>
                  )}
                </div>

                {selectedAction.is_reversed && (
                  <div className="py-2 border-b border-gray-100">
                    <span className="text-gray-500 block mb-1">Reversal Status</span>
                    <span className="text-purple-600">This action has been reversed</span>
                  </div>
                )}

                {selectedAction.report_id && (
                  <div className="py-2">
                    <span className="text-gray-500 block mb-1">Report ID</span>
                    <span className="text-gray-900">{selectedAction.report_id}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModerationActionsHistory;
