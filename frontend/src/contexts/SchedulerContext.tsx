import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';

// Type definitions for scheduled tasks
export interface ScheduledTask {
  id: string;
  name: string;
  description: string;
  type: 'email_digest' | 'report' | 'notification' | 'cleanup' | 'backup' | 'custom';
  cronExpression: string;
  timezone: string;
  action: {
    type: string;
    config: Record<string, unknown>;
  };
  enabled: boolean;
  lastRun?: {
    status: 'success' | 'failed' | 'partial';
    startedAt: string;
    completedAt: string;
    output?: string;
    error?: string;
  };
  nextRun?: string;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  runCount: number;
  successRate: number;
}

export interface TaskExecutionLog {
  id: string;
  taskId: string;
  status: 'running' | 'success' | 'failed' | 'partial';
  startedAt: string;
  completedAt?: string;
  duration?: number;
  output?: string;
  error?: string;
  metadata?: Record<string, unknown>;
}

export interface CronSchedule {
  expression: string;
  humanReadable: string;
  nextExecution: string;
  previousExecution?: string;
}

export interface TaskTemplate {
  id: string;
  name: string;
  description: string;
  type: ScheduledTask['type'];
  cronPreset: string;
  defaultConfig: Record<string, unknown>;
}

export interface SchedulerContextType {
  // Task State
  tasks: ScheduledTask[];
  selectedTask: ScheduledTask | null;
  isLoading: boolean;
  error: string | null;
  
  // Task Operations
  fetchTasks: () => Promise<void>;
  createTask: (task: Partial<ScheduledTask>) => Promise<ScheduledTask>;
  updateTask: (taskId: string, updates: Partial<ScheduledTask>) => Promise<void>;
  deleteTask: (taskId: string) => Promise<void>;
  toggleTask: (taskId: string, enabled: boolean) => Promise<void>;
  
  // Execution Operations
  executeTask: (taskId: string) => Promise<void>;
  cancelExecution: (taskId: string) => Promise<void>;
  
  // Logs State
  executionLogs: TaskExecutionLog[];
  fetchExecutionLogs: (taskId: string, limit?: number) => Promise<void>;
  
  // Templates
  templates: TaskTemplate[];
  createFromTemplate: (templateId: string, customConfig?: Record<string, unknown>) => Promise<ScheduledTask>;
  
  // Validation
  validateCronExpression: (expression: string) => { isValid: boolean; humanReadable: string; error?: string };
  
  // Statistics
  getTaskStats: () => {
    totalTasks: number;
    activeTasks: number;
    totalRuns: number;
    successRate: number;
  };
}

const SchedulerContext = createContext<SchedulerContextType | undefined>(undefined);

// Preset cron expressions
const CRON_PRESETS = {
  every_minute: '* * * * *',
  every_5_minutes: '*/5 * * * *',
  every_15_minutes: '*/15 * * * *',
  every_30_minutes: '*/30 * * * *',
  every_hour: '0 * * * *',
  every_4_hours: '0 */4 * * *',
  every_6_hours: '0 */6 * * *',
  every_12_hours: '0 */12 * * *',
  daily_midnight: '0 0 * * *',
  daily_6am: '0 6 * * *',
  daily_noon: '0 12 * * *',
  weekly_sunday: '0 0 * * 0',
  weekly_monday: '0 0 * * 1',
  monthly_first: '0 0 1 * *',
  quarterly_first: '0 0 1 1,4,7,10 *',
};

export function SchedulerProvider({ children }: { children: ReactNode }) {
  const [tasks, setTasks] = useState<ScheduledTask[]>([]);
  const [selectedTask, setSelectedTask] = useState<ScheduledTask | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [executionLogs, setExecutionLogs] = useState<TaskExecutionLog[]>([]);
  
  // Templates
  const templates: TaskTemplate[] = [
    {
      id: 'tpl-daily-digest',
      name: 'Daily Learning Digest',
      description: 'Send daily summary of user progress and achievements',
      type: 'email_digest',
      cronPreset: 'daily_6am',
      defaultConfig: {
        includeStats: ['progress', 'achievements', 'leaderboard'],
        templateId: 'daily-digest',
        recipientFilter: 'active_users',
      },
    },
    {
      id: 'tpl-weekly-report',
      name: 'Weekly Course Report',
      description: 'Generate and email weekly course analytics report',
      type: 'report',
      cronPreset: 'weekly_monday',
      defaultConfig: {
        reportType: 'course_analytics',
        includeCharts: true,
        format: 'pdf',
        recipients: ['instructors', 'admins'],
      },
    },
    {
      id: 'tpl-cleanup',
      name: 'Session Cleanup',
      description: 'Clean up expired sessions and temporary data',
      type: 'cleanup',
      cronPreset: 'every_6_hours',
      defaultConfig: {
        cleanupAge: '7d',
        includeTables: ['sessions', 'temp_tokens', 'expired_codes'],
      },
    },
    {
      id: 'tpl-backup',
      name: 'Database Backup',
      description: 'Create automated database backups',
      type: 'backup',
      cronPreset: 'daily_midnight',
      defaultConfig: {
        storage: 's3',
        retentionDays: 30,
        compression: true,
        includeTables: ['all'],
      },
    },
    {
      id: 'tpl-reminder',
      name: 'Course Reminder',
      description: 'Send reminders for incomplete courses',
      type: 'notification',
      cronPreset: 'daily_noon',
      defaultConfig: {
        triggerType: 'course_incomplete',
        thresholdDays: 3,
        maxReminders: 2,
      },
    },
  ];

  // Fetch all tasks
  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    try {
      // Simulate API call
      const response = await new Promise<ScheduledTask[]>((resolve) => {
        setTimeout(() => {
          const mockTasks: ScheduledTask[] = [
            {
              id: 'task-1',
              name: 'Daily Learning Digest',
              description: 'Send daily summary of user progress',
              type: 'email_digest',
              cronExpression: '0 6 * * *',
              timezone: 'America/New_York',
              action: { type: 'send_email', config: { template: 'daily-digest' } },
              enabled: true,
              lastRun: {
                status: 'success',
                startedAt: '2025-12-15T06:00:00Z',
                completedAt: '2025-12-15T06:02:15Z',
                output: 'Sent 1,245 emails successfully',
              },
              nextRun: '2025-12-16T06:00:00Z',
              createdAt: '2025-11-01T10:00:00Z',
              updatedAt: '2025-12-10T14:30:00Z',
              createdBy: 'admin',
              runCount: 45,
              successRate: 98.5,
            },
            {
              id: 'task-2',
              name: 'Weekly Analytics Report',
              description: 'Generate comprehensive weekly analytics',
              type: 'report',
              cronExpression: '0 8 * * 1',
              timezone: 'America/New_York',
              action: { type: 'generate_report', config: { type: 'analytics', format: 'pdf' } },
              enabled: true,
              lastRun: {
                status: 'success',
                startedAt: '2025-12-14T08:00:00Z',
                completedAt: '2025-12-14T08:05:30Z',
                output: 'Report generated: analytics-week-50.pdf',
              },
              nextRun: '2025-12-21T08:00:00Z',
              createdAt: '2025-10-15T12:00:00Z',
              updatedAt: '2025-12-01T09:00:00Z',
              createdBy: 'admin',
              runCount: 18,
              successRate: 100,
            },
            {
              id: 'task-3',
              name: 'Session Cleanup',
              description: 'Clean up expired sessions',
              type: 'cleanup',
              cronExpression: '0 */6 * * *',
              timezone: 'UTC',
              action: { type: 'cleanup_sessions', config: { olderThan: '7d' } },
              enabled: true,
              lastRun: {
                status: 'success',
                startedAt: '2025-12-15T12:00:00Z',
                completedAt: '2025-12-15T12:01:45Z',
                output: 'Cleaned 234 expired sessions',
              },
              nextRun: '2025-12-15T18:00:00Z',
              createdAt: '2025-09-01T08:00:00Z',
              updatedAt: '2025-11-20T16:00:00Z',
              createdBy: 'system',
              runCount: 320,
              successRate: 99.7,
            },
            {
              id: 'task-4',
              name: 'Database Backup',
              description: 'Automated database backup',
              type: 'backup',
              cronExpression: '0 0 * * *',
              timezone: 'UTC',
              action: { type: 'backup_db', config: { storage: 's3', compression: true } },
              enabled: false,
              lastRun: {
                status: 'failed',
                startedAt: '2025-12-14T00:00:00Z',
                completedAt: '2025-12-14T00:05:00Z',
                error: 'Connection timeout to backup storage',
              },
              createdAt: '2025-08-01T00:00:00Z',
              updatedAt: '2025-12-14T00:05:00Z',
              createdBy: 'admin',
              runCount: 166,
              successRate: 98.8,
            },
          ];
          resolve(mockTasks);
        }, 500);
      });
      setTasks(response);
    } catch (err) {
      setError('Failed to fetch scheduled tasks');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Create task
  const createTask = useCallback(async (task: Partial<ScheduledTask>): Promise<ScheduledTask> => {
    const newTask: ScheduledTask = {
      id: `task-${Date.now()}`,
      name: task.name || 'New Task',
      description: task.description || '',
      type: task.type || 'custom',
      cronExpression: task.cronExpression || '0 0 * * *',
      timezone: task.timezone || 'UTC',
      action: task.action || { type: 'custom', config: {} },
      enabled: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      createdBy: 'current-user',
      runCount: 0,
      successRate: 0,
      ...task,
    };
    
    setTasks(prev => [...prev, newTask]);
    return newTask;
  }, []);

  // Update task
  const updateTask = useCallback(async (taskId: string, updates: Partial<ScheduledTask>) => {
    setTasks(prev =>
      prev.map(task =>
        task.id === taskId
          ? { ...task, ...updates, updatedAt: new Date().toISOString() }
          : task
      )
    );
  }, []);

  // Delete task
  const deleteTask = useCallback(async (taskId: string) => {
    setTasks(prev => prev.filter(task => task.id !== taskId));
    if (selectedTask?.id === taskId) {
      setSelectedTask(null);
    }
  }, [selectedTask]);

  // Toggle task enabled state
  const toggleTask = useCallback(async (taskId: string, enabled: boolean) => {
    await updateTask(taskId, { enabled });
  }, [updateTask]);

  // Execute task immediately
  const executeTask = useCallback(async (taskId: string) => {
    // Simulate execution
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setTasks(prev =>
      prev.map(task =>
        task.id === taskId
          ? {
              ...task,
              lastRun: {
                status: 'success',
                startedAt: new Date().toISOString(),
                completedAt: new Date().toISOString(),
                output: 'Manual execution completed successfully',
              },
              runCount: task.runCount + 1,
            }
          : task
      )
    );
  }, []);

  // Cancel running execution
  const cancelExecution = useCallback(async (taskId: string) => {
    console.log('Cancelling execution for task:', taskId);
  }, []);

  // Fetch execution logs
  const fetchExecutionLogs = useCallback(async (taskId: string, limit = 50) => {
    // Simulate API call
    const logs: TaskExecutionLog[] = [
      {
        id: 'log-1',
        taskId,
        status: 'success',
        startedAt: '2025-12-15T06:00:00Z',
        completedAt: '2025-12-15T06:02:15Z',
        duration: 135,
        output: 'Sent 1,245 emails successfully',
      },
      {
        id: 'log-2',
        taskId,
        status: 'success',
        startedAt: '2025-12-14T06:00:00Z',
        completedAt: '2025-12-14T06:01:50Z',
        duration: 110,
        output: 'Sent 1,198 emails successfully',
      },
      {
        id: 'log-3',
        taskId,
        status: 'success',
        startedAt: '2025-12-13T06:00:00Z',
        completedAt: '2025-12-13T06:03:05Z',
        duration: 185,
        output: 'Sent 1,312 emails successfully',
      },
    ];
    setExecutionLogs(logs);
  }, []);

  // Create task from template
  const createFromTemplate = useCallback(async (
    templateId: string,
    customConfig?: Record<string, unknown>
  ): Promise<ScheduledTask> => {
    const template = templates.find(t => t.id === templateId);
    if (!template) {
      throw new Error('Template not found');
    }
    
    return createTask({
      name: template.name,
      description: template.description,
      type: template.type,
      cronExpression: CRON_PRESETS[template.cronPreset as keyof typeof CRON_PRESETS] || template.cronPreset,
      action: {
        type: template.defaultConfig.actionType || 'custom',
        config: { ...template.defaultConfig, ...customConfig },
      },
    });
  }, [templates, createTask]);

  // Validate cron expression
  const validateCronExpression = useCallback((expression: string): {
    isValid: boolean;
    humanReadable: string;
    error?: string;
  } => {
    // Basic validation
    const parts = expression.split(' ');
    
    if (parts.length < 5) {
      return { isValid: false, humanReadable: '', error: 'Invalid cron format (expected 5+ fields)' };
    }
    
    if (parts.length === 5) {
      return {
        isValid: true,
        humanReadable: `${parts[0]} min, ${parts[1]} hour, ${parts[2]} day, ${parts[3]} month, ${parts[4]} weekday`,
      };
    }
    
    return {
      isValid: true,
      humanReadable: `${parts[0]} min, ${parts[1]} hour, ${parts[2]} day, ${parts[3]} month, ${parts[4]} weekday, ${parts[5]} second`,
    };
  }, []);

  // Get task statistics
  const getTaskStats = useCallback(() => {
    const totalTasks = tasks.length;
    const activeTasks = tasks.filter(t => t.enabled).length;
    const totalRuns = tasks.reduce((sum, t) => sum + t.runCount, 0);
    const successfulRuns = tasks.reduce((sum, t) => sum + (t.runCount * t.successRate / 100), 0);
    const successRate = totalRuns > 0 ? (successfulRuns / totalRuns) * 100 : 0;
    
    return {
      totalTasks,
      activeTasks,
      totalRuns,
      successRate,
    };
  }, [tasks]);

  // Initial fetch
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const value: SchedulerContextType = {
    tasks,
    selectedTask,
    isLoading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleTask,
    executeTask,
    cancelExecution,
    executionLogs,
    fetchExecutionLogs,
    templates,
    createFromTemplate,
    validateCronExpression,
    getTaskStats,
  };

  return (
    <SchedulerContext.Provider value={value}>
      {children}
    </SchedulerContext.Provider>
  );
}

export function useScheduler() {
  const context = useContext(SchedulerContext);
  if (context === undefined) {
    throw new Error('useScheduler must be used within a SchedulerProvider');
  }
  return context;
}

export default SchedulerContext;
