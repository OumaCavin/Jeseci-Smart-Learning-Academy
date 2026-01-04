import React, { useState, useCallback, useEffect } from 'react';
import { useWebSocket, WebSocketMessage } from '../../hooks/useWebSocket';

// Types for metrics
export interface MetricDataPoint {
  timestamp: string;
  value: number;
}

export interface MetricCard {
  id: string;
  title: string;
  value: number;
  unit?: string;
  change?: number;
  changeLabel?: string;
  trend?: 'up' | 'down' | 'stable';
  icon?: React.ReactNode;
  color?: string;
}

export interface RealTimeMetrics {
  activeUsers: MetricCard;
  executionsToday: MetricCard;
  avgExecutionTime: MetricCard;
  successRate: MetricCard;
  queuedTasks: MetricCard;
  systemLoad: MetricCard;
}

// Icons
const UsersIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
          d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
  </svg>
);

const CodeIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
          d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
  </svg>
);

const ClockIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const CheckCircleIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const QueueIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
          d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
  </svg>
);

const CpuIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
          d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
  </svg>
);

const RefreshIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
          d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
  </svg>
);

interface MetricCardProps {
  metric: MetricCard;
  onClick?: () => void;
}

function MetricCardComponent({ metric, onClick }: MetricCardProps) {
  const trendColors = {
    up: 'text-green-500',
    down: 'text-red-500',
    stable: 'text-gray-500'
  };

  const trendIcons = {
    up: '↑',
    down: '↓',
    stable: '→'
  };

  return (
    <div 
      onClick={onClick}
      className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 
               dark:border-gray-700 hover:shadow-md transition-shadow cursor-pointer"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
            {metric.title}
          </p>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-3xl font-bold text-gray-900 dark:text-gray-100">
              {metric.value.toLocaleString()}
            </span>
            {metric.unit && (
              <span className="text-sm text-gray-500">{metric.unit}</span>
            )}
          </div>
          {metric.change !== undefined && (
            <div className={`flex items-center gap-1 mt-2 text-sm ${trendColors[metric.trend || 'stable']}`}>
              <span>{trendIcons[metric.trend || 'stable']}</span>
              <span>{Math.abs(metric.change)}%</span>
              {metric.changeLabel && (
                <span className="text-gray-500">{metric.changeLabel}</span>
              )}
            </div>
          )}
        </div>
        {metric.icon && (
          <div className={`p-3 rounded-lg ${metric.color || 'bg-blue-100 text-blue-600'}`}>
            {metric.icon}
          </div>
        )}
      </div>
    </div>
  );
}

interface RealTimeMetricsGridProps {
  refreshInterval?: number;
  onMetricClick?: (metricId: string) => void;
  initialMetrics?: RealTimeMetrics;
}

export function RealTimeMetricsGrid({
  refreshInterval = 5000,
  onMetricClick,
  initialMetrics
}: RealTimeMetricsGridProps) {
  const [metrics, setMetrics] = useState<RealTimeMetrics>(initialMetrics || getDefaultMetrics());
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [history, setHistory] = useState<Record<string, MetricDataPoint[]>>({});

  const { isConnected, lastMessage, reconnect } = useWebSocket({
    url: '/ws/dashboard',
    autoConnect: true,
    onMessage: useCallback((message: WebSocketMessage) => {
      if (message.type === 'dashboard.metric') {
        handleMetricUpdate(message.payload);
      }
    }, [])
  });

  // Handle metric update from WebSocket
  const handleMetricUpdate = useCallback((update: { metricId: string; value: number; timestamp: string }) => {
    setMetrics(prev => ({
      ...prev,
      [update.metricId]: {
        ...prev[update.metricId as keyof RealTimeMetrics],
        value: update.value
      }
    }));

    // Add to history
    setHistory(prev => ({
      ...prev,
      [update.metricId]: [
        ...(prev[update.metricId] || []).slice(-59),
        { timestamp: update.timestamp, value: update.value }
      ]
    }));

    setLastUpdate(new Date());
  }, []);

  // Fetch metrics from API
  const fetchMetrics = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/dashboard/metrics');
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
        setLastUpdate(new Date());
      }
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initial fetch and polling
  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchMetrics, refreshInterval]);

  // Update trends based on history
  const getMetricWithTrend = (metricId: string, currentValue: number): MetricCard => {
    const metric = metrics[metricId as keyof RealTimeMetrics];
    const metricHistory = history[metricId] || [];
    
    if (metricHistory.length < 2) {
      return metric;
    }

    const previousValue = metricHistory[metricHistory.length - 2]?.value || metric.value;
    const change = currentValue - previousValue;
    const percentChange = previousValue !== 0 ? (change / previousValue) * 100 : 0;

    return {
      ...metric,
      change: Math.round(percentChange * 10) / 10,
      trend: percentChange > 1 ? 'up' : percentChange < -1 ? 'down' : 'stable'
    };
  };

  const displayMetrics = {
    activeUsers: getMetricWithTrend('activeUsers', metrics.activeUsers.value),
    executionsToday: getMetricWithTrend('executionsToday', metrics.executionsToday.value),
    avgExecutionTime: getMetricWithTrend('avgExecutionTime', metrics.avgExecutionTime.value),
    successRate: getMetricWithTrend('successRate', metrics.successRate.value),
    queuedTasks: getMetricWithTrend('queuedTasks', metrics.queuedTasks.value),
    systemLoad: getMetricWithTrend('systemLoad', metrics.systemLoad.value)
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Real-Time Metrics
          </h2>
          <p className="text-sm text-gray-500">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          {/* Connection status */}
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-sm text-gray-500">
              {isConnected ? 'Live' : 'Disconnected'}
            </span>
          </div>

          {/* Refresh button */}
          <button
            onClick={() => {
              if (!isConnected) {
                reconnect();
              } else {
                fetchMetrics();
              }
            }}
            disabled={isLoading}
            className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 
                     hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <RefreshIcon />
          </button>
        </div>
      </div>

      {/* Metrics grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <MetricCardComponent
          metric={displayMetrics.activeUsers}
          onClick={() => onMetricClick?.('activeUsers')}
        />
        <MetricCardComponent
          metric={displayMetrics.executionsToday}
          onClick={() => onMetricClick?.('executionsToday')}
        />
        <MetricCardComponent
          metric={displayMetrics.avgExecutionTime}
          onClick={() => onMetricClick?.('avgExecutionTime')}
        />
        <MetricCardComponent
          metric={displayMetrics.successRate}
          onClick={() => onMetricClick?.('successRate')}
        />
        <MetricCardComponent
          metric={displayMetrics.queuedTasks}
          onClick={() => onMetricClick?.('queuedTasks')}
        />
        <MetricCardComponent
          metric={displayMetrics.systemLoad}
          onClick={() => onMetricClick?.('systemLoad')}
        />
      </div>
    </div>
  );
}

// Default metrics configuration
function getDefaultMetrics(): RealTimeMetrics {
  return {
    activeUsers: {
      id: 'activeUsers',
      title: 'Active Users',
      value: 0,
      unit: 'users',
      change: 0,
      icon: <UsersIcon />,
      color: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'
    },
    executionsToday: {
      id: 'executionsToday',
      title: 'Executions Today',
      value: 0,
      change: 0,
      icon: <CodeIcon />,
      color: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400'
    },
    avgExecutionTime: {
      id: 'avgExecutionTime',
      title: 'Avg. Execution',
      value: 0,
      unit: 'ms',
      change: 0,
      icon: <ClockIcon />,
      color: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400'
    },
    successRate: {
      id: 'successRate',
      title: 'Success Rate',
      value: 0,
      unit: '%',
      change: 0,
      icon: <CheckCircleIcon />,
      color: 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400'
    },
    queuedTasks: {
      id: 'queuedTasks',
      title: 'Queued Tasks',
      value: 0,
      change: 0,
      icon: <QueueIcon />,
      color: 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400'
    },
    systemLoad: {
      id: 'systemLoad',
      title: 'System Load',
      value: 0,
      unit: '%',
      change: 0,
      icon: <CpuIcon />,
      color: 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400'
    }
  };
}

