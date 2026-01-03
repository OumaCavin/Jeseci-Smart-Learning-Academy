import React, { useState, useEffect, useCallback } from 'react';
import { Activity, ActivityFilter, activityService } from '../../services/activityService';
import RecentActivityCard from './RecentActivityCard';
import { RefreshCw } from 'lucide-react';

interface RecentActivityFeedProps {
  userId: string;
  limit?: number;
  filter?: ActivityFilter;
  showHeader?: boolean;
  showLoadMore?: boolean;
  compact?: boolean;
  autoRefresh?: boolean;
  refreshInterval?: number;
  onActivityClick?: (activity: Activity) => void;
}

const RecentActivityFeed: React.FC<RecentActivityFeedProps> = ({
  userId,
  limit = 10,
  filter,
  showHeader = true,
  showLoadMore = true,
  compact = false,
  autoRefresh = false,
  refreshInterval = 30000,
  onActivityClick,
}) => {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchActivities = useCallback(async (pageNum: number, isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    setError(null);

    try {
      const response = await activityService.getActivities(userId || '', {
        limit,
        offset: (pageNum - 1) * limit,
        activityType: filter?.activityType || '',
      });

      if (isRefresh || pageNum === 1) {
        setActivities(response.activities);
      } else {
        setActivities((prev) => [...prev, ...response.activities]);
      }

      setHasMore(response.activities.length === limit);
      setPage(pageNum);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load activities');
      console.error('Error fetching activities:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [limit, filter]);

  useEffect(() => {
    fetchActivities(1);

    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchActivities(1, true);
      }, refreshInterval);

      return () => clearInterval(interval);
    }
  }, [fetchActivities, autoRefresh, refreshInterval]);

  const handleLoadMore = () => {
    if (!loading && hasMore) {
      fetchActivities(page + 1);
    }
  };

  const handleRefresh = () => {
    fetchActivities(1, true);
  };

  const getEmptyState = () => {
    if (filter?.activityType) {
      return {
        title: 'No Activities Found',
        description: `You haven't performed any "${filter.activityType.replace(/_/g, ' ')}" activities yet.`,
      };
    }

    return {
      title: 'No Recent Activities',
      description: 'Start learning to see your activities here!',
    };
  };

  const emptyState = getEmptyState();

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      {showHeader && (
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-gray-900">Recent Activity</h3>
            {error && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                Error
              </span>
            )}
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="inline-flex items-center gap-1 px-2 py-1 text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50"
            aria-label="Refresh activities"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      )}

      <div className="divide-y divide-gray-50">
        {loading && activities.length === 0 ? (
          <div className="p-4 space-y-3">
            {Array.from({ length: limit }).map((_, index) => (
              <RecentActivityCardSkeleton key={index} compact={compact} />
            ))}
          </div>
        ) : error && activities.length === 0 ? (
          <div className="p-8 text-center">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-red-100 mb-3">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h4 className="font-medium text-gray-900 mb-1">{emptyState.title}</h4>
            <p className="text-sm text-gray-600 mb-3">{emptyState.description}</p>
            <button
              onClick={handleRefresh}
              className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
            >
              Try Again
            </button>
          </div>
        ) : activities.length === 0 ? (
          <div className="p-8 text-center">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gray-100 mb-3">
              <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <h4 className="font-medium text-gray-900 mb-1">{emptyState.title}</h4>
            <p className="text-sm text-gray-600">{emptyState.description}</p>
          </div>
        ) : (
          <>
            <div className={`${compact ? 'p-2' : 'p-3'} space-y-1`}>
              {activities.map((activity) => (
                <RecentActivityCard
                  key={activity.id}
                  activity={activity}
                  onClick={onActivityClick}
                  showTimestamp={!compact}
                  compact={compact}
                />
              ))}
            </div>

            {showLoadMore && hasMore && (
              <div className="px-4 py-3 border-t border-gray-100">
                <button
                  onClick={handleLoadMore}
                  disabled={loading}
                  className="w-full py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Loading...' : 'Load More'}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

interface RecentActivityCardSkeletonProps {
  compact?: boolean;
}

const RecentActivityCardSkeleton: React.FC<RecentActivityCardSkeletonProps> = ({ compact = false }) => {
  return (
    <div className={`flex items-start gap-3 ${compact ? 'py-2' : 'py-3'}`}>
      <div className="w-10 h-10 bg-gray-200 rounded-full animate-pulse flex-shrink-0" />

      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <div className="h-4 bg-gray-200 rounded animate-pulse w-1/3 mb-2" />
            {!compact && (
              <div className="h-3 bg-gray-200 rounded animate-pulse w-2/3" />
            )}
          </div>

          <div className="flex flex-col items-end gap-1 flex-shrink-0">
            <div className="h-5 bg-gray-200 rounded-full w-16 animate-pulse" />
            <div className="h-3 bg-gray-200 rounded animate-pulse w-12" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecentActivityFeed;
