import { useCallback, useState, useRef, useEffect } from 'react';
import {
  LMSProvider,
  LMSCourse,
  LMSStudent,
  LMSAssignment,
  SyncProgress,
  SyncResult,
  RosterMapping,
  OAuthConfig
} from '../contexts/LMSIntegrationContext';

interface UseLMSIntegrationOptions {
  autoFetchCourses?: boolean;
  autoFetchStudents?: boolean;
  onSyncProgress?: (progress: SyncProgress) => void;
  onSyncComplete?: (result: SyncResult) => void;
  onSyncError?: (error: Error) => void;
}

interface UseLMSIntegrationReturn {
  // Provider state
  providers: LMSProvider[];
  selectedProvider: LMSProvider | null;
  isLoading: boolean;
  error: string | null;
  
  // Provider actions
  fetchProviders: () => Promise<void>;
  selectProvider: (provider: LMSProvider) => Promise<void>;
  addProvider: (config: Partial<LMSProvider>) => Promise<LMSProvider>;
  updateProvider: (id: string, updates: Partial<LMSProvider>) => Promise<void>;
  deleteProvider: (id: string) => Promise<void>;
  testConnection: (id: string) => Promise<{ success: boolean; message: string }>;
  
  // OAuth actions
  initiateOAuth: (providerId: string) => void;
  handleOAuthCallback: (code: string, state: string) => Promise<boolean>;
  
  // Course state
  courses: LMSCourse[];
  isLoadingCourses: boolean;
  
  // Course actions
  fetchCourses: () => Promise<void>;
  syncCourse: (courseId: string) => Promise<void>;
  linkCourse: (lmsCourseId: string, localCourseId: string) => Promise<void>;
  unlinkCourse: (lmsCourseId: string) => Promise<void>;
  searchCourses: (query: string) => LMSCourse[];
  
  // Student state
  students: LMSStudent[];
  rosterMappings: RosterMapping[];
  isLoadingStudents: boolean;
  
  // Student actions
  fetchStudents: (courseId?: string) => Promise<void>;
  syncRoster: (courseId: string) => Promise<void>;
  updateRosterMappings: (mappings: RosterMapping[]) => Promise<void>;
  importStudents: (studentIds: string[]) => Promise<{ success: number; failed: number }>;
  matchStudent: (lmsStudentId: string, localUserId: string) => Promise<void>;
  
  // Assignment state
  assignments: LMSAssignment[];
  isLoadingAssignments: boolean;
  
  // Assignment actions
  fetchAssignments: (courseId: string) => Promise<void>;
  syncGrades: (assignmentId: string, grades: { studentId: string; grade: number; feedback?: string }[]) => Promise<void>;
  
  // Sync state
  isSyncing: boolean;
  syncProgress: SyncProgress | null;
  lastSyncResult: SyncResult | null;
  
  // Sync actions
  startFullSync: () => Promise<void>;
  cancelSync: () => Promise<void>;
  bulkSyncCourses: (courseIds: string[]) => Promise<void>;
  reconcileRosters: () => Promise<SyncResult>;
  
  // Utility
  clearError: () => void;
  reset: () => void;
  getProviderStats: () => { totalCourses: number; totalStudents: number; syncedCourses: number };
}

export function useLMSIntegration(options: UseLMSIntegrationOptions = {}): UseLMSIntegrationReturn {
  const {
    autoFetchCourses = true,
    autoFetchStudents = false,
    onSyncProgress,
    onSyncComplete,
    onSyncError
  } = options;

  const [providers, setProviders] = useState<LMSProvider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<LMSProvider | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [courses, setCourses] = useState<LMSCourse[]>([]);
  const [isLoadingCourses, setIsLoadingCourses] = useState(false);
  
  const [students, setStudents] = useState<LMSStudent[]>([]);
  const [rosterMappings, setRosterMappings] = useState<RosterMapping[]>([]);
  const [isLoadingStudents, setIsLoadingStudents] = useState(false);
  
  const [assignments, setAssignments] = useState<LMSAssignment[]>([]);
  const [isLoadingAssignments, setIsLoadingAssignments] = useState(false);
  
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncProgress, setSyncProgress] = useState<SyncProgress | null>(null);
  const [lastSyncResult, setLastSyncResult] = useState<SyncResult | null>(null);

  const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const apiBase = '/api/lms';

  // Fetch all providers
  const fetchProviders = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiBase}/providers`);
      if (!response.ok) throw new Error('Failed to fetch providers');
      
      const data = await response.json();
      setProviders(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch providers');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Select provider and fetch associated data
  const selectProvider = useCallback(async (provider: LMSProvider) => {
    setIsLoading(true);
    setError(null);
    setSelectedProvider(provider);
    
    try {
      // Fetch provider details
      const [providerRes, syncRes] = await Promise.all([
        fetch(`${apiBase}/providers/${provider.id}`),
        fetch(`${apiBase}/providers/${provider.id}/sync-status`)
      ]);
      
      if (!providerRes.ok) throw new Error('Failed to fetch provider details');
      
      const providerData = await providerRes.json();
      const syncData = await syncRes.json().catch(() => ({}));
      
      setSelectedProvider({
        ...provider,
        ...providerData,
        lastSync: syncData.lastSync,
        courseCount: syncData.courseCount,
        studentCount: syncData.studentCount
      });
      
      // Fetch initial data
      if (autoFetchCourses) {
        await fetchCourses();
      }
      if (autoFetchStudents) {
        await fetchStudents();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to select provider');
      setSelectedProvider(null);
    } finally {
      setIsLoading(false);
    }
  }, [autoFetchCourses, autoFetchStudents]);

  // Add new provider
  const addProvider = useCallback(async (config: Partial<LMSProvider>): Promise<LMSProvider> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiBase}/providers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to add provider');
      }
      
      const newProvider = await response.json();
      setProviders(prev => [...prev, newProvider]);
      return newProvider;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add provider');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Update provider
  const updateProvider = useCallback(async (id: string, updates: Partial<LMSProvider>) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiBase}/providers/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
      
      if (!response.ok) throw new Error('Failed to update provider');
      
      const updated = await response.json();
      setProviders(prev => prev.map(p => p.id === id ? updated : p));
      
      if (selectedProvider?.id === id) {
        setSelectedProvider(updated);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update provider');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [selectedProvider]);

  // Delete provider
  const deleteProvider = useCallback(async (id: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiBase}/providers/${id}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) throw new Error('Failed to delete provider');
      
      setProviders(prev => prev.filter(p => p.id !== id));
      
      if (selectedProvider?.id === id) {
        setSelectedProvider(null);
        setCourses([]);
        setStudents([]);
        setAssignments([]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete provider');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [selectedProvider]);

  // Test connection
  const testConnection = useCallback(async (id: string): Promise<{ success: boolean; message: string }> => {
    try {
      const response = await fetch(`${apiBase}/providers/${id}/test`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        return { success: false, message: errorData.message };
      }
      
      const result = await response.json();
      return result;
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Connection test failed' };
    }
  }, []);

  // OAuth flow
  const initiateOAuth = useCallback((providerId: string) => {
    sessionStorage.setItem('lms_oauth_provider', providerId);
    window.location.href = `/api/lms/providers/${providerId}/oauth/initiate`;
  }, []);

  const handleOAuthCallback = useCallback(async (code: string, state: string): Promise<boolean> => {
    const providerId = sessionStorage.getItem('lms_oauth_provider');
    if (!providerId) {
      setError('No OAuth provider found in session');
      return false;
    }

    try {
      const response = await fetch(`${apiBase}/oauth/callback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, state })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.message || 'OAuth failed');
        return false;
      }
      
      const result = await response.json();
      
      if (result.success && selectedProvider?.id === providerId) {
        await updateProvider(providerId, { enabled: true });
      }
      
      sessionStorage.removeItem('lms_oauth_provider');
      return result.success;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'OAuth callback failed');
      return false;
    }
  }, [selectedProvider, updateProvider]);

  // Course management
  const fetchCourses = useCallback(async () => {
    if (!selectedProvider) return;
    
    setIsLoadingCourses(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiBase}/providers/${selectedProvider.id}/courses`);
      if (!response.ok) throw new Error('Failed to fetch courses');
      
      const data = await response.json();
      setCourses(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch courses');
    } finally {
      setIsLoadingCourses(false);
    }
  }, [selectedProvider]);

  const syncCourse = useCallback(async (courseId: string) => {
    if (!selectedProvider) return;
    
    setCourses(prev => prev.map(c => 
      c.id === courseId ? { ...c, syncStatus: 'in_progress' } : c
    ));
    
    try {
      const response = await fetch(
        `${apiBase}/providers/${selectedProvider.id}/courses/${courseId}/sync`,
        { method: 'POST' }
      );
      
      if (!response.ok) throw new Error('Failed to sync course');
      
      setCourses(prev => prev.map(c => 
        c.id === courseId ? { ...c, syncStatus: 'synced', lastSync: new Date().toISOString() } : c
      ));
    } catch (err) {
      setCourses(prev => prev.map(c => 
        c.id === courseId ? { ...c, syncStatus: 'error' } : c
      ));
      throw err;
    }
  }, [selectedProvider]);

  const linkCourse = useCallback(async (lmsCourseId: string, localCourseId: string) => {
    if (!selectedProvider) return;
    
    try {
      const response = await fetch(
        `${apiBase}/providers/${selectedProvider.id}/courses/${lmsCourseId}/link`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ localCourseId })
        }
      );
      
      if (!response.ok) throw new Error('Failed to link course');
      
      setCourses(prev => prev.map(c => 
        c.id === lmsCourseId ? { ...c, syncStatus: 'synced' } : c
      ));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to link course');
      throw err;
    }
  }, [selectedProvider]);

  const unlinkCourse = useCallback(async (lmsCourseId: string) => {
    if (!selectedProvider) return;
    
    try {
      const response = await fetch(
        `${apiBase}/providers/${selectedProvider.id}/courses/${lmsCourseId}/unlink`,
        { method: 'POST' }
      );
      
      if (!response.ok) throw new Error('Failed to unlink course');
      
      setCourses(prev => prev.map(c => 
        c.id === lmsCourseId ? { ...c, syncStatus: 'pending' } : c
      ));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to unlink course');
      throw err;
    }
  }, [selectedProvider]);

  const searchCourses = useCallback((query: string): LMSCourse[] => {
    const lowerQuery = query.toLowerCase();
    return courses.filter(c => 
      c.name.toLowerCase().includes(lowerQuery) ||
      c.code.toLowerCase().includes(lowerQuery)
    );
  }, [courses]);

  // Student management
  const fetchStudents = useCallback(async (courseId?: string) => {
    if (!selectedProvider) return;
    
    setIsLoadingStudents(true);
    setError(null);
    
    try {
      const url = courseId
        ? `${apiBase}/providers/${selectedProvider.id}/courses/${courseId}/students`
        : `${apiBase}/providers/${selectedProvider.id}/students`;
      
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch students');
      
      const data = await response.json();
      setStudents(data);
      
      // Fetch roster mappings
      const mappingsRes = await fetch(`${apiBase}/providers/${selectedProvider.id}/roster/mappings`);
      if (mappingsRes.ok) {
        const mappings = await mappingsRes.json();
        setRosterMappings(mappings);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch students');
    } finally {
      setIsLoadingStudents(false);
    }
  }, [selectedProvider]);

  const syncRoster = useCallback(async (courseId: string) => {
    if (!selectedProvider) return;
    
    setIsSyncing(true);
    setSyncProgress({
      current: 0,
      total: 100,
      status: 'Starting roster sync...',
      errors: [],
      startTime: new Date().toISOString()
    });
    
    try {
      // Start sync
      const startRes = await fetch(
        `${apiBase}/providers/${selectedProvider.id}/courses/${courseId}/roster/sync`,
        { method: 'POST' }
      );
      
      if (!startRes.ok) throw new Error('Failed to start roster sync');
      
      // Poll for progress
      pollIntervalRef.current = setInterval(async () => {
        const progressRes = await fetch(`${apiBase}/providers/${selectedProvider.id}/sync/progress`);
        
        if (progressRes.ok) {
          const progress = await progressRes.json();
          setSyncProgress(progress);
          onSyncProgress?.(progress);
          
          if (progress.status === 'completed') {
            clearInterval(pollIntervalRef.current!);
            setIsSyncing(false);
            setLastSyncResult(progress.result);
            onSyncComplete?.(progress.result);
            await fetchStudents(courseId);
          } else if (progress.status === 'failed') {
            clearInterval(pollIntervalRef.current!);
            setIsSyncing(false);
            const error = new Error(progress.errors?.[0] || 'Sync failed');
            onSyncError?.(error);
          }
        }
      }, 1000);
    } catch (err) {
      setIsSyncing(false);
      const error = err instanceof Error ? err : new Error('Failed to sync roster');
      onSyncError?.(error);
      throw error;
    }
  }, [selectedProvider, onSyncProgress, onSyncComplete, onSyncError, fetchStudents]);

  const updateRosterMappings = useCallback(async (mappings: RosterMapping[]) => {
    if (!selectedProvider) return;
    
    try {
      const response = await fetch(`${apiBase}/providers/${selectedProvider.id}/roster/mappings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mappings })
      });
      
      if (!response.ok) throw new Error('Failed to update roster mappings');
      
      setRosterMappings(mappings);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update roster mappings');
      throw err;
    }
  }, [selectedProvider]);

  const importStudents = useCallback(async (studentIds: string[]): Promise<{ success: number; failed: number }> => {
    if (!selectedProvider) return { success: 0, failed: 0 };
    
    try {
      const response = await fetch(`${apiBase}/providers/${selectedProvider.id}/students/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ studentIds })
      });
      
      if (!response.ok) throw new Error('Failed to import students');
      
      const result = await response.json();
      await fetchStudents();
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to import students');
      throw err;
    }
  }, [selectedProvider, fetchStudents]);

  const matchStudent = useCallback(async (lmsStudentId: string, localUserId: string) => {
    if (!selectedProvider) return;
    
    try {
      const response = await fetch(
        `${apiBase}/providers/${selectedProvider.id}/roster/match`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ lmsStudentId, localUserId })
        }
      );
      
      if (!response.ok) throw new Error('Failed to match student');
      
      setRosterMappings(prev =>
        prev.map(m => m.lmsStudentId === lmsStudentId ? { ...m, localUserId, status: 'matched' } : m)
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to match student');
      throw err;
    }
  }, [selectedProvider]);

  // Assignment management
  const fetchAssignments = useCallback(async (courseId: string) => {
    if (!selectedProvider) return;
    
    setIsLoadingAssignments(true);
    setError(null);
    
    try {
      const response = await fetch(
        `${apiBase}/providers/${selectedProvider.id}/courses/${courseId}/assignments`
      );
      
      if (!response.ok) throw new Error('Failed to fetch assignments');
      
      const data = await response.json();
      setAssignments(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch assignments');
    } finally {
      setIsLoadingAssignments(false);
    }
  }, [selectedProvider]);

  const syncGrades = useCallback(async (
    assignmentId: string,
    grades: { studentId: string; grade: number; feedback?: string }[]
  ) => {
    if (!selectedProvider) return;
    
    try {
      const response = await fetch(
        `${apiBase}/providers/${selectedProvider.id}/assignments/${assignmentId}/grades`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ grades })
        }
      );
      
      if (!response.ok) throw new Error('Failed to sync grades');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to sync grades');
      throw err;
    }
  }, [selectedProvider]);

  // Sync operations
  const startFullSync = useCallback(async () => {
    if (!selectedProvider) return;
    
    setIsSyncing(true);
    setSyncProgress({
      current: 0,
      total: 100,
      status: 'Initializing full sync...',
      errors: [],
      startTime: new Date().toISOString()
    });
    
    try {
      const startRes = await fetch(`${apiBase}/providers/${selectedProvider.id}/sync`, {
        method: 'POST'
      });
      
      if (!startRes.ok) throw new Error('Failed to start sync');
      
      pollIntervalRef.current = setInterval(async () => {
        const progressRes = await fetch(`${apiBase}/providers/${selectedProvider.id}/sync/progress`);
        
        if (progressRes.ok) {
          const progress = await progressRes.json();
          setSyncProgress(progress);
          onSyncProgress?.(progress);
          
          if (progress.status === 'completed') {
            clearInterval(pollIntervalRef.current!);
            setIsSyncing(false);
            setLastSyncResult(progress.result);
            onSyncComplete?.(progress.result);
            
            // Refresh data
            await Promise.all([fetchCourses(), fetchStudents()]);
          } else if (progress.status === 'failed') {
            clearInterval(pollIntervalRef.current!);
            setIsSyncing(false);
            const error = new Error(progress.errors?.[0] || 'Sync failed');
            onSyncError?.(error);
          }
        }
      }, 1000);
    } catch (err) {
      setIsSyncing(false);
      const error = err instanceof Error ? err : new Error('Sync failed');
      onSyncError?.(error);
      throw error;
    }
  }, [selectedProvider, onSyncProgress, onSyncComplete, onSyncError, fetchCourses, fetchStudents]);

  const cancelSync = useCallback(async () => {
    if (!selectedProvider) return;
    
    try {
      await fetch(`${apiBase}/providers/${selectedProvider.id}/sync/cancel`, {
        method: 'POST'
      });
      
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
      
      setIsSyncing(false);
      setSyncProgress(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to cancel sync');
    }
  }, [selectedProvider]);

  const bulkSyncCourses = useCallback(async (courseIds: string[]) => {
    if (!selectedProvider) return;
    
    try {
      const response = await fetch(`${apiBase}/providers/${selectedProvider.id}/courses/bulk-sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ courseIds })
      });
      
      if (!response.ok) throw new Error('Failed to bulk sync courses');
      
      // Update course statuses
      setCourses(prev => prev.map(c => 
        courseIds.includes(c.id) ? { ...c, syncStatus: 'in_progress' } : c
      ));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to bulk sync courses');
      throw err;
    }
  }, [selectedProvider]);

  const reconcileRosters = useCallback(async (): Promise<SyncResult> => {
    if (!selectedProvider) throw new Error('No provider selected');
    
    try {
      const response = await fetch(`${apiBase}/providers/${selectedProvider.id}/roster/reconcile`, {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error('Failed to reconcile rosters');
      
      const result = await response.json();
      await fetchStudents();
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reconcile rosters');
      throw err;
    }
  }, [selectedProvider, fetchStudents]);

  // Utility functions
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const reset = useCallback(() => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }
    
    setSelectedProvider(null);
    setCourses([]);
    setStudents([]);
    setAssignments([]);
    setRosterMappings([]);
    setSyncProgress(null);
    setLastSyncResult(null);
    setError(null);
    setIsSyncing(false);
  }, []);

  const getProviderStats = useCallback(() => ({
    totalCourses: courses.length,
    totalStudents: students.length,
    syncedCourses: courses.filter(c => c.syncStatus === 'synced').length
  }), [courses, students]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  return {
    providers,
    selectedProvider,
    isLoading,
    error,
    fetchProviders,
    selectProvider,
    addProvider,
    updateProvider,
    deleteProvider,
    testConnection,
    initiateOAuth,
    handleOAuthCallback,
    courses,
    isLoadingCourses,
    fetchCourses,
    syncCourse,
    linkCourse,
    unlinkCourse,
    searchCourses,
    students,
    rosterMappings,
    isLoadingStudents,
    fetchStudents,
    syncRoster,
    updateRosterMappings,
    importStudents,
    matchStudent,
    assignments,
    isLoadingAssignments,
    fetchAssignments,
    syncGrades,
    isSyncing,
    syncProgress,
    lastSyncResult,
    startFullSync,
    cancelSync,
    bulkSyncCourses,
    reconcileRosters,
    clearError,
    reset,
    getProviderStats
  };
}

