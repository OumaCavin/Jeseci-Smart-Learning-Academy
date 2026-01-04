import React, { useState, useEffect, useCallback } from 'react';
import {
  Calendar,
  Plus,
  Clock,
  MapPin,
  Users,
  X,
  CheckCircle,
  AlertCircle,
  LoadingSpinner,
  ChevronLeft,
  ChevronRight,
  Video,
  FileText,
  MessageSquare
} from 'lucide-react';
import advancedCollaborationService, {
  StudyGroupMessage
} from '../../services/advancedCollaborationService';

interface StudyGroupEventsProps {
  groupId: string;
  groupName: string;
  isAdmin?: boolean;
  onClose?: () => void;
}

interface GroupEvent {
  event_id: string;
  group_id: string;
  title: string;
  description: string;
  event_time: string;
  duration_minutes: number;
  created_by: number;
  creator_name: string;
  created_at: string;
  participant_count?: number;
  is_participating?: boolean;
}

const StudyGroupEvents: React.FC<StudyGroupEventsProps> = ({
  groupId,
  groupName,
  isAdmin = false,
  onClose
}) => {
  const [events, setEvents] = useState<GroupEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<GroupEvent | null>(null);
  const [showEventModal, setShowEventModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  // Create form state
  const [createTitle, setCreateTitle] = useState('');
  const [createDescription, setCreateDescription] = useState('');
  const [createEventTime, setCreateEventTime] = useState('');
  const [createDuration, setCreateDuration] = useState(60);
  const [createFormLoading, setCreateFormLoading] = useState(false);

  const fetchEvents = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await advancedCollaborationService.getStudyGroupEvents(groupId);

      if (response.success && response.data) {
        setEvents(response.data as GroupEvent[]);
      } else {
        setError(response.error || 'Failed to load events');
      }
    } catch (err) {
      setError('An error occurred while loading events');
      console.error('Error fetching group events:', err);
    } finally {
      setLoading(false);
    }
  }, [groupId]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const handleCreateEvent = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!createTitle || !createEventTime) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setCreateFormLoading(true);
      setError(null);

      const response = await advancedCollaborationService.createStudyGroupEvent(
        groupId,
        createTitle,
        {
          description: createDescription,
          eventTime: createEventTime,
          durationMinutes: createDuration
        }
      );

      if (response.success) {
        setSuccessMessage('Event created successfully');
        setShowCreateModal(false);
        setCreateTitle('');
        setCreateDescription('');
        setCreateEventTime('');
        setCreateDuration(60);
        fetchEvents();
      } else {
        setError(response.error || 'Failed to create event');
      }
    } catch (err) {
      setError('An error occurred while creating event');
      console.error('Error creating event:', err);
    } finally {
      setCreateFormLoading(false);
    }
  };

  const handleJoinEvent = async (event: GroupEvent) => {
    try {
      setActionLoading(true);
      setError(null);

      const response = await advancedCollaborationService.joinStudyGroupEvent(
        groupId,
        event.event_id
      );

      if (response.success) {
        setSuccessMessage('Joined event successfully');
        fetchEvents();
        setShowEventModal(false);
      } else {
        setError(response.error || 'Failed to join event');
      }
    } catch (err) {
      setError('An error occurred while joining event');
      console.error('Error joining event:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleLeaveEvent = async (event: GroupEvent) => {
    try {
      setActionLoading(true);
      setError(null);

      const response = await advancedCollaborationService.leaveStudyGroupEvent(
        groupId,
        event.event_id
      );

      if (response.success) {
        setSuccessMessage('Left event successfully');
        fetchEvents();
      } else {
        setError(response.error || 'Failed to leave event');
      }
    } catch (err) {
      setError('An error occurred while leaving event');
      console.error('Error leaving event:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const getUpcomingEvents = () => {
    const now = new Date();
    return events
      .filter(event => new Date(event.event_time) > now)
      .sort((a, b) => new Date(a.event_time).getTime() - new Date(b.event_time).getTime());
  };

  const getPastEvents = () => {
    const now = new Date();
    return events
      .filter(event => new Date(event.event_time) <= now)
      .sort((a, b) => new Date(b.event_time).getTime() - new Date(a.event_time).getTime());
  };

  const formatEventTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDuration = (minutes: number) => {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <LoadingSpinner size={40} className="animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[80vh] overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Calendar className="text-blue-500" size={24} />
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Group Events</h2>
            <p className="text-sm text-gray-500">{groupName}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isAdmin && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              <Plus size={18} />
              Create Event
            </button>
          )}
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X size={20} className="text-gray-500" />
          </button>
        </div>
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

      {/* Events List */}
      <div className="overflow-y-auto max-h-[500px] p-4">
        {getUpcomingEvents().length === 0 && getPastEvents().length === 0 ? (
          <div className="text-center py-8">
            <Calendar size={48} className="mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500">No events scheduled</p>
            {isAdmin && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="mt-4 flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors mx-auto"
              >
                <Plus size={18} />
                Create First Event
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-6">
            {/* Upcoming Events */}
            {getUpcomingEvents().length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
                  Upcoming Events
                </h3>
                <div className="space-y-3">
                  {getUpcomingEvents().map((event) => (
                    <div
                      key={event.event_id}
                      className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all cursor-pointer"
                      onClick={() => {
                        setSelectedEvent(event);
                        setShowEventModal(true);
                      }}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900">{event.title}</h4>
                          <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                            <div className="flex items-center gap-1">
                              <Clock size={14} />
                              {formatEventTime(event.event_time)}
                            </div>
                            <div className="flex items-center gap-1">
                              <Calendar size={14} />
                              {formatDuration(event.duration_minutes)}
                            </div>
                          </div>
                          {event.description && (
                            <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                              {event.description}
                            </p>
                          )}
                        </div>
                        <div className="flex items-center gap-2">
                          {event.is_participating ? (
                            <span className="flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
                              <CheckCircle size={12} />
                              Going
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs">
                              <Users size={12} />
                              {event.participant_count || 0}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Past Events */}
            {getPastEvents().length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
                  Past Events
                </h3>
                <div className="space-y-3">
                  {getPastEvents().slice(0, 5).map((event) => (
                    <div
                      key={event.event_id}
                      className="p-4 border border-gray-100 rounded-lg bg-gray-50 opacity-75"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-700">{event.title}</h4>
                          <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                            <div className="flex items-center gap-1">
                              <Clock size={14} />
                              {formatEventTime(event.event_time)}
                            </div>
                          </div>
                        </div>
                        <span className="text-xs text-gray-400">Completed</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Create Event Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Create New Event</h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X size={20} className="text-gray-500" />
                </button>
              </div>

              <form onSubmit={handleCreateEvent} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Event Title *
                  </label>
                  <input
                    type="text"
                    value={createTitle}
                    onChange={(e) => setCreateTitle(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="e.g., Weekly Study Session"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={createDescription}
                    onChange={(e) => setCreateDescription(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Describe what will be covered..."
                    rows={3}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Date & Time *
                    </label>
                    <input
                      type="datetime-local"
                      value={createEventTime}
                      onChange={(e) => setCreateEventTime(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Duration
                    </label>
                    <select
                      value={createDuration}
                      onChange={(e) => setCreateDuration(Number(e.target.value))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value={30}>30 minutes</option>
                      <option value={60}>1 hour</option>
                      <option value={90}>1.5 hours</option>
                      <option value={120}>2 hours</option>
                      <option value={180}>3 hours</option>
                    </select>
                  </div>
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={createFormLoading}
                    className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
                  >
                    {createFormLoading ? 'Creating...' : 'Create Event'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Event Detail Modal */}
      {showEventModal && selectedEvent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{selectedEvent.title}</h3>
                <button
                  onClick={() => setShowEventModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X size={20} className="text-gray-500" />
                </button>
              </div>

              {selectedEvent.description && (
                <p className="text-gray-600 mb-4">{selectedEvent.description}</p>
              )}

              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-3 py-2 border-b border-gray-100">
                  <Calendar size={18} className="text-blue-500" />
                  <span className="text-gray-700">{formatEventTime(selectedEvent.event_time)}</span>
                </div>
                <div className="flex items-center gap-3 py-2 border-b border-gray-100">
                  <Clock size={18} className="text-blue-500" />
                  <span className="text-gray-700">{formatDuration(selectedEvent.duration_minutes)}</span>
                </div>
                <div className="flex items-center gap-3 py-2 border-b border-gray-100">
                  <Users size={18} className="text-blue-500" />
                  <span className="text-gray-700">{selectedEvent.participant_count || 0} participants</span>
                </div>
                <div className="flex items-center gap-3 py-2">
                  <Video size={18} className="text-blue-500" />
                  <span className="text-gray-700">Online session</span>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-gray-200">
                {selectedEvent.is_participating ? (
                  <button
                    onClick={() => handleLeaveEvent(selectedEvent)}
                    disabled={actionLoading}
                    className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Leave Event
                  </button>
                ) : (
                  <button
                    onClick={() => handleJoinEvent(selectedEvent)}
                    disabled={actionLoading}
                    className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                  >
                    Join Event
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudyGroupEvents;
