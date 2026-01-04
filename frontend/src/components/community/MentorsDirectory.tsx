import React, { useState, useEffect, useCallback } from 'react';
import {
  Search,
  Filter,
  Star,
  Users,
  Clock,
  BookOpen,
  X,
  CheckCircle,
  AlertCircle,
  LoadingSpinner,
  ChevronDown,
  MessageSquare,
  Award,
  TrendingUp
} from 'lucide-react';
import advancedCollaborationService, {
  MentorshipProfile
} from '../../services/advancedCollaborationService';

interface MentorsDirectoryProps {
  onClose?: () => void;
  onSelectMentor?: (mentor: MentorshipProfile) => void;
}

const MentorsDirectory: React.FC<MentorsDirectoryProps> = ({
  onClose,
  onSelectMentor
}) => {
  const [mentors, setMentors] = useState<MentorshipProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedExpertise, setSelectedExpertise] = useState<string>('all');
  const [selectedAvailability, setSelectedAvailability] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('rating');
  const [selectedMentor, setSelectedMentor] = useState<MentorshipProfile | null>(null);
  const [showMentorModal, setShowMentorModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchMentors = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await advancedCollaborationService.searchMentors();

      if (response.success && response.data) {
        setMentors(response.data as MentorshipProfile[]);
      } else {
        setError(response.error || 'Failed to load mentors');
      }
    } catch (err) {
      setError('An error occurred while loading mentors');
      console.error('Error fetching mentors:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMentors();
  }, [fetchMentors]);

  const allExpertiseAreas = React.useMemo(() => {
    const areas = new Set<string>();
    mentors.forEach(mentor => {
      mentor.expertise_areas?.forEach(area => areas.add(area));
    });
    return Array.from(areas).sort();
  }, [mentors]);

  const handleRequestMentorship = async (mentor: MentorshipProfile) => {
    try {
      setActionLoading(true);
      setError(null);

      const response = await advancedCollaborationService.requestMentorship(
        mentor.user_id,
        'General inquiry'
      );

      if (response.success) {
        setSuccessMessage('Mentorship request sent successfully!');
        setShowMentorModal(false);
      } else {
        setError(response.error || 'Failed to send request');
      }
    } catch (err) {
      setError('An error occurred while sending request');
      console.error('Error requesting mentorship:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const filteredMentors = mentors.filter(mentor => {
    const matchesSearch = !searchQuery ||
      mentor.username?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      mentor.first_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      mentor.last_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      mentor.bio?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      mentor.expertise_areas?.some(area =>
        area.toLowerCase().includes(searchQuery.toLowerCase())
      );

    const matchesExpertise = selectedExpertise === 'all' ||
      mentor.expertise_areas?.includes(selectedExpertise);

    const matchesAvailability = selectedAvailability === 'all' ||
      (selectedAvailability === 'available' && mentor.is_available) ||
      (selectedAvailability === 'full' && !mentor.is_available);

    return matchesSearch && matchesExpertise && matchesAvailability;
  });

  const sortedMentors = [...filteredMentors].sort((a, b) => {
    switch (sortBy) {
      case 'rating':
        return (b.average_rating || 0) - (a.average_rating || 0);
      case 'experience':
        return (b.years_experience || 0) - (a.years_experience || 0);
      case 'sessions':
        return (b.total_sessions_completed || 0) - (a.total_sessions_completed || 0);
      case 'mentees':
        return (b.current_mentees_count || 0) - (a.current_mentees_count || 0);
      default:
        return 0;
    }
  });

  const getAvailabilityBadge = (mentor: MentorshipProfile) => {
    if (mentor.is_available) {
      return mentor.current_mentees_count < mentor.max_mentees ? (
        <span className="flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
          <CheckCircle size={12} />
          Available
        </span>
      ) : (
        <span className="flex items-center gap-1 px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs">
          <Clock size={12} />
          Limited
        </span>
      );
    }
    return (
      <span className="flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs">
        <X size={12} />
        Unavailable
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <LoadingSpinner size={40} className="animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg max-w-4xl w-full max-h-[80vh] overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Users className="text-blue-500" size={24} />
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Find a Mentor</h2>
            <p className="text-sm text-gray-500">Browse experienced mentors in your field</p>
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
          <div className="flex-1 min-w-[250px] relative">
            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search by name, expertise, or bio..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <select
            value={selectedExpertise}
            onChange={(e) => setSelectedExpertise(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Expertise</option>
            {allExpertiseAreas.map(area => (
              <option key={area} value={area}>{area}</option>
            ))}
          </select>
          <select
            value={selectedAvailability}
            onChange={(e) => setSelectedAvailability(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">Any Availability</option>
            <option value="available">Available</option>
            <option value="full">Limited Spots</option>
          </select>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="rating">Highest Rated</option>
            <option value="experience">Most Experience</option>
            <option value="sessions">Most Sessions</option>
            <option value="mentees">Most Mentees</option>
          </select>
        </div>
      </div>

      {/* Mentors Grid */}
      <div className="overflow-y-auto max-h-[500px] p-4">
        {sortedMentors.length === 0 ? (
          <div className="text-center py-8">
            <Users size={48} className="mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500">No mentors found matching your criteria</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {sortedMentors.map((mentor) => (
              <div
                key={mentor.user_id}
                className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all cursor-pointer"
                onClick={() => {
                  setSelectedMentor(mentor);
                  setShowMentorModal(true);
                }}
              >
                <div className="flex items-start gap-4">
                  <div className="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                    {mentor.avatar_url ? (
                      <img
                        src={mentor.avatar_url}
                        alt={mentor.username}
                        className="w-full h-full rounded-full object-cover"
                      />
                    ) : (
                      <Users className="text-blue-500" size={28} />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-gray-900 truncate">
                        {mentor.first_name && mentor.last_name
                          ? `${mentor.first_name} ${mentor.last_name}`
                          : mentor.username || 'Unknown Mentor'}
                      </h3>
                      {getAvailabilityBadge(mentor)}
                    </div>
                    <p className="text-sm text-gray-500 mb-2">@{mentor.username}</p>

                    {mentor.bio && (
                      <p className="text-sm text-gray-600 line-clamp-2 mb-3">{mentor.bio}</p>
                    )}

                    <div className="flex flex-wrap gap-2 mb-3">
                      {mentor.expertise_areas?.slice(0, 3).map((area, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs"
                        >
                          {area}
                        </span>
                      ))}
                      {mentor.expertise_areas && mentor.expertise_areas.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
                          +{mentor.expertise_areas.length - 3}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <Star size={14} className="text-yellow-500" fill="currentColor" />
                        {mentor.average_rating?.toFixed(1) || 'N/A'}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock size={14} />
                        {mentor.years_experience || 0} years
                      </span>
                      <span className="flex items-center gap-1">
                        <Users size={14} />
                        {mentor.total_sessions_completed || 0} sessions
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Mentor Detail Modal */}
      {showMentorModal && selectedMentor && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                    {selectedMentor.avatar_url ? (
                      <img
                        src={selectedMentor.avatar_url}
                        alt={selectedMentor.username}
                        className="w-full h-full rounded-full object-cover"
                      />
                    ) : (
                      <Users className="text-blue-500" size={32} />
                    )}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {selectedMentor.first_name && selectedMentor.last_name
                        ? `${selectedMentor.first_name} ${selectedMentor.last_name}`
                        : selectedMentor.username || 'Unknown Mentor'}
                    </h3>
                    <p className="text-gray-500">@{selectedMentor.username}</p>
                    {getAvailabilityBadge(selectedMentor)}
                  </div>
                </div>
                <button
                  onClick={() => setShowMentorModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X size={20} className="text-gray-500" />
                </button>
              </div>

              {selectedMentor.bio && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">About</h4>
                  <p className="text-gray-600">{selectedMentor.bio}</p>
                </div>
              )}

              <div className="space-y-3 text-sm">
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-500">Expertise</span>
                  <span className="text-gray-900 text-right">
                    {selectedMentor.expertise_areas?.join(', ') || 'Not specified'}
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-500">Experience</span>
                  <span className="text-gray-900">{selectedMentor.years_experience || 0} years</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-500">Teaching Style</span>
                  <span className="text-gray-900">{selectedMentor.teaching_style || 'Not specified'}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-500">Availability</span>
                  <span className="text-gray-900">{selectedMentor.availability_hours || 'Not specified'}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-500">Sessions Completed</span>
                  <span className="text-gray-900">{selectedMentor.total_sessions_completed || 0}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-500">Current Mentees</span>
                  <span className="text-gray-900">
                    {selectedMentor.current_mentees_count || 0} / {selectedMentor.max_mentees || 3}
                  </span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-gray-500">Rating</span>
                  <span className="text-gray-900 flex items-center gap-1">
                    <Star size={14} className="text-yellow-500" fill="currentColor" />
                    {selectedMentor.average_rating?.toFixed(1) || 'N/A'}
                  </span>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-gray-200 space-y-2">
                <button
                  onClick={() => handleRequestMentorship(selectedMentor)}
                  disabled={actionLoading || !selectedMentor.is_available}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
                >
                  <MessageSquare size={18} />
                  {actionLoading ? 'Sending...' : 'Request Mentorship'}
                </button>
                <button
                  onClick={() => {
                    onSelectMentor?.(selectedMentor);
                    setShowMentorModal(false);
                  }}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <MessageSquare size={18} />
                  Send Message
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MentorsDirectory;
