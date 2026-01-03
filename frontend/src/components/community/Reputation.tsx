/**
 * Reputation Components
 * 
 * Components for displaying user reputation, leaderboard, and upvoting
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Trophy,
  Star,
  TrendingUp,
  ThumbsUp,
  Award,
  Medal,
  Crown,
  Target,
  Activity,
  RefreshCw,
  ChevronRight,
  User
} from 'lucide-react';
import advancedCollaborationService, { UserReputation, LeaderboardEntry } from '../../services/advancedCollaborationService';

// Props interface
interface ReputationCardProps {
  reputation?: UserReputation;
}

interface LeaderboardProps {
  limit?: number;
}

interface UpvoteButtonProps {
  contentId: string;
  contentType: string;
  initialVote?: 1 | -1 | 0;
  onVoteChange?: (vote: number) => void;
}

// Reputation Card Component
export const ReputationCard: React.FC<ReputationCardProps> = ({ reputation }) => {
  const [currentReputation, setCurrentReputation] = useState<UserReputation | undefined>(reputation);
  const [loading, setLoading] = useState(!reputation);

  const loadReputation = useCallback(async () => {
    try {
      setLoading(true);
      const result = await advancedCollaborationService.getUserReputation();
      if (result.success && result.data) {
        setCurrentReputation(result.data);
      }
    } catch (error) {
      console.error('Error loading reputation:', error);
    } finally {
      setLoading(false);
    }
  }, [reputation]);

  useEffect(() => {
    if (!reputation) {
      loadReputation();
    }
  }, [reputation, loadReputation]);

  const getLevelColor = (level: number) => {
    if (level >= 10) return '#FFD700'; // Gold
    if (level >= 7) return '#C0C0C0'; // Silver
    if (level >= 4) return '#CD7F32'; // Bronze
    return '#4CAF50'; // Green
  };

  const getLevelIcon = (level: number) => {
    if (level >= 10) return <Crown className="w-6 h-6 text-yellow-500" />;
    if (level >= 7) return <Medal className="w-6 h-6 text-gray-400" />;
    if (level >= 4) return <Medal className="w-6 h-6 text-orange-500" />;
    return <Award className="w-6 h-6 text-green-500" />;
  };

  const getNextLevelProgress = () => {
    if (!currentReputation) return 0;
    const currentLevel = currentReputation.level;
    const expForCurrentLevel = currentLevel * 100;
    const expForNextLevel = (currentLevel + 1) * 100;
    const progress = ((currentReputation.total_reputation - expForCurrentLevel) / (expForNextLevel - expForCurrentLevel)) * 100;
    return Math.min(Math.max(progress, 0), 100);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="animate-pulse flex items-center space-x-4">
          <div className="rounded-full bg-gray-200 h-16 w-16"></div>
          <div className="flex-1">
            <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
            <div className="h-6 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div
            className="w-16 h-16 rounded-full flex items-center justify-center"
            style={{ backgroundColor: `${getLevelColor(currentReputation?.level || 0)}20` }}
          >
            {getLevelIcon(currentReputation?.level || 0)}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-semibold text-gray-900">Level {currentReputation?.level || 0}</h3>
              <span className="px-2 py-0.5 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                {currentReputation?.rank || 'Newcomer'}
              </span>
            </div>
            <p className="text-gray-600">
              <span className="font-bold text-2xl">{currentReputation?.total_reputation || 0}</span> reputation points
            </p>
          </div>
        </div>

        <div className="text-right">
          <div className="flex items-center space-x-1 text-yellow-500">
            <TrendingUp className="w-4 h-4" />
            <span className="font-medium">+{currentReputation?.reputation_change || 0}</span>
          </div>
          <p className="text-sm text-gray-500">this week</p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mt-4">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Progress to Level {(currentReputation?.level || 0) + 1}</span>
          <span>{Math.round(getNextLevelProgress())}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="h-2 rounded-full transition-all duration-300"
            style={{
              width: `${getNextLevelProgress()}%`,
              backgroundColor: getLevelColor(currentReputation?.level || 0)
            }}
          ></div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mt-6">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <p className="text-2xl font-bold text-gray-900">{currentReputation?.total_upvotes || 0}</p>
          <p className="text-sm text-gray-500">Upvotes Given</p>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <p className="text-2xl font-bold text-gray-900">{currentReputation?.helpful_count || 0}</p>
          <p className="text-sm text-gray-500">Helpful Marks</p>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <p className="text-2xl font-bold text-gray-900">{currentReputation?.streak_days || 0}</p>
          <p className="text-sm text-gray-500">Day Streak</p>
        </div>
      </div>
    </div>
  );
};

// Leaderboard Component
export const Leaderboard: React.FC<LeaderboardProps> = ({ limit = 10 }) => {
  const [entries, setEntries] = useState<UserReputation[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<'week' | 'month' | 'all'>('week');

  const loadLeaderboard = useCallback(async () => {
    try {
      setLoading(true);
      const result = await advancedCollaborationService.getLeaderboard(limit, timeRange);
      if (result.success && result.data) {
        setEntries(result.data);
      }
    } catch (error) {
      console.error('Error loading leaderboard:', error);
    } finally {
      setLoading(false);
    }
  }, [limit, timeRange]);

  useEffect(() => {
    loadLeaderboard();
  }, [loadLeaderboard]);

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Crown className="w-5 h-5 text-yellow-500" />;
    if (rank === 2) return <Medal className="w-5 h-5 text-gray-400" />;
    if (rank === 3) return <Medal className="w-5 h-5 text-orange-500" />;
    return <span className="text-gray-500 font-medium w-5 text-center">{rank}</span>;
  };

  const getRankStyle = (rank: number) => {
    if (rank === 1) return 'bg-yellow-50 border-yellow-200';
    if (rank === 2) return 'bg-gray-50 border-gray-200';
    if (rank === 3) return 'bg-orange-50 border-orange-200';
    return 'bg-white border-gray-100';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="animate-pulse space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex items-center space-x-4">
              <div className="rounded-full bg-gray-200 h-10 w-10"></div>
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-1/3 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/4"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Trophy className="w-5 h-5 text-yellow-500" />
            Top Contributors
          </h3>
          <div className="flex space-x-1">
            {(['week', 'month', 'all'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                  timeRange === range
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {range === 'week' ? 'This Week' : range === 'month' ? 'This Month' : 'All Time'}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="divide-y divide-gray-100">
        {entries.map((entry, index) => (
          <div
            key={entry.user_id}
            className={`p-4 flex items-center justify-between ${getRankStyle(entry.rank)}`}
          >
            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0 w-8 flex justify-center">
                {getRankIcon(entry.rank)}
              </div>
              <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center text-white font-medium">
                {entry.username?.charAt(0).toUpperCase() || '?'}
              </div>
              <div>
                <p className="font-medium text-gray-900">{entry.username}</p>
                <p className="text-sm text-gray-500">Level {entry.level} • {entry.rank}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="font-bold text-gray-900">{entry.total_reputation}</p>
                <p className="text-sm text-gray-500">points</p>
              </div>
              <ChevronRight className="w-5 h-5 text-gray-400" />
            </div>
          </div>
        ))}
      </div>

      {entries.length === 0 && (
        <div className="p-8 text-center">
          <Trophy className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No rankings available yet</p>
        </div>
      )}
    </div>
  );
};

// Upvote Button Component
export const UpvoteButton: React.FC<UpvoteButtonProps> = ({
  contentId,
  contentType,
  initialVote = 0,
  onVoteChange
}) => {
  const [vote, setVote] = useState<1 | -1 | 0>(initialVote);
  const [loading, setLoading] = useState(false);

  const handleVote = async (newVote: 1 | -1 | 0) => {
    if (loading) return;

    try {
      setLoading(true);
      const result = await advancedCollaborationService.voteContent(contentId, contentType, newVote);
      if (result.success) {
        setVote(newVote);
        onVoteChange?.(newVote);
      }
    } catch (error) {
      console.error('Error voting:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center space-x-2">
      <button
        onClick={() => handleVote(vote === 1 ? 0 : 1)}
        disabled={loading}
        className={`flex items-center space-x-1 px-3 py-1 rounded-full transition-colors ${
          vote === 1
            ? 'bg-green-100 text-green-700'
            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
        }`}
      >
        <ThumbsUp className={`w-4 h-4 ${vote === 1 ? 'fill-current' : ''}`} />
        <span className="text-sm font-medium">Helpful</span>
      </button>
    </div>
  );
};

// Main Reputation Component (combines all features)
const Reputation: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'leaderboard' | 'achievements'>('overview');

  return (
    <div className="space-y-6">
      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <>
          <ReputationCard />
          <Leaderboard limit={10} />
        </>
      )}

      {/* Leaderboard Tab */}
      {activeTab === 'leaderboard' && (
        <Leaderboard limit={50} />
      )}

      {/* Achievements Tab */}
      {activeTab === 'achievements' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Award className="w-5 h-5 text-yellow-500" />
            Achievements
          </h3>
          <p className="text-gray-600">Achievements feature coming soon!</p>
        </div>
      )}
    </div>
  );
};

export default Reputation;
