import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useWebSocket, WebSocketMessage } from '../../hooks/useWebSocket';

// Types for activity feed
export interface ActivityItem {
  id: string;
  type: 'execution' | 'user' | 'sync' | 'error' | 'deployment' | 'system' | 'collaboration';
  title: string;
  description: string;
  timestamp: string;
  userId?: string;
  userName?: string;
  userAvatar?: string;
  status?: 'success' | 'pending' | 'error' | 'warning';
  metadata?: Record<string, unknown>;
  priority?: 'low' | 'medium' | 'high';
}

interface LiveActivityFeedProps {
  maxItems?: number;
  autoRefresh?: boolean;
  filterByType?: ActivityItem['type'][];
  onItemClick?: (item: ActivityItem) => void;
  showTimestamps?: boolean;
  compactMode?: boolean;
}

// Icons for different activity types
const ActivityIcons: Record<ActivityItem['type'], React.ReactNode> = {
  execution: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
            d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
    </svg>
  ),
  user: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
    </svg>
  ),
  sync: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
    </svg>
  ),
  error: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  deployment: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
    </svg>
  ),
  system: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  ),
  collaboration: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
            d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
    </svg>
  )
};

const ActivityColors: Record<ActivityItem['type'], string> = {
  execution: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
  user: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400',
  sync: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400',
  error: 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400',
  deployment: 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400',
  system: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400',
  collaboration: 'bg-teal-100 text-teal-600 dark:bg-teal-900/30 dark:text-teal-400'
};

const StatusColors: Record<ActivityItem['status'] | 'default', string> = {
  success: 'text-green-500',
  pending: 'text-yellow-500',
  error: 'text-red-500',
  warning: 'text-orange-500',
  default: 'text-gray-400'
};

export function LiveActivityFeed({
  maxItems = 50,
  autoRefresh = true,
  filterByType,
  onItemClick,
  showTimestamps = true,
  compactMode = false
}: LiveActivityFeedProps) {
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<ActivityItem['type'] | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isPaused, setIsPaused] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  const { isConnected, lastMessage, reconnect } = useWebSocket({
    url: '/ws/activities',
    autoConnect: autoRefresh,
    onMessage: useCallback((message: WebSocketMessage) => {
      if (message.type === 'notification' || message.type === 'sync.progress') {
        const newActivity = message.payload as ActivityItem;
        addActivity(newActivity);
      }
    }, [])
  });

  // Add new activity
  const addActivity = useCallback((activity: ActivityItem) => {
    if (isPaused) return;
    
    setActivities(prev => {
      const updated = [activity, ...prev];
      if (maxItems) {
        return updated.slice(0, maxItems);
      }
      return updated;
    });
  }, [isPaused, maxItems]);

  // Fetch initial activities
  const fetchActivities = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/activities?limit=50');
      if (response.ok) {
        const data = await response.json();
        // Ensure we set an array even if the API returns an error response
        if (data.success && Array.isArray(data.activities)) {
          setActivities(data.activities);
        } else {
          console.error('Failed to fetch activities:', data.error || 'Unknown error');
          setActivities([]);
        }
      } else {
        console.error('Failed to fetch activities: HTTP', response.status);
        setActivities([]);
      }
    } catch (error) {
      console.error('Failed to fetch activities:', error);
      setActivities([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchActivities();
  }, [fetchActivities]);

  // Filter activities
  const filteredActivities = activities.filter(activity => {
    // Type filter
    if (filter !== 'all' && activity.type !== filter) return false;
    
    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        activity.title.toLowerCase().includes(query) ||
        activity.description.toLowerCase().includes(query) ||
        activity.userName?.toLowerCase().includes(query)
      );
    }
    
    return true;
  });

  // Group activities by date
  const groupedActivities = filteredActivities.reduce((groups, activity) => {
    const date = new Date(activity.timestamp).toLocaleDateString();
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(activity);
    return groups;
  }, {} as Record<string, ActivityItem[]>);

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  // Get priority indicator
  const getPriorityIndicator = (priority?: ActivityItem['priority']) => {
    if (!priority || priority === 'low') return null;
    
    const colors = {
      medium: 'bg-yellow-400',
      high: 'bg-red-500'
    };
    
    return (
      <div className={`w-1.5 h-1.5 rounded-full ${colors[priority]}`} />
    );
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 
                   dark:border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">
              Activity Feed
            </h3>
            <div className="flex items-center gap-1.5">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'} 
                            ${isPaused ? 'animate-pulse' : ''}`} />
              <span className="text-xs text-gray-500">
                {isPaused ? 'Paused' : isConnected ? 'Live' : 'Disconnected'}
              </span>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {/* Pause/Resume button */}
            <button
              onClick={() => setIsPaused(!isPaused)}
              className={`p-1.5 rounded-lg transition-colors ${
                isPaused 
                  ? 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400'
                  : 'text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
              title={isPaused ? 'Resume' : 'Pause'}
            >
              {isPaused ? (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
            </button>

            {/* Reconnect button */}
            {!isConnected && (
              <button
                onClick={reconnect}
                className="p-1.5 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 
                         rounded-lg transition-colors"
                title="Reconnect"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
            )}
          </div>
        </div>

        {/* Search and filter */}
        <div className="flex items-center gap-3 mt-3">
          <div className="relative flex-1">
            <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" 
                 fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="Search activities..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 text-sm border border-gray-200 dark:border-gray-600 
                       rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-gray-100
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as ActivityItem['type'] | 'all')}
            className="px-3 py-2 text-sm border border-gray-200 dark:border-gray-600 rounded-lg
                     bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-gray-100
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Types</option>
            <option value="execution">Executions</option>
            <option value="user">Users</option>
            <option value="sync">Syncs</option>
            <option value="error">Errors</option>
            <option value="deployment">Deployments</option>
            <option value="system">System</option>
            <option value="collaboration">Collaboration</option>
          </select>
        </div>
      </div>

      {/* Activity list */}
      <div 
        ref={listRef}
        className="overflow-auto" 
        style={{ maxHeight: compactMode ? '300px' : '500px' }}
      >
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        ) : filteredActivities.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-gray-500">
            <svg className="w-12 h-12 mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p>No activities found</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100 dark:divide-gray-700">
            {Object.entries(groupedActivities).map(([date, dateActivities]) => (
              <div key={date}>
                {/* Date header */}
                <div className="px-4 py-2 bg-gray-50 dark:bg-gray-750 text-xs font-medium 
                              text-gray-500 sticky top-0">
                  {date === new Date().toLocaleDateString() ? 'Today' : date}
                </div>
                
                {dateActivities.map((activity) => (
                  <div
                    key={activity.id}
                    onClick={() => onItemClick?.(activity)}
                    className={`flex items-start gap-3 px-4 py-3 hover:bg-gray-50 
                             dark:hover:bg-gray-700/50 transition-colors cursor-pointer
                             ${compactMode ? 'py-2' : ''}`}
                  >
                    {/* Icon */}
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center 
                                   justify-center ${ActivityColors[activity.type]}`}>
                      {ActivityIcons[activity.type]}
                    </div>
                    
                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        {getPriorityIndicator(activity.priority)}
                        <span className="font-medium text-gray-900 dark:text-gray-100 truncate">
                          {activity.title}
                        </span>
                        {activity.status && (
                          <div className={`w-2 h-2 rounded-full ${StatusColors[activity.status]}`} />
                        )}
                      </div>
                      
                      {!compactMode && (
                        <p className="text-sm text-gray-500 truncate mt-0.5">
                          {activity.description}
                        </p>
                      )}
                      
                      {/* Meta info */}
                      <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
                        {activity.userName && (
                          <span className="flex items-center gap-1">
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                            {activity.userName}
                          </span>
                        )}
                        
                        {showTimestamps && (
                          <span>{formatTimestamp(activity.timestamp)}</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-2 border-t border-gray-100 dark:border-gray-700 
                    bg-gray-50 dark:bg-gray-750 text-xs text-gray-500 flex items-center justify-between">
        <span>{filteredActivities.length} activities</span>
        <button className="text-blue-600 hover:text-blue-700 dark:text-blue-400">
          View All
        </button>
      </div>
    </div>
  );
}

