import { useState, useCallback, useEffect, useRef } from 'react';

// Type definitions for system health
export interface SystemMetrics {
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
  networkIn: number;
  networkOut: number;
  activeConnections: number;
  requestsPerSecond: number;
  averageResponseTime: number;
  errorRate: number;
  uptime: number;
  lastUpdated: string;
}

export interface HealthComponent {
  name: string;
  status: 'operational' | 'degraded' | 'down' | 'unknown';
  message?: string;
  lastChecked: string;
  responseTime?: number;
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy' | 'unknown';
  overallUptime: number;
  components: HealthComponent[];
  lastUpdated: string;
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  actorId: string;
  actorEmail: string;
  actorRole: string;
  action: string;
  resourceType: string;
  resourceId?: string;
  details: Record<string, unknown>;
  ipAddress?: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  status: 'success' | 'failure';
}

export interface UseSystemHealthOptions {
  pollInterval?: number;
  onHealthChange?: (health: SystemHealth) => void;
  onMetricsUpdate?: (metrics: SystemMetrics) => void;
  enablePolling?: boolean;
}

export interface UseSystemHealthReturn {
  // Metrics
  metrics: SystemMetrics | null;
  isLoadingMetrics: boolean;
  fetchMetrics: () => Promise<void>;
  
  // Health
  health: SystemHealth | null;
  isLoadingHealth: boolean;
  fetchHealth: () => Promise<void>;
  
  // Audit logs
  auditLogs: AuditLogEntry[];
  totalLogs: number;
  isLoadingLogs: boolean;
  fetchAuditLogs: (filter?: AuditLogFilter) => Promise<void>;
  exportAuditLogs: (filter?: AuditLogFilter) => Promise<void>;
  setLogFilter: (filter: AuditLogFilter) => void;
  
  // Polling control
  isPolling: boolean;
  startPolling: (interval?: number) => void;
  stopPolling: () => void;
  
  // Utilities
  getHealthStatus: () => 'healthy' | 'degraded' | 'unhealthy' | 'unknown';
  getComponentStatus: (name: string) => HealthComponent | undefined;
  formatUptime: (seconds: number) => string;
  formatBytes: (bytes: number) => string;
}

export interface AuditLogFilter {
  actorId?: string;
  action?: string;
  resourceType?: string;
  severity?: AuditLogEntry['severity'];
  dateRange?: {
    start: string;
    end: string;
  };
  searchText?: string;
}

export function useSystemHealth(options: UseSystemHealthOptions = {}): UseSystemHealthReturn {
  const {
    pollInterval = 5000,
    onHealthChange,
    onMetricsUpdate,
    enablePolling = true,
  } = options;

  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [isLoadingMetrics, setIsLoadingMetrics] = useState(false);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [isLoadingHealth, setIsLoadingHealth] = useState(false);
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([]);
  const [totalLogs, setTotalLogs] = useState(0);
  const [isLoadingLogs, setIsLoadingLogs] = useState(false);
  const [logFilter, setLogFilter] = useState<AuditLogFilter>({});
  const [isPolling, setIsPolling] = useState(false);
  
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  // Fetch metrics
  const fetchMetrics = useCallback(async () => {
    setIsLoadingMetrics(true);
    try {
      // Simulate API call
      const response = await new Promise<SystemMetrics>((resolve) => {
        setTimeout(() => {
          resolve({
            cpuUsage: 35 + Math.random() * 30,
            memoryUsage: 60 + Math.random() * 20,
            diskUsage: 45 + Math.random() * 15,
            networkIn: Math.random() * 500,
            networkOut: Math.random() * 500,
            activeConnections: Math.floor(100 + Math.random() * 200),
            requestsPerSecond: Math.floor(50 + Math.random() * 100),
            averageResponseTime: Math.random() * 200 + 50,
            errorRate: Math.random() * 2,
            uptime: 86400 - Math.random() * 3600,
            lastUpdated: new Date().toISOString(),
          });
        }, 300);
      });
      
      setMetrics(response);
      onMetricsUpdate?.(response);
    } catch (error) {
      console.error('Failed to fetch system metrics:', error);
    } finally {
      setIsLoadingMetrics(false);
    }
  }, [onMetricsUpdate]);

  // Fetch health
  const fetchHealth = useCallback(async () => {
    setIsLoadingHealth(true);
    try {
      // Simulate API call
      const response = await new Promise<SystemHealth>((resolve) => {
        setTimeout(() => {
          resolve({
            status: 'healthy',
            overallUptime: 86400 * 7, // 7 days
            components: [
              {
                name: 'API Server',
                status: 'operational',
                responseTime: Math.random() * 100 + 20,
                lastChecked: new Date().toISOString(),
              },
              {
                name: 'Database',
                status: 'operational',
                responseTime: Math.random() * 50 + 10,
                lastChecked: new Date().toISOString(),
              },
              {
                name: 'WebSocket Server',
                status: 'operational',
                responseTime: Math.random() * 30 + 5,
                lastChecked: new Date().toISOString(),
              },
              {
                name: 'File Storage',
                status: 'operational',
                responseTime: Math.random() * 100 + 50,
                lastChecked: new Date().toISOString(),
              },
              {
                name: 'Email Service',
                status: Math.random() > 0.9 ? 'degraded' : 'operational',
                message: Math.random() > 0.9 ? 'Slight delay in delivery' : undefined,
                responseTime: Math.random() * 500 + 100,
                lastChecked: new Date().toISOString(),
              },
            ],
            lastUpdated: new Date().toISOString(),
          });
        }, 300);
      });
      
      setHealth(response);
      onHealthChange?.(response);
    } catch (error) {
      console.error('Failed to fetch system health:', error);
    } finally {
      setIsLoadingHealth(false);
    }
  }, [onHealthChange]);

  // Fetch audit logs
  const fetchAuditLogs = useCallback(async (filter?: AuditLogFilter) => {
    setIsLoadingLogs(true);
    try {
      // Simulate API call
      const response = await new Promise<{ logs: AuditLogEntry[]; total: number }>((resolve) => {
        setTimeout(() => {
          const mockLogs: AuditLogEntry[] = [
            {
              id: 'log-1',
              timestamp: new Date(Date.now() - 3600000).toISOString(),
              actorId: 'user-123',
              actorEmail: 'instructor@example.com',
              actorRole: 'instructor',
              action: 'CREATE_COURSE',
              resourceType: 'course',
              resourceId: 'course-456',
              details: { title: 'Introduction to Python' },
              severity: 'info',
              status: 'success',
            },
            {
              id: 'log-2',
              timestamp: new Date(Date.now() - 7200000).toISOString(),
              actorId: 'user-789',
              actorEmail: 'admin@example.com',
              actorRole: 'admin',
              action: 'SUSPEND_USER',
              resourceType: 'user',
              resourceId: 'user-999',
              details: { reason: 'Violated terms of service' },
              severity: 'warning',
              status: 'success',
            },
          ];
          resolve({ logs: mockLogs, total: mockLogs.length });
        }, 500);
      });
      
      setAuditLogs(response.logs);
      setTotalLogs(response.total);
      if (filter) setLogFilter(filter);
    } catch (error) {
      console.error('Failed to fetch audit logs:', error);
    } finally {
      setIsLoadingLogs(false);
    }
  }, []);

  // Export audit logs
  const exportAuditLogs = useCallback(async (filter?: AuditLogFilter) => {
    const headers = [
      'Timestamp',
      'Actor',
      'Action',
      'Resource Type',
      'Resource ID',
      'Severity',
      'Status',
      'IP Address',
    ];
    
    const rows = auditLogs.map(log => [
      log.timestamp,
      log.actorEmail,
      log.action,
      log.resourceType,
      log.resourceId || '',
      log.severity,
      log.status,
      log.ipAddress || '',
    ]);
    
    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }, [auditLogs]);

  // Start polling
  const startPolling = useCallback((interval = pollInterval) => {
    if (isPolling) return;
    
    setIsPolling(true);
    fetchMetrics();
    fetchHealth();
    
    pollingRef.current = setInterval(() => {
      fetchMetrics();
      fetchHealth();
    }, interval);
  }, [isPolling, pollInterval, fetchMetrics, fetchHealth]);

  // Stop polling
  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
    setIsPolling(false);
  }, []);

  // Get health status
  const getHealthStatus = useCallback((): 'healthy' | 'degraded' | 'unhealthy' | 'unknown' => {
    return health?.status || 'unknown';
  }, [health]);

  // Get component status
  const getComponentStatus = useCallback((name: string): HealthComponent | undefined => {
    return health?.components.find(c => c.name === name);
  }, [health]);

  // Format uptime
  const formatUptime = useCallback((seconds: number): string => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    const parts: string[] = [];
    if (days > 0) parts.push(`${days}d`);
    if (hours > 0) parts.push(`${hours}h`);
    if (minutes > 0) parts.push(`${minutes}m`);
    
    return parts.join(' ') || '0m';
  }, []);

  // Format bytes
  const formatBytes = useCallback((bytes: number): string => {
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let unitIndex = 0;
    let size = bytes;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    
    return `${size.toFixed(1)} ${units[unitIndex]}`;
  }, []);

  // Auto-poll on mount if enabled
  useEffect(() => {
    if (enablePolling) {
      startPolling();
    }
    
    return () => {
      stopPolling();
    };
  }, [enablePolling, startPolling, stopPolling]);

  return {
    metrics,
    isLoadingMetrics,
    fetchMetrics,
    health,
    isLoadingHealth,
    fetchHealth,
    auditLogs,
    totalLogs,
    isLoadingLogs,
    fetchAuditLogs,
    exportAuditLogs,
    setLogFilter,
    isPolling,
    startPolling,
    stopPolling,
    getHealthStatus,
    getComponentStatus,
    formatUptime,
    formatBytes,
  };
}

export default useSystemHealth;
