import { useCallback, useState, useEffect } from 'react';
import { useAnalytics, ExecutionMetric, LearningMetric, EngagementMetric, PerformanceTrend, ActivityDataPoint, StudentPerformance, CohortAnalytics, DateRange } from '../contexts/AnalyticsContext';

interface UsePerformanceMetricsOptions {
  userId?: string;
  language?: string;
  autoFetch?: boolean;
}

interface UsePerformanceMetricsReturn {
  // Metrics
  executionMetrics: ExecutionMetric | null;
  learningMetrics: LearningMetric[];
  performanceTrends: PerformanceTrend[];
  
  // Computed stats
  totalExecutions: number;
  overallSuccessRate: number;
  avgRuntime: number;
  topLanguage: string;
  mostCommonError: string | null;
  
  // State
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
  
  // Actions
  refresh: () => Promise<void>;
  getLanguageStats: (language: string) => ExecutionMetric | undefined;
  getTrendForDate: (date: string) => PerformanceTrend | undefined;
}

export function usePerformanceMetrics(options: UsePerformanceMetricsOptions = {}): UsePerformanceMetricsReturn {
  const { userId, language, autoFetch = true } = options;

  const [totalExecutions, setTotalExecutions] = useState(0);
  const [overallSuccessRate, setOverallSuccessRate] = useState(0);
  const [avgRuntime, setAvgRuntime] = useState(0);
  const [topLanguage, setTopLanguage] = useState('');
  const [mostCommonError, setMostCommonError] = useState<string | null>(null);

  const {
    state,
    setUserFilter,
    setLanguageFilter,
    fetchExecutionMetrics,
    fetchLearningMetrics,
    fetchPerformanceTrends,
    refresh
  } = useAnalytics();

  // Set filters
  useEffect(() => {
    if (userId) setUserFilter(userId);
    if (language) setLanguageFilter(language);
  }, [userId, language, setUserFilter, setLanguageFilter]);

  // Auto-fetch
  useEffect(() => {
    if (autoFetch) {
      Promise.all([
        fetchExecutionMetrics(),
        fetchLearningMetrics(),
        fetchPerformanceTrends()
      ]);
    }
  }, [autoFetch, fetchExecutionMetrics, fetchLearningMetrics, fetchPerformanceTrends]);

  // Compute aggregated stats
  useEffect(() => {
    if (state.executionMetrics) {
      const metrics = state.executionMetrics;
      setTotalExecutions(metrics.totalRuns);
      setOverallSuccessRate(metrics.successRate);
      setAvgRuntime(metrics.avgRuntimeMs);
      setMostCommonError(metrics.commonErrors[0]?.error || null);
    }
  }, [state.executionMetrics]);

  // Find top language
  useEffect(() => {
    // This would be computed from comprehensive data
    // For now, use the current metric's language
    if (state.executionMetrics) {
      setTopLanguage(state.executionMetrics.language);
    }
  }, [state.executionMetrics]);

  // Get stats for specific language
  const getLanguageStats = useCallback((lang: string) => {
    // Would fetch language-specific data
    return state.executionMetrics?.language === lang ? state.executionMetrics : undefined;
  }, [state.executionMetrics]);

  // Get trend for specific date
  const getTrendForDate = useCallback((date: string) => {
    return state.performanceTrends.find(t => t.date === date);
  }, [state.performanceTrends]);

  return {
    executionMetrics: state.executionMetrics,
    learningMetrics: state.learningMetrics,
    performanceTrends: state.performanceTrends,
    totalExecutions,
    overallSuccessRate,
    avgRuntime,
    topLanguage,
    mostCommonError,
    isLoading: state.isLoading,
    error: state.error,
    lastUpdated: state.lastUpdated,
    refresh,
    getLanguageStats,
    getTrendForDate
  };
}

interface UseEngagementDataOptions {
  cohortId?: string;
  dateRange?: DateRange;
  autoFetch?: boolean;
}

interface UseEngagementDataReturn {
  // Metrics
  engagementMetrics: EngagementMetric | null;
  activityData: ActivityDataPoint[];
  
  // Computed metrics
  dailyActiveUsers: number;
  weeklyActiveUsers: number;
  monthlyActiveUsers: number;
  avgSessionMinutes: number;
  completionRate: number;
  
  // Activity stats
  totalActivityCount: number;
  avgDailyActivity: number;
  peakActivityDay: ActivityDataPoint | null;
  
  // State
  isLoading: boolean;
  error: string | null;
  
  // Actions
  refresh: () => Promise<void>;
  getActivityForDate: (date: string) => ActivityDataPoint | undefined;
  getActivityChange: () => number;
}

export function useEngagementData(options: UseEngagementDataOptions = {}): UseEngagementDataReturn {
  const { cohortId, dateRange, autoFetch = true } = options;

  const [dailyActiveUsers, setDailyActiveUsers] = useState(0);
  const [weeklyActiveUsers, setWeeklyActiveUsers] = useState(0);
  const [monthlyActiveUsers, setMonthlyActiveUsers] = useState(0);
  const [avgSessionMinutes, setAvgSessionMinutes] = useState(0);
  const [completionRate, setCompletionRate] = useState(0);
  const [totalActivityCount, setTotalActivityCount] = useState(0);
  const [avgDailyActivity, setAvgDailyActivity] = useState(0);
  const [peakActivityDay, setPeakActivityDay] = useState<ActivityDataPoint | null>(null);

  const {
    state,
    setCohortFilter,
    setDateRange,
    fetchEngagementMetrics,
    fetchActivityData,
    refresh
  } = useAnalytics();

  // Set filters
  useEffect(() => {
    if (cohortId) setCohortFilter(cohortId);
    if (dateRange) setDateRange(dateRange);
  }, [cohortId, dateRange, setCohortFilter, setDateRange]);

  // Auto-fetch
  useEffect(() => {
    if (autoFetch) {
      Promise.all([
        fetchEngagementMetrics(),
        fetchActivityData()
      ]);
    }
  }, [autoFetch, fetchEngagementMetrics, fetchActivityData]);

  // Compute metrics from engagement data
  useEffect(() => {
    if (state.engagementMetrics) {
      const metrics = state.engagementMetrics;
      setDailyActiveUsers(metrics.dailyActiveUsers);
      setWeeklyActiveUsers(metrics.weeklyActiveUsers);
      setMonthlyActiveUsers(metrics.monthlyActiveUsers);
      setAvgSessionMinutes(Math.round(metrics.avgSessionDuration / 60));
      setCompletionRate(metrics.completionRate * 100);
    }
  }, [state.engagementMetrics]);

  // Compute activity stats
  useEffect(() => {
    if (state.activityData.length > 0) {
      const total = state.activityData.reduce((sum, d) => sum + d.value, 0);
      setTotalActivityCount(total);
      setAvgDailyActivity(Math.round(total / state.activityData.length));
      
      const peak = state.activityData.reduce((max, d) => 
        d.value > (max?.value || 0) ? d : max
      , null as ActivityDataPoint | null);
      setPeakActivityDay(peak);
    }
  }, [state.activityData]);

  // Get activity for specific date
  const getActivityForDate = useCallback((date: string) => {
    return state.activityData.find(d => d.date === date);
  }, [state.activityData]);

  // Calculate change from previous period
  const getActivityChange = useCallback(() => {
    if (state.activityData.length < 2) return 0;
    
    const midpoint = Math.floor(state.activityData.length / 2);
    const firstHalf = state.activityData.slice(0, midpoint);
    const secondHalf = state.activityData.slice(midpoint);
    
    const firstTotal = firstHalf.reduce((sum, d) => sum + d.value, 0);
    const secondTotal = secondHalf.reduce((sum, d) => sum + d.value, 0);
    
    if (firstTotal === 0) return 0;
    return ((secondTotal - firstTotal) / firstTotal) * 100;
  }, [state.activityData]);

  return {
    engagementMetrics: state.engagementMetrics,
    activityData: state.activityData,
    dailyActiveUsers,
    weeklyActiveUsers,
    monthlyActiveUsers,
    avgSessionMinutes,
    completionRate,
    totalActivityCount,
    avgDailyActivity,
    peakActivityDay,
    isLoading: state.isLoading,
    error: state.error,
    refresh,
    getActivityForDate,
    getActivityChange
  };
}

interface UseStudentAnalyticsOptions {
  cohortId?: string;
  courseId?: string;
  autoFetch?: boolean;
  riskThreshold?: number;
}

interface UseStudentAnalyticsReturn {
  // Students
  students: StudentPerformance[];
  atRiskStudents: StudentPerformance[];
  topPerformers: StudentPerformance[];
  
  // Statistics
  avgScore: number;
  avgCompletion: number;
  atRiskCount: number;
  totalStudents: number;
  
  // State
  isLoading: boolean;
  error: string | null;
  
  // Actions
  refresh: () => Promise<void>;
  getStudentById: (userId: string) => StudentPerformance | undefined;
  getStudentsByRisk: (level: 'low' | 'medium' | 'high') => StudentPerformance[];
  sortBy: (field: keyof StudentPerformance, direction?: 'asc' | 'desc') => StudentPerformance[];
}

export function useStudentAnalytics(options: UseStudentAnalyticsOptions = {}): UseStudentAnalyticsReturn {
  const { cohortId, courseId, autoFetch = true, riskThreshold = 70 } = options;

  const [avgScore, setAvgScore] = useState(0);
  const [avgCompletion, setAvgCompletion] = useState(0);
  const [atRiskCount, setAtRiskCount] = useState(0);
  const [totalStudents, setTotalStudents] = useState(0);

  const {
    state,
    setCohortFilter,
    setCourseFilter,
    fetchStudentPerformance,
    refresh
  } = useAnalytics();

  // Set filters
  useEffect(() => {
    if (cohortId) setCohortFilter(cohortId);
    if (courseId) setCourseFilter(courseId);
  }, [cohortId, courseId, setCohortFilter, setCourseFilter]);

  // Auto-fetch
  useEffect(() => {
    if (autoFetch && (cohortId || courseId)) {
      fetchStudentPerformance();
    }
  }, [autoFetch, cohortId, courseId, fetchStudentPerformance]);

  // Compute statistics
  useEffect(() => {
    const students = state.studentPerformance;
    setTotalStudents(students.length);
    
    if (students.length > 0) {
      const avgScoreCalc = students.reduce((sum, s) => sum + s.avgScore, 0) / students.length;
      const avgCompletionCalc = students.reduce((sum, s) => sum + s.completionRate, 0) / students.length;
      
      setAvgScore(Math.round(avgScoreCalc));
      setAvgCompletion(Math.round(avgCompletionCalc * 100));
      setAtRiskCount(students.filter(s => s.riskLevel === 'high').length);
    }
  }, [state.studentPerformance]);

  // Filter students
  const atRiskStudents = state.studentPerformance.filter(s => s.riskLevel === 'high');
  const topPerformers = [...state.studentPerformance]
    .sort((a, b) => b.avgScore - a.avgScore)
    .slice(0, 10);

  // Get student by ID
  const getStudentById = useCallback((userId: string) => {
    return state.studentPerformance.find(s => s.userId === userId);
  }, [state.studentPerformance]);

  // Get students by risk level
  const getStudentsByRisk = useCallback((level: 'low' | 'medium' | 'high') => {
    return state.studentPerformance.filter(s => s.riskLevel === level);
  }, [state.studentPerformance]);

  // Sort students
  const sortBy = useCallback((field: keyof StudentPerformance, direction: 'asc' | 'desc' = 'desc') => {
    return [...state.studentPerformance].sort((a, b) => {
      const aVal = a[field];
      const bVal = b[field];
      
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return direction === 'asc' ? aVal - bVal : bVal - aVal;
      }
      
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return direction === 'asc' 
          ? aVal.localeCompare(bVal) 
          : bVal.localeCompare(aVal);
      }
      
      return 0;
    });
  }, [state.studentPerformance]);

  return {
    students: state.studentPerformance,
    atRiskStudents,
    topPerformers,
    avgScore,
    avgCompletion,
    atRiskCount,
    totalStudents,
    isLoading: state.isLoading,
    error: state.error,
    refresh,
    getStudentById,
    getStudentsByRisk,
    sortBy
  };
}

import { useCallback, useState, useEffect } from 'react';
