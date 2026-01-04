import { createContext, useContext, useCallback, useState, useEffect, useRef, useMemo } from 'react';

// Types for analytics
export interface DateRange {
  start: string;
  end: string;
  label?: string;
}

export interface AnalyticsFilters {
  dateRange: DateRange;
  cohortId?: string;
  courseId?: string;
  userId?: string;
  language?: string;
  metricType?: string;
}

export interface ExecutionMetric {
  language: string;
  totalRuns: number;
  successfulRuns: number;
  failedRuns: number;
  successRate: number;
  avgRuntimeMs: number;
  medianRuntimeMs: number;
  p95RuntimeMs: number;
  avgMemoryKB: number;
  commonErrors: Array<{ error: string; count: number; percentage: number }>;
}

export interface LearningMetric {
  conceptId: string;
  conceptName: string;
  attempts: number;
  successRate: number;
  avgTimeSpent: number;
  masteryLevel: number;
  subConcepts: Array<{
    id: string;
    name: string;
    masteryLevel: number;
  }>;
}

export interface EngagementMetric {
  dailyActiveUsers: number;
  weeklyActiveUsers: number;
  monthlyActiveUsers: number;
  avgSessionDuration: number;
  totalSessionTime: number;
  loginFrequency: number;
  collaborationParticipation: number;
  completionRate: number;
}

export interface PerformanceTrend {
  date: string;
  executions: number;
  successRate: number;
  avgRuntime: number;
  activeUsers: number;
}

export interface StudentPerformance {
  userId: string;
  userName: string;
  avatar?: string;
  totalExecutions: number;
  successRate: number;
  avgScore: number;
  completionRate: number;
  engagementScore: number;
  riskLevel: 'low' | 'medium' | 'high';
  riskFactors: string[];
  lastActive: string;
}

export interface CohortAnalytics {
  cohortId: string;
  cohortName: string;
  studentCount: number;
  avgSuccessRate: number;
  avgCompletionRate: number;
  avgEngagement: number;
  atRiskCount: number;
  topPerformers: StudentPerformance[];
  strugglingStudents: StudentPerformance[];
  conceptMastery: LearningMetric[];
}

export interface ActivityDataPoint {
  date: string;
  value: number;
  label?: string;
}

export interface SkillMetrics {
  overallLevel: number;
  categoryScores: Array<{ category: string; score: number; level: number }>;
  strongAreas: string[];
  improvementAreas: string[];
  skillBreakdown: Array<{
    skillId: string;
    skillName: string;
    level: number;
    practiceCount: number;
    successRate: number;
  }>;
}

export interface StudentAnalytics {
  studentId: string;
  studentName: string;
  overallProgress: number;
  totalXP: number;
  currentLevel: number;
  completedConcepts: number;
  totalConcepts: number;
  averageScore: number;
  totalTimeSpent: number;
  streakDays: number;
  recentActivity: ActivityDataPoint[];
  skillLevels: SkillMetrics;
  strengths: string[];
  areasForImprovement: string[];
}

export interface CourseAnalytics {
  courseId: string;
  courseName: string;
  totalStudents: number;
  activeStudents: number;
  completionRate: number;
  averageScore: number;
  averageTimeToComplete: number;
  dropOffPoints: Array<{ module: string; dropOffRate: number }>;
  conceptPerformance: LearningMetric[];
  engagementTrend: ActivityDataPoint[];
}

export interface EngagementData {
  dailyActiveUsers: number;
  weeklyActiveUsers: number;
  monthlyActiveUsers: number;
  averageSessionDuration: number;
  totalSessions: number;
  peakActivityHours: Array<{ hour: number; activity: number }>;
  engagementTrend: ActivityDataPoint[];
}

export interface SkillData {
  category: string;
  skills: Array<{
    id: string;
    name: string;
    level: number;
    maxLevel: number;
    practiceCount: number;
    successRate: number;
  }>;
}

export interface ReportConfig {
  id: string;
  name: string;
  type: 'user' | 'course' | 'cohort' | 'system';
  filters: AnalyticsFilters;
  sections: string[];
  format: 'pdf' | 'csv' | 'json';
}

export interface AnalyticsState {
  // Filters
  filters: AnalyticsFilters;
  
  // Cached data
  executionMetrics: ExecutionMetric | null;
  learningMetrics: LearningMetric[];
  engagementMetrics: EngagementMetric | null;
  performanceTrends: PerformanceTrend[];
  activityData: ActivityDataPoint[];
  skillsData: SkillData[];
  studentPerformance: StudentPerformance[];
  cohortAnalytics: CohortAnalytics | null;
  
  // Reports
  savedReports: ReportConfig[];
  generatingReport: boolean;
  
  // UI State
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

export interface AnalyticsContextType {
  // State
  state: AnalyticsState;
  
  // Filter Management
  setDateRange: (range: DateRange) => void;
  setCohortFilter: (cohortId?: string) => void;
  setCourseFilter: (courseId?: string) => void;
  setUserFilter: (userId?: string) => void;
  setLanguageFilter: (language?: string) => void;
  resetFilters: () => void;
  
  // Data Fetching
  fetchExecutionMetrics: () => Promise<void>;
  fetchLearningMetrics: () => Promise<void>;
  fetchEngagementMetrics: () => Promise<void>;
  fetchPerformanceTrends: () => Promise<void>;
  fetchActivityData: () => Promise<void>;
  fetchSkillsData: () => Promise<void>;
  fetchStudentPerformance: () => Promise<void>;
  fetchCohortAnalytics: (cohortId: string) => Promise<void>;
  refreshAll: () => Promise<void>;
  
  // Skill Assessment
  assessSkillLevel: (skillId: string, assessmentData: unknown) => Promise<number>;
  getSkillRecommendations: (skillId: string) => Promise<string[]>;
  
  // Reports
  generateReport: (config: Omit<ReportConfig, 'id'>) => Promise<string>;
  saveReportConfig: (config: ReportConfig) => Promise<void>;
  exportReport: (reportId: string, format: 'pdf' | 'csv' | 'json') => Promise<void>;
  
  // Utility
  getDatePreset: (preset: 'today' | 'week' | 'month' | 'quarter' | 'year') => DateRange;
  clearCache: () => void;
}

const AnalyticsContext = createContext<AnalyticsContextType | null>(null);

// Date presets
const DATE_PRESETS: Record<string, () => DateRange> = {
  today: () => {
    const today = new Date();
    return {
      start: new Date(today.setHours(0, 0, 0, 0)).toISOString(),
      end: new Date().toISOString(),
      label: 'Today'
    };
  },
  week: () => {
    const today = new Date();
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    return {
      start: weekAgo.toISOString(),
      end: new Date().toISOString(),
      label: 'Last 7 Days'
    };
  },
  month: () => {
    const today = new Date();
    const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
    return {
      start: monthAgo.toISOString(),
      end: new Date().toISOString(),
      label: 'Last 30 Days'
    };
  },
  quarter: () => {
    const today = new Date();
    const quarterAgo = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000);
    return {
      start: quarterAgo.toISOString(),
      end: new Date().toISOString(),
      label: 'Last 90 Days'
    };
  },
  year: () => {
    const today = new Date();
    const yearAgo = new Date(today.getTime() - 365 * 24 * 60 * 60 * 1000);
    return {
      start: yearAgo.toISOString(),
      end: new Date().toISOString(),
      label: 'Last Year'
    };
  }
};

export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AnalyticsState>({
    filters: {
      dateRange: DATE_PRESETS.month(),
      cohortId: undefined,
      courseId: undefined,
      userId: undefined,
      language: undefined,
      metricType: undefined
    },
    executionMetrics: null,
    learningMetrics: [],
    engagementMetrics: null,
    performanceTrends: [],
    activityData: [],
    skillsData: [],
    studentPerformance: [],
    cohortAnalytics: null,
    savedReports: [],
    generatingReport: false,
    isLoading: false,
    error: null,
    lastUpdated: null
  });

  const cacheRef = useRef<Map<string, unknown>>(new Map());
  const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

  // Filter management
  const setDateRange = useCallback((range: DateRange) => {
    setState(prev => ({
      ...prev,
      filters: { ...prev.filters, dateRange: range },
      executionMetrics: null,
      learningMetrics: [],
      engagementMetrics: null,
      performanceTrends: [],
      activityData: []
    }));
  }, []);

  const setCohortFilter = useCallback((cohortId?: string) => {
    setState(prev => ({
      ...prev,
      filters: { ...prev.filters, cohortId },
      cohortAnalytics: null,
      studentPerformance: []
    }));
  }, []);

  const setCourseFilter = useCallback((courseId?: string) => {
    setState(prev => ({
      ...prev,
      filters: { ...prev.filters, courseId },
      learningMetrics: []
    }));
  }, []);

  const setUserFilter = useCallback((userId?: string) => {
    setState(prev => ({
      ...prev,
      filters: { ...prev.filters, userId },
      executionMetrics: null,
      skillsData: []
    }));
  }, []);

  const setLanguageFilter = useCallback((language?: string) => {
    setState(prev => ({
      ...prev,
      filters: { ...prev.filters, language },
      executionMetrics: null
    }));
  }, []);

  const resetFilters = useCallback(() => {
    setState(prev => ({
      ...prev,
      filters: {
        dateRange: DATE_PRESETS.month(),
        cohortId: undefined,
        courseId: undefined,
        userId: undefined,
        language: undefined,
        metricType: undefined
      },
      executionMetrics: null,
      learningMetrics: [],
      engagementMetrics: null,
      performanceTrends: [],
      activityData: [],
      skillsData: [],
      studentPerformance: [],
      cohortAnalytics: null
    }));
  }, []);

  // Helper to check and update cache
  const getCachedData = useCallback(<T,>(key: string): T | null => {
    const cached = cacheRef.current.get(key);
    if (cached && Date.now() - (cached as { timestamp: number }).timestamp < CACHE_DURATION) {
      return (cached as { data: T }).data;
    }
    return null;
  }, []);

  const setCachedData = useCallback(<T,>(key: string, data: T) => {
    cacheRef.current.set(key, { data, timestamp: Date.now() });
  }, []);

  // Data fetching
  const fetchExecutionMetrics = useCallback(async () => {
    const cacheKey = `exec_${JSON.stringify(state.filters)}`;
    const cached = getCachedData<ExecutionMetric>(cacheKey);
    if (cached) {
      setState(prev => ({ ...prev, executionMetrics: cached }));
      return;
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const params = new URLSearchParams({
        startDate: state.filters.dateRange.start,
        endDate: state.filters.dateRange.end
      });
      
      if (state.filters.language) params.append('language', state.filters.language);
      if (state.filters.userId) params.append('userId', state.filters.userId);
      if (state.filters.courseId) params.append('courseId', state.filters.courseId);

      const response = await fetch(`/api/analytics/executions?${params}`);
      if (!response.ok) throw new Error('Failed to fetch execution metrics');
      
      const data = await response.json();
      setCachedData(cacheKey, data);
      setState(prev => ({
        ...prev,
        executionMetrics: data,
        isLoading: false,
        lastUpdated: new Date().toISOString()
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }));
    }
  }, [state.filters, getCachedData, setCachedData]);

  const fetchLearningMetrics = useCallback(async () => {
    const cacheKey = `learn_${JSON.stringify(state.filters)}`;
    const cached = getCachedData<LearningMetric[]>(cacheKey);
    if (cached) {
      setState(prev => ({ ...prev, learningMetrics: cached }));
      return;
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const params = new URLSearchParams({
        startDate: state.filters.dateRange.start,
        endDate: state.filters.dateRange.end
      });
      
      if (state.filters.courseId) params.append('courseId', state.filters.courseId);
      if (state.filters.userId) params.append('userId', state.filters.userId);

      const response = await fetch(`/api/analytics/learning?${params}`);
      if (!response.ok) throw new Error('Failed to fetch learning metrics');
      
      const data = await response.json();
      setCachedData(cacheKey, data);
      setState(prev => ({
        ...prev,
        learningMetrics: data,
        isLoading: false,
        lastUpdated: new Date().toISOString()
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }));
    }
  }, [state.filters, getCachedData, setCachedData]);

  const fetchEngagementMetrics = useCallback(async () => {
    const cacheKey = `engage_${JSON.stringify(state.filters)}`;
    const cached = getCachedData<EngagementMetric>(cacheKey);
    if (cached) {
      setState(prev => ({ ...prev, engagementMetrics: cached }));
      return;
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const params = new URLSearchParams({
        startDate: state.filters.dateRange.start,
        endDate: state.filters.dateRange.end
      });
      
      if (state.filters.cohortId) params.append('cohortId', state.filters.cohortId);

      const response = await fetch(`/api/analytics/engagement?${params}`);
      if (!response.ok) throw new Error('Failed to fetch engagement metrics');
      
      const data = await response.json();
      setCachedData(cacheKey, data);
      setState(prev => ({
        ...prev,
        engagementMetrics: data,
        isLoading: false,
        lastUpdated: new Date().toISOString()
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }));
    }
  }, [state.filters, getCachedData, setCachedData]);

  const fetchPerformanceTrends = useCallback(async () => {
    const cacheKey = `trends_${JSON.stringify(state.filters)}`;
    const cached = getCachedData<PerformanceTrend[]>(cacheKey);
    if (cached) {
      setState(prev => ({ ...prev, performanceTrends: cached }));
      return;
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const params = new URLSearchParams({
        startDate: state.filters.dateRange.start,
        endDate: state.filters.dateRange.end
      });
      
      if (state.filters.language) params.append('language', state.filters.language);
      if (state.filters.userId) params.append('userId', state.filters.userId);

      const response = await fetch(`/api/analytics/trends?${params}`);
      if (!response.ok) throw new Error('Failed to fetch performance trends');
      
      const data = await response.json();
      setCachedData(cacheKey, data);
      setState(prev => ({
        ...prev,
        performanceTrends: data,
        isLoading: false,
        lastUpdated: new Date().toISOString()
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }));
    }
  }, [state.filters, getCachedData, setCachedData]);

  const fetchActivityData = useCallback(async () => {
    const cacheKey = `activity_${JSON.stringify(state.filters)}`;
    const cached = getCachedData<ActivityDataPoint[]>(cacheKey);
    if (cached) {
      setState(prev => ({ ...prev, activityData: cached }));
      return;
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const params = new URLSearchParams({
        startDate: state.filters.dateRange.start,
        endDate: state.filters.dateRange.end
      });
      
      if (state.filters.userId) params.append('userId', state.filters.userId);

      const response = await fetch(`/api/analytics/activity?${params}`);
      if (!response.ok) throw new Error('Failed to fetch activity data');
      
      const data = await response.json();
      setCachedData(cacheKey, data);
      setState(prev => ({
        ...prev,
        activityData: data,
        isLoading: false,
        lastUpdated: new Date().toISOString()
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }));
    }
  }, [state.filters, getCachedData, setCachedData]);

  const fetchSkillsData = useCallback(async () => {
    const cacheKey = `skills_${state.filters.userId || 'all'}`;
    const cached = getCachedData<SkillData[]>(cacheKey);
    if (cached) {
      setState(prev => ({ ...prev, skillsData: cached }));
      return;
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const url = state.filters.userId
        ? `/api/analytics/skills/${state.filters.userId}`
        : '/api/analytics/skills';

      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch skills data');
      
      const data = await response.json();
      setCachedData(cacheKey, data);
      setState(prev => ({
        ...prev,
        skillsData: data,
        isLoading: false,
        lastUpdated: new Date().toISOString()
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }));
    }
  }, [state.filters, getCachedData, setCachedData]);

  const fetchStudentPerformance = useCallback(async () => {
    if (!state.filters.cohortId && !state.filters.courseId) return;

    const cacheKey = `students_${JSON.stringify(state.filters)}`;
    const cached = getCachedData<StudentPerformance[]>(cacheKey);
    if (cached) {
      setState(prev => ({ ...prev, studentPerformance: cached }));
      return;
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const params = new URLSearchParams({
        startDate: state.filters.dateRange.start,
        endDate: state.filters.dateRange.end
      });
      
      if (state.filters.cohortId) params.append('cohortId', state.filters.cohortId);
      if (state.filters.courseId) params.append('courseId', state.filters.courseId);

      const response = await fetch(`/api/analytics/student-performance?${params}`);
      if (!response.ok) throw new Error('Failed to fetch student performance');
      
      const data = await response.json();
      setCachedData(cacheKey, data);
      setState(prev => ({
        ...prev,
        studentPerformance: data,
        isLoading: false,
        lastUpdated: new Date().toISOString()
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }));
    }
  }, [state.filters, getCachedData, setCachedData]);

  const fetchCohortAnalytics = useCallback(async (cohortId: string) => {
    const cacheKey = `cohort_${cohortId}`;
    const cached = getCachedData<CohortAnalytics>(cacheKey);
    if (cached) {
      setState(prev => ({ ...prev, cohortAnalytics: cached }));
      return;
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await fetch(`/api/analytics/cohorts/${cohortId}`);
      if (!response.ok) throw new Error('Failed to fetch cohort analytics');
      
      const data = await response.json();
      setCachedData(cacheKey, data);
      setState(prev => ({
        ...prev,
        cohortAnalytics: data,
        isLoading: false,
        lastUpdated: new Date().toISOString()
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }));
    }
  }, [getCachedData, setCachedData]);

  const refreshAll = useCallback(async () => {
    cacheRef.current.clear();
    await Promise.all([
      fetchExecutionMetrics(),
      fetchLearningMetrics(),
      fetchEngagementMetrics(),
      fetchPerformanceTrends(),
      fetchActivityData(),
      fetchSkillsData(),
      fetchStudentPerformance()
    ]);
  }, [fetchExecutionMetrics, fetchLearningMetrics, fetchEngagementMetrics,
      fetchPerformanceTrends, fetchActivityData, fetchSkillsData, fetchStudentPerformance]);

  // Skill assessment
  const assessSkillLevel = useCallback(async (skillId: string, assessmentData: unknown): Promise<number> => {
    const response = await fetch(`/api/analytics/skills/${skillId}/assess`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(assessmentData)
    });

    if (!response.ok) throw new Error('Failed to assess skill');
    
    const result = await response.json();
    return result.level;
  }, []);

  const getSkillRecommendations = useCallback(async (skillId: string): Promise<string[]> => {
    const response = await fetch(`/api/analytics/skills/${skillId}/recommendations`);
    if (!response.ok) return [];
    return response.json();
  }, []);

  // Reports
  const generateReport = useCallback(async (config: Omit<ReportConfig, 'id'>): Promise<string> => {
    setState(prev => ({ ...prev, generatingReport: true }));

    try {
      const response = await fetch('/api/analytics/reports/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });

      if (!response.ok) throw new Error('Failed to generate report');
      
      const result = await response.json();
      setState(prev => ({
        ...prev,
        generatingReport: false,
        savedReports: [...prev.savedReports, { ...config, id: result.reportId }]
      }));
      
      return result.reportId;
    } catch (error) {
      setState(prev => ({
        ...prev,
        generatingReport: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }));
      throw error;
    }
  }, []);

  const saveReportConfig = useCallback(async (config: ReportConfig) => {
    await fetch('/api/analytics/reports/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });

    setState(prev => ({
      ...prev,
      savedReports: [...prev.savedReports.filter(r => r.id !== config.id), config]
    }));
  }, []);

  const exportReport = useCallback(async (reportId: string, format: 'pdf' | 'csv' | 'json') => {
    const response = await fetch(`/api/analytics/reports/${reportId}/export?format=${format}`);
    if (!response.ok) throw new Error('Failed to export report');
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report_${reportId}.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }, []);

  // Utility functions
  const getDatePreset = useCallback((preset: keyof typeof DATE_PRESETS): DateRange => {
    return DATE_PRESETS[preset]();
  }, []);

  const clearCache = useCallback(() => {
    cacheRef.current.clear();
  }, []);

  const value = useMemo<AnalyticsContextType>(() => ({
    state,
    setDateRange,
    setCohortFilter,
    setCourseFilter,
    setUserFilter,
    setLanguageFilter,
    resetFilters,
    fetchExecutionMetrics,
    fetchLearningMetrics,
    fetchEngagementMetrics,
    fetchPerformanceTrends,
    fetchActivityData,
    fetchSkillsData,
    fetchStudentPerformance,
    fetchCohortAnalytics,
    refreshAll,
    assessSkillLevel,
    getSkillRecommendations,
    generateReport,
    saveReportConfig,
    exportReport,
    getDatePreset,
    clearCache
  }), [state, setDateRange, setCohortFilter, setCourseFilter, setUserFilter, setLanguageFilter,
      resetFilters, fetchExecutionMetrics, fetchLearningMetrics, fetchEngagementMetrics,
      fetchPerformanceTrends, fetchActivityData, fetchSkillsData, fetchStudentPerformance,
      fetchCohortAnalytics, refreshAll, assessSkillLevel, getSkillRecommendations,
      generateReport, saveReportConfig, exportReport, getDatePreset, clearCache]);

  return (
    <AnalyticsContext.Provider value={value}>
      {children}
    </AnalyticsContext.Provider>
  );
}

export function useAnalytics() {
  const context = useContext(AnalyticsContext);
  if (!context) {
    throw new Error('useAnalytics must be used within an AnalyticsProvider');
  }
  return context;
}
