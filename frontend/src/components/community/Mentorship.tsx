/**
 * Mentorship Components
 * 
 * Components for mentorship connections, requests, and sessions
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Users,
  Star,
  Clock,
  Award,
  Search,
  Plus,
  ChevronRight,
  Calendar,
  MessageSquare,
  CheckCircle,
  XCircle,
  User,
  RefreshCw,
  Filter,
  Heart,
  Briefcase,
  GraduationCap,
  Code,
  Palette,
  Microscope
} from 'lucide-react';
import advancedCollaborationService, {
  MentorshipProfile,
  MentorshipRequest,
  MentorshipSession
} from '../../services/advancedCollaborationService';

// Props interfaces
interface MentorSearchProps {
  onMentorSelect?: (mentor: MentorshipProfile) => void;
}

interface MentorshipRequestsProps {
  onRequestUpdate?: () => void;
}

interface MentorshipSessionsProps {
  onSessionUpdate?: () => void;
}

interface MentorProfileCardProps {
  mentor: MentorshipProfile;
  onSelect?: () => void;
}

// Mentor Profile Card Component
export const MentorProfileCard: React.FC<MentorProfileCardProps> = ({ mentor, onSelect }) => {
  const getExpertiseIcon = (area: string) => {
    if (area.toLowerCase().includes('programming') || area.toLowerCase().includes('code')) return <Code className="w-3 h-3" />;
    if (area.toLowerCase().includes('design')) return <Palette className="w-3 h-3" />;
    if (area.toLowerCase().includes('science') || area.toLowerCase().includes('research')) return <Microscope className="w-3 h-3" />;
    if (area.toLowerCase().includes('business') || area.toLowerCase().includes('career')) return <Briefcase className="w-3 h-3" />;
    return <GraduationCap className="w-3 h-3" />;
  };

  return (
    <div
      onClick={onSelect}
      className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 hover:shadow-md transition-shadow cursor-pointer"
    >
      <div className="flex items-start gap-4">
        <div className="w-14 h-14 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center text-white text-xl font-bold">
          {mentor.first_name?.charAt(0) || mentor.username?.charAt(0) || '?'}
        </div>
        <div className="flex-1">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-semibold text-gray-900">
                {mentor.first_name && mentor.last_name
                  ? `${mentor.first_name} ${mentor.last_name}`
                  : mentor.username || 'Anonymous'}
              </h3>
              <p className="text-sm text-gray-500">{mentor.title || 'Mentor'}</p>
            </div>
            {mentor.is_available && (
              <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                Available
              </span>
            )}
          </div>

          {/* Rating */}
          <div className="flex items-center gap-2 mt-2">
            <div className="flex items-center">
              {[1, 2, 3, 4, 5].map((star) => (
                <Star
                  key={star}
                  className={`w-4 h-4 ${
                    star <= (mentor.average_rating || 0) ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'
                  }`}
                />
              ))}
            </div>
            <span className="text-sm font-medium text-gray-900">
              {mentor.average_rating?.toFixed(1) || 'N/A'}
            </span>
            <span className="text-sm text-gray-500">
              ({mentor.total_sessions_completed || 0} sessions)
            </span>
          </div>

          {/* Bio */}
          {mentor.bio && (
            <p className="text-sm text-gray-600 mt-2 line-clamp-2">{mentor.bio}</p>
          )}

          {/* Expertise */}
          {mentor.expertise_areas && mentor.expertise_areas.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {mentor.expertise_areas.slice(0, 4).map((area, index) => (
                <span
                  key={index}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-full"
                >
                  {getExpertiseIcon(area)}
                  {area}
                </span>
              ))}
              {mentor.expertise_areas.length > 4 && (
                <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                  +{mentor.expertise_areas.length - 4} more
                </span>
              )}
            </div>
          )}

          {/* Footer */}
          <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-100">
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                {mentor.availability_hours || 'Flexible hours'}
              </span>
              <span className="flex items-center gap-1">
                <Users className="w-4 h-4" />
                {mentor.max_mentees - (mentor.current_mentees_count || 0)} spots left
              </span>
            </div>
            <button className="text-blue-500 hover:text-blue-600">
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Mentor Search Component
export const MentorSearch: React.FC<MentorSearchProps> = ({ onMentorSelect }) => {
  const [mentors, setMentors] = useState<MentorshipProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedExpertise, setSelectedExpertise] = useState<string | undefined>();

  const loadMentors = useCallback(async () => {
    try {
      setLoading(true);
      const result = await advancedCollaborationService.searchMentors(searchQuery, selectedExpertise);
      if (result.success && result.data) {
        setMentors(result.data);
      }
    } catch (error) {
      console.error('Error loading mentors:', error);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, selectedExpertise]);

  useEffect(() => {
    loadMentors();
  }, [loadMentors]);

  const expertiseAreas = [
    'All Areas',
    'Programming',
    'Web Development',
    'Data Science',
    'Machine Learning',
    'Career Development',
    'Design',
    'Research'
  ];

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="animate-pulse space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex items-start space-x-4">
              <div className="rounded-full bg-gray-200 h-14 w-14"></div>
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-1/3 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search and Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name or skill..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="flex gap-2 flex-wrap">
            {expertiseAreas.map((area) => (
              <button
                key={area}
                onClick={() => setSelectedExpertise(area === 'All Areas' ? undefined : area)}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  (area === 'All Areas' && !selectedExpertise) ||
                  (area !== 'All Areas' && selectedExpertise === area)
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {area}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Mentors List */}
      <div className="space-y-4">
        {mentors.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center">
            <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No mentors found matching your criteria</p>
          </div>
        ) : (
          mentors.map((mentor) => (
            <MentorProfileCard
              key={mentor.user_id}
              mentor={mentor}
              onSelect={() => onMentorSelect?.(mentor)}
            />
          ))
        )}
      </div>
    </div>
  );
};

// Mentorship Requests Component
export const MentorshipRequests: React.FC<MentorshipRequestsProps> = ({ onRequestUpdate }) => {
  const [requests, setRequests] = useState<MentorshipRequest[]>([]);
  const [loading, setLoading] = useState(true);

  const loadRequests = useCallback(async () => {
    try {
      setLoading(true);
      const result = await advancedCollaborationService.getMentorshipRequests();
      if (result.success && result.data) {
        setRequests(result.data);
      }
    } catch (error) {
      console.error('Error loading requests:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadRequests();
  }, [loadRequests]);

  const handleAccept = async (requestId: string) => {
    try {
      await advancedCollaborationService.acceptMentorshipRequest(requestId);
      loadRequests();
      onRequestUpdate?.();
    } catch (error) {
      console.error('Error accepting request:', error);
    }
  };

  const handleDecline = async (requestId: string) => {
    try {
      await advancedCollaborationService.declineMentorshipRequest(requestId);
      loadRequests();
    } catch (error) {
      console.error('Error declining request:', error);
    }
  };

  const handleCancel = async (requestId: string) => {
    try {
      await advancedCollaborationService.cancelMentorshipRequest(requestId);
      loadRequests();
    } catch (error) {
      console.error('Error cancelling request:', error);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="animate-pulse space-y-4">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="h-20 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  const pendingRequests = requests.filter((r) => r.status === 'pending');
  const otherRequests = requests.filter((r) => r.status !== 'pending');

  return (
    <div className="space-y-6">
      {/* Pending Requests */}
      {pendingRequests.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="p-4 border-b border-gray-100">
            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
              <Clock className="w-5 h-5 text-yellow-500" />
              Pending Requests
            </h3>
          </div>
          <div className="divide-y divide-gray-100">
            {pendingRequests.map((request) => (
              <div key={request.request_id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                      <User className="w-5 h-5 text-gray-500" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">
                        {request.role === 'mentor' ? `Mentor: ${request.mentor_name}` : `Mentee: ${request.mentee_name}`}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">{request.message || 'No message'}</p>
                      <p className="text-xs text-gray-500 mt-2">
                        {new Date(request.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleAccept(request.request_id)}
                      className="p-2 bg-green-100 text-green-600 rounded-lg hover:bg-green-200"
                      title="Accept"
                    >
                      <CheckCircle className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleDecline(request.request_id)}
                      className="p-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200"
                      title="Decline"
                    >
                      <XCircle className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Other Requests */}
      {otherRequests.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="p-4 border-b border-gray-100">
            <h3 className="font-semibold text-gray-900">Request History</h3>
          </div>
          <div className="divide-y divide-gray-100">
            {otherRequests.map((request) => (
              <div key={request.request_id} className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                    <User className="w-5 h-5 text-gray-500" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">
                      {request.role === 'mentor' ? `Mentor: ${request.mentor_name}` : `Mentee: ${request.mentee_name}`}
                    </p>
                    <p className="text-sm text-gray-500">
                      {new Date(request.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <span
                  className={`px-3 py-1 text-xs font-medium rounded-full ${
                    request.status === 'accepted'
                      ? 'bg-green-100 text-green-700'
                      : request.status === 'rejected'
                      ? 'bg-red-100 text-red-700'
                      : 'bg-gray-100 text-gray-700'
                  }`}
                >
                  {request.status.charAt(0).toUpperCase() + request.status.slice(1)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {requests.length === 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center">
          <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No mentorship requests</p>
        </div>
      )}
    </div>
  );
};

// Main Mentorship Component
const Mentorship: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'find' | 'requests' | 'sessions'>('find');

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="border-b border-gray-200">
          <nav className="flex">
            <button
              onClick={() => setActiveTab('find')}
              className={`flex-1 py-4 px-6 text-center font-medium text-sm transition-colors ${
                activeTab === 'find'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Search className="w-4 h-4 inline-block mr-2" />
              Find Mentors
            </button>
            <button
              onClick={() => setActiveTab('requests')}
              className={`flex-1 py-4 px-6 text-center font-medium text-sm transition-colors ${
                activeTab === 'requests'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Users className="w-4 h-4 inline-block mr-2" />
              Requests
            </button>
            <button
              onClick={() => setActiveTab('sessions')}
              className={`flex-1 py-4 px-6 text-center font-medium text-sm transition-colors ${
                activeTab === 'sessions'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Calendar className="w-4 h-4 inline-block mr-2" />
              Sessions
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'find' && <MentorSearch />}
          {activeTab === 'requests' && <MentorshipRequests />}
          {activeTab === 'sessions' && (
            <div className="text-center py-8">
              <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Sessions feature coming soon!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Mentorship;
