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
import MentorsDirectory from './MentorsDirectory';
import MentorshipRequests from './MentorshipRequests';
import MentorRequestsReceived from './MentorRequestsReceived';

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

// Main Mentorship Component
const Mentorship: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'directory' | 'my_requests' | 'requests_received' | 'sessions'>('directory');

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="border-b border-gray-200">
          <nav className="flex">
            <button
              onClick={() => setActiveTab('directory')}
              className={`flex-1 py-4 px-6 text-center font-medium text-sm transition-colors ${
                activeTab === 'directory'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Search className="w-4 h-4 inline-block mr-2" />
              Find Mentors
            </button>
            <button
              onClick={() => setActiveTab('my_requests')}
              className={`flex-1 py-4 px-6 text-center font-medium text-sm transition-colors ${
                activeTab === 'my_requests'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Users className="w-4 h-4 inline-block mr-2" />
              My Requests
            </button>
            <button
              onClick={() => setActiveTab('requests_received')}
              className={`flex-1 py-4 px-6 text-center font-medium text-sm transition-colors ${
                activeTab === 'requests_received'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Users className="w-4 h-4 inline-block mr-2" />
              Requests Received
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
          {activeTab === 'directory' && <MentorsDirectory />}
          {activeTab === 'my_requests' && <MentorshipRequests />}
          {activeTab === 'requests_received' && <MentorRequestsReceived />}
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
