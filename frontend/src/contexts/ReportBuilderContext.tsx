import React, { createContext, useContext, useState, useCallback, useMemo, ReactNode } from 'react';

// Type definitions for report builder
export interface ReportMetric {
  id: string;
  name: string;
  field: string;
  aggregation: 'sum' | 'avg' | 'count' | 'min' | 'max' | 'distinct';
  format: 'number' | 'currency' | 'percentage' | 'duration';
}

export interface ReportDimension {
  id: string;
  name: string;
  field: string;
  type: 'date' | 'category' | 'user' | 'course';
  granularity?: 'hour' | 'day' | 'week' | 'month' | 'quarter' | 'year';
}

export interface ReportFilter {
  id: string;
  field: string;
  operator: 'equals' | 'not_equals' | 'contains' | 'greater_than' | 'less_than' | 'between' | 'in';
  value: unknown;
  value2?: unknown;
}

export interface ReportTimeRange {
  type: 'preset' | 'custom';
  preset?: 'today' | 'yesterday' | 'last_7_days' | 'last_30_days' | 'this_month' | 'last_month' | 'this_year';
  startDate?: string;
  endDate?: string;
}

export interface ReportVisualization {
  type: 'table' | 'bar_chart' | 'line_chart' | 'pie_chart' | 'area_chart' | 'heatmap';
  title: string;
  xAxis?: string;
  yAxis?: string;
  colorScheme?: string;
  showLegend?: boolean;
  showGrid?: boolean;
}

export interface ReportColumn {
  id: string;
  field: string;
  header: string;
  width?: number;
  sortable?: boolean;
  filterable?: boolean;
  visible?: boolean;
}

export interface SavedReport {
  id: string;
  name: string;
  description: string;
  query: ReportQuery;
  createdAt: string;
  createdBy: string;
  isPublic: boolean;
  schedule?: ReportSchedule;
}

export interface ReportSchedule {
  frequency: 'daily' | 'weekly' | 'monthly';
  dayOfWeek?: number; // 0-6 for weekly
  dayOfMonth?: number; // 1-31 for monthly
  time: string; // HH:mm
  recipients: string[];
  format: 'pdf' | 'csv' | 'excel';
  enabled: boolean;
}

export interface ReportQuery {
  metrics: string[];
  dimensions: string[];
  filters: ReportFilter[];
  timeRange: ReportTimeRange;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  limit?: number;
}

export interface ReportData {
  columns: ReportColumn[];
  rows: Record<string, unknown>[];
  totalRows: number;
  executionTime: number;
  cachedAt?: string;
}

export interface ExportJob {
  id: string;
  reportId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  format: 'pdf' | 'csv' | 'excel';
  progress: number;
  url?: string;
  error?: string;
  createdAt: string;
  completedAt?: string;
}

export interface ReportBuilderContextType {
  // Query State
  query: ReportQuery;
  setQuery: (query: Partial<ReportQuery>) => void;
  resetQuery: () => void;
  
  // Visualization State
  visualizations: ReportVisualization[];
  addVisualization: (viz: ReportVisualization) => void;
  updateVisualization: (index: number, viz: ReportVisualization) => void;
  removeVisualization: (index: number) => void;
  
  // Available Fields
  availableMetrics: ReportMetric[];
  availableDimensions: ReportDimension[];
  
  // Data State
  data: ReportData | null;
  isLoading: boolean;
  error: string | null;
  
  // Execution
  executeQuery: () => Promise<void>;
  refreshData: () => Promise<void>;
  
  // Export
  exportJob: ExportJob | null;
  startExport: (format: ExportJob['format']) => Promise<void>;
  checkExportStatus: (jobId: string) => Promise<void>;
  
  // Saved Reports
  savedReports: SavedReport[];
  loadSavedReport: (reportId: string) => Promise<void>;
  saveCurrentReport: (name: string, description: string, isPublic: boolean) => Promise<SavedReport>;
  deleteSavedReport: (reportId: string) => Promise<void>;
  
  // Schedule
  schedule: ReportSchedule | null;
  setSchedule: (schedule: ReportSchedule | null) => void;
  
  // Utilities
  getFieldLabel: (field: string) => string;
  formatValue: (value: unknown, format: ReportMetric['format']) => string;
}

const defaultQuery: ReportQuery = {
  metrics: [],
  dimensions: [],
  filters: [],
  timeRange: { type: 'preset', preset: 'last_30_days' },
  sortBy: undefined,
  sortOrder: 'desc',
  limit: 1000,
};

const ReportBuilderContext = createContext<ReportBuilderContextType | undefined>(undefined);

export function ReportBuilderProvider({ children }: { children: ReactNode }) {
  const [query, setQueryState] = useState<ReportQuery>(defaultQuery);
  const [visualizations, setVisualizations] = useState<ReportVisualization[]>([]);
  const [data, setData] = useState<ReportData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exportJob, setExportJob] = useState<ExportJob | null>(null);
  const [savedReports, setSavedReports] = useState<SavedReport[]>([]);
  const [schedule, setSchedule] = useState<ReportSchedule | null>(null);

  // Available metrics
  const availableMetrics: ReportMetric[] = useMemo(() => [
    { id: 'total_users', name: 'Total Users', field: 'users.id', aggregation: 'count', format: 'number' },
    { id: 'active_users', name: 'Active Users', field: 'users.active', aggregation: 'count', format: 'number' },
    { id: 'total_courses', name: 'Total Courses', field: 'courses.id', aggregation: 'count', format: 'number' },
    { id: 'course_completions', name: 'Course Completions', field: 'enrollments.completed', aggregation: 'count', format: 'number' },
    { id: 'avg_completion_rate', name: 'Avg Completion Rate', field: 'enrollments.completion_rate', aggregation: 'avg', format: 'percentage' },
    { id: 'total_xp', name: 'Total XP Earned', field: 'gamification.xp', aggregation: 'sum', format: 'number' },
    { id: 'avg_session_duration', name: 'Avg Session Duration', field: 'sessions.duration', aggregation: 'avg', format: 'duration' },
    { id: 'total_revenue', name: 'Total Revenue', field: 'payments.amount', aggregation: 'sum', format: 'currency' },
  ], []);

  // Available dimensions
  const availableDimensions: ReportDimension[] = useMemo(() => [
    { id: 'date', name: 'Date', field: 'created_at', type: 'date', granularity: 'day' },
    { id: 'user_role', name: 'User Role', field: 'users.role', type: 'category' },
    { id: 'course_category', name: 'Course Category', field: 'courses.category', type: 'category' },
    { id: 'course_difficulty', name: 'Course Difficulty', field: 'courses.difficulty', type: 'category' },
    { id: 'country', name: 'Country', field: 'users.country', type: 'category' },
    { id: 'payment_status', name: 'Payment Status', field: 'payments.status', type: 'category' },
  ], []);

  // Update query
  const setQuery = useCallback((updates: Partial<ReportQuery>) => {
    setQueryState(prev => ({ ...prev, ...updates }));
  }, []);

  // Reset query
  const resetQuery = useCallback(() => {
    setQueryState(defaultQuery);
    setVisualizations([]);
    setData(null);
  }, []);

  // Add visualization
  const addVisualization = useCallback((viz: ReportVisualization) => {
    setVisualizations(prev => [...prev, viz]);
  }, []);

  // Update visualization
  const updateVisualization = useCallback((index: number, viz: ReportVisualization) => {
    setVisualizations(prev => {
      const updated = [...prev];
      updated[index] = viz;
      return updated;
    });
  }, []);

  // Remove visualization
  const removeVisualization = useCallback((index: number) => {
    setVisualizations(prev => prev.filter((_, i) => i !== index));
  }, []);

  // Execute query
  const executeQuery = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Simulate API call
      const response = await new Promise<ReportData>((resolve) => {
        setTimeout(() => {
          const columns: ReportColumn[] = [
            { id: 'col1', field: 'date', header: 'Date', sortable: true },
            { id: 'col2', field: 'users', header: 'Users', sortable: true },
            { id: 'col3', field: 'courses', header: 'Courses', sortable: true },
            { id: 'col4', field: 'completions', header: 'Completions', sortable: true },
            { id: 'col5', field: 'revenue', header: 'Revenue', sortable: true },
          ];
          
          const rows: Record<string, unknown>[] = [];
          for (let i = 0; i < 25; i++) {
            rows.push({
              date: new Date(Date.now() - i * 86400000).toISOString().split('T')[0],
              users: Math.floor(Math.random() * 500) + 100,
              courses: Math.floor(Math.random() * 50) + 10,
              completions: Math.floor(Math.random() * 100) + 20,
              revenue: Math.floor(Math.random() * 5000) + 1000,
            });
          }
          
          resolve({
            columns,
            rows,
            totalRows: rows.length,
            executionTime: 0.45,
            cachedAt: new Date().toISOString(),
          });
        }, 800);
      });
      
      setData(response);
    } catch (err) {
      setError('Failed to execute report query');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Refresh data
  const refreshData = useCallback(async () => {
    await executeQuery();
  }, [executeQuery]);

  // Start export
  const startExport = useCallback(async (format: ExportJob['format']) => {
    setIsLoading(true);
    
    try {
      // Simulate export job creation
      const job: ExportJob = {
        id: `export-${Date.now()}`,
        reportId: 'current-report',
        status: 'pending',
        format,
        progress: 0,
        createdAt: new Date().toISOString(),
      };
      
      setExportJob(job);
      
      // Simulate processing
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setExportJob(prev => prev ? ({
        ...prev,
        status: 'completed',
        progress: 100,
        url: `/api/v4/admin/reports/download/${job.id}`,
        completedAt: new Date().toISOString(),
      }) : null);
    } catch (err) {
      setExportJob(prev => prev ? ({
        ...prev,
        status: 'failed',
        error: (err as Error).message,
      }) : null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Check export status
  const checkExportStatus = useCallback(async (jobId: string) => {
    console.log('Checking export status:', jobId);
  }, []);

  // Load saved report
  const loadSavedReport = useCallback(async (reportId: string) => {
    const report = savedReports.find(r => r.id === reportId);
    if (report) {
      setQueryState(report.query);
    }
  }, [savedReports]);

  // Save current report
  const saveCurrentReport = useCallback(async (
    name: string,
    description: string,
    isPublic: boolean
  ): Promise<SavedReport> => {
    const savedReport: SavedReport = {
      id: `report-${Date.now()}`,
      name,
      description,
      query: { ...query },
      createdAt: new Date().toISOString(),
      createdBy: 'current-user',
      isPublic,
    };
    
    setSavedReports(prev => [...prev, savedReport]);
    return savedReport;
  }, [query]);

  // Delete saved report
  const deleteSavedReport = useCallback(async (reportId: string) => {
    setSavedReports(prev => prev.filter(r => r.id !== reportId));
  }, []);

  // Get field label
  const getFieldLabel = useCallback((field: string) => {
    const metric = availableMetrics.find(m => m.field === field);
    if (metric) return metric.name;
    
    const dimension = availableDimensions.find(d => d.field === field);
    if (dimension) return dimension.name;
    
    return field;
  }, [availableMetrics, availableDimensions]);

  // Format value
  const formatValue = useCallback((value: unknown, format: ReportMetric['format']) => {
    if (value === null || value === undefined) return '-';
    
    switch (format) {
      case 'currency':
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value as number);
      case 'percentage':
        return `${(value as number).toFixed(1)}%`;
      case 'duration':
        const mins = Math.floor((value as number) / 60);
        const secs = Math.floor((value as number) % 60);
        return `${mins}m ${secs}s`;
      default:
        return new Intl.NumberFormat('en-US').format(value as number);
    }
  }, []);

  const value: ReportBuilderContextType = {
    query,
    setQuery,
    resetQuery,
    visualizations,
    addVisualization,
    updateVisualization,
    removeVisualization,
    availableMetrics,
    availableDimensions,
    data,
    isLoading,
    error,
    executeQuery,
    refreshData,
    exportJob,
    startExport,
    checkExportStatus,
    savedReports,
    loadSavedReport,
    saveCurrentReport,
    deleteSavedReport,
    schedule,
    setSchedule,
    getFieldLabel,
    formatValue,
  };

  return (
    <ReportBuilderContext.Provider value={value}>
      {children}
    </ReportBuilderContext.Provider>
  );
}

export function useReportBuilder() {
  const context = useContext(ReportBuilderContext);
  if (context === undefined) {
    throw new Error('useReportBuilder must be used within a ReportBuilderProvider');
  }
  return context;
}

export default ReportBuilderContext;
