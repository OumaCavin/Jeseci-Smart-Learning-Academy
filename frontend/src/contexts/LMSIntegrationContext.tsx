import { useCallback, useEffect, useRef, useState, useMemo } from 'react';

// Types for LMS Integration
export interface LMSProvider {
  id: string;
  name: string;
  type: 'canvas' | 'blackboard' | 'moodle' | 'brightspace' | 'custom';
  baseUrl: string;
  apiVersion: string;
  authType: 'oauth2' | 'apikey' | 'basic';
  enabled: boolean;
  lastSync?: string;
  courseCount?: number;
  studentCount?: number;
}

export interface LMSCourse {
  id: string;
  externalId: string;
  name: string;
  code: string;
  description?: string;
  term?: string;
  enrollmentCount: number;
  status: 'active' | 'inactive' | 'archived';
  lastSync?: string;
  syncStatus: 'synced' | 'pending' | 'error' | 'in_progress';
}

export interface LMSStudent {
  id: string;
  externalId: string;
  email: string;
  firstName: string;
  lastName: string;
  enrollmentStatus: 'enrolled' | 'dropped' | 'pending';
  enrollmentDate?: string;
  lastActivity?: string;
}

export interface LMSAssignment {
  id: string;
  courseId: string;
  title: string;
  description?: string;
  dueDate?: string;
  pointsPossible: number;
  submissionType: 'online' | 'file_upload' | 'text_entry' | 'external_tool';
  status: 'published' | 'draft' | 'deleted';
}

export interface SyncProgress {
  current: number;
  total: number;
  status: string;
  errors: SyncError[];
  startTime: string;
  estimatedCompletion?: string;
}

export interface SyncError {
  item: string;
  error: string;
  timestamp: string;
  retryable: boolean;
}

export interface GradeSync {
  studentId: string;
  grade: number;
  feedback?: string;
}

export interface LMSIntegrationState {
  // Provider state
  providers: LMSProvider[];
  selectedProvider: LMSProvider | null;
  isConnecting: boolean;
  connectionError: string | null;
  
  // Sync state
  isSyncing: boolean;
  syncProgress: SyncProgress | null;
  lastSyncResult: SyncResult | null;
  
  // Data state
  courses: LMSCourse[];
  students: LMSStudent[];
  assignments: LMSAssignment[];
  
  // Roster management
  rosterMappings: RosterMapping[];
  pendingRosterChanges: number;
}

export interface SyncResult {
  success: boolean;
  coursesCreated: number;
  coursesUpdated: number;
  studentsImported: number;
  enrollmentsProcessed: number;
  errors: string[];
  duration: number;
}

export interface RosterMapping {
  lmsStudentId: string;
  localUserId: string;
  email: string;
  firstName: string;
  lastName: string;
  status: 'matched' | 'unmatched' | 'conflict' | 'pending';
}

export interface OAuthConfig {
  clientId: string;
  redirectUri: string;
  scope: string[];
  authUrl: string;
  tokenUrl: string;
}

export interface LMSIntegrationContextType {
  // Provider management
  providers: LMSProvider[];
  selectedProvider: LMSProvider | null;
  fetchProviders: () => Promise<void>;
  selectProvider: (provider: LMSProvider) => Promise<void>;
  addProvider: (config: Partial<LMSProvider>) => Promise<LMSProvider>;
  updateProvider: (id: string, updates: Partial<LMSProvider>) => Promise<void>;
  deleteProvider: (id: string) => Promise<void>;
  testConnection: (id: string) => Promise<{ success: boolean; message: string }>;
  
  // OAuth flow
  initiateOAuth: (providerId: string) => Promise<void>;
  handleOAuthCallback: (code: string, state: string) => Promise<boolean>;
  getOAuthConfig: (providerId: string) => Promise<OAuthConfig | null>;
  
  // Course management
  courses: LMSCourse[];
  fetchCourses: (providerId: string) => Promise<void>;
  syncCourse: (courseId: string) => Promise<void>;
  linkCourse: (lmsCourseId: string, localCourseId: string) => Promise<void>;
  unlinkCourse: (lmsCourseId: string) => Promise<void>;
  
  // Student/roster management
  students: LMSStudent[];
  rosterMappings: RosterMapping[];
  fetchStudents: (providerId: string, courseId?: string) => Promise<void>;
  syncRoster: (providerId: string, courseId: string) => Promise<SyncResult>;
  updateRosterMapping: (mappings: RosterMapping[]) => Promise<void>;
  importStudents: (studentIds: string[]) => Promise<{ success: number; failed: number }>;
  
  // Assignment management
  assignments: LMSAssignment[];
  fetchAssignments: (providerId: string, courseId: string) => Promise<void>;
  syncAssignmentGrades: (assignmentId: string, grades: GradeSync[]) => Promise<void>;
  
  // Sync operations
  isSyncing: boolean;
  syncProgress: SyncProgress | null;
  lastSyncResult: SyncResult | null;
  startFullSync: (providerId: string) => Promise<void>;
  cancelSync: () => Promise<void>;
  
  // Bulk operations
  bulkSyncCourses: (courseIds: string[]) => Promise<void>;
  bulkImportStudents: (providerId: string, studentIds: string[]) => Promise<SyncResult>;
  reconcileRosters: (providerId: string) => Promise<SyncResult>;
  
  // Utility
  clearError: () => void;
  resetIntegration: () => void;
  exportConfiguration: (providerId: string) => Promise<string>;
  importConfiguration: (config: string) => Promise<boolean>;
}

const LMSIntegrationContext = createContext<LMSIntegrationContextType | null>(null);

export function LMSIntegrationProvider({ children }: { children: React.ReactNode }) {
  const [providers, setProviders] = useState<LMSProvider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<LMSProvider | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncProgress, setSyncProgress] = useState<SyncProgress | null>(null);
  const [lastSyncResult, setLastSyncResult] = useState<SyncResult | null>(null);
  
  const [courses, setCourses] = useState<LMSCourse[]>([]);
  const [students, setStudents] = useState<LMSStudent[]>([]);
  const [assignments, setAssignments] = useState<LMSAssignment[]>([]);
  
  const [rosterMappings, setRosterMappings] = useState<RosterMapping[]>([]);
  const [pendingRosterChanges, setPendingRosterChanges] = useState(0);

  // API base URL
  const apiBase = '/api/lms';

  // Fetch all providers
  const fetchProviders = useCallback(async () => {
    try {
      const response = await fetch(`${apiBase}/providers`);
      if (!response.ok) throw new Error('Failed to fetch providers');
      const data = await response.json();
      setProviders(data);
    } catch (error) {
      setConnectionError(error instanceof Error ? error.message : 'Failed to fetch providers');
    }
  }, []);

  // Select and configure provider
  const selectProvider = useCallback(async (provider: LMSProvider) => {
    setIsConnecting(true);
    setConnectionError(null);
    try {
      // Fetch provider details and sync status
      const [providerRes, syncRes] = await Promise.all([
        fetch(`${apiBase}/providers/${provider.id}`),
        fetch(`${apiBase}/providers/${provider.id}/sync-status`)
      ]);
      
      if (!providerRes.ok) throw new Error('Failed to fetch provider details');
      
      const providerData = await providerRes.json();
      const syncData = await syncRes.json();
      
      const updatedProvider: LMSProvider = {
        ...provider,
        ...providerData,
        lastSync: syncData.lastSync,
        courseCount: syncData.courseCount,
        studentCount: syncData.studentCount
      };
      
      setSelectedProvider(updatedProvider);
      
      // Fetch initial data
      await Promise.all([
        fetchCourses(provider.id),
        fetchStudents(provider.id)
      ]);
    } catch (error) {
      setConnectionError(error instanceof Error ? error.message : 'Failed to select provider');
    } finally {
      setIsConnecting(false);
    }
  }, []);

  // Add new provider
  const addProvider = useCallback(async (config: Partial<LMSProvider>): Promise<LMSProvider> => {
    const response = await fetch(`${apiBase}/providers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to add provider');
    }
    
    const newProvider = await response.json();
    setProviders(prev => [...prev, newProvider]);
    return newProvider;
  }, []);

  // Update provider
  const updateProvider = useCallback(async (id: string, updates: Partial<LMSProvider>) => {
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
  }, [selectedProvider]);

  // Delete provider
  const deleteProvider = useCallback(async (id: string) => {
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
  }, [selectedProvider]);

  // Test connection
  const testConnection = useCallback(async (id: string): Promise<{ success: boolean; message: string }> => {
    const response = await fetch(`${apiBase}/providers/${id}/test`, {
      method: 'POST'
    });
    
    if (!response.ok) {
      const error = await response.json();
      return { success: false, message: error.message };
    }
    
    const result = await response.json();
    return result;
  }, []);

  // OAuth flow
  const initiateOAuth = useCallback(async (providerId: string) => {
    const response = await fetch(`${apiBase}/providers/${providerId}/oauth/initiate`, {
      method: 'POST'
    });
    
    if (!response.ok) throw new Error('Failed to initiate OAuth');
    
    const { authUrl, state } = await response.json();
    
    // Store state for verification
    sessionStorage.setItem('lms_oauth_state', state);
    
    // Redirect to OAuth provider
    window.location.href = authUrl;
  }, []);

  const handleOAuthCallback = useCallback(async (code: string, state: string): Promise<boolean> => {
    const storedState = sessionStorage.getItem('lms_oauth_state');
    
    if (state !== storedState) {
      setConnectionError('Invalid OAuth state. Please try again.');
      return false;
    }
    
    sessionStorage.removeItem('lms_oauth_state');
    
    try {
      const response = await fetch(`${apiBase}/oauth/callback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, state })
      });
      
      if (!response.ok) throw new Error('OAuth callback failed');
      
      const result = await response.json();
      
      if (selectedProvider) {
        await updateProvider(selectedProvider.id, { enabled: true });
      }
      
      return result.success;
    } catch (error) {
      setConnectionError(error instanceof Error ? error.message : 'OAuth failed');
      return false;
    }
  }, [selectedProvider, updateProvider]);

  const getOAuthConfig = useCallback(async (providerId: string): Promise<OAuthConfig | null> => {
    const response = await fetch(`${apiBase}/providers/${providerId}/oauth/config`);
    if (!response.ok) return null;
    return response.json();
  }, []);

  // Course management
  const fetchCourses = useCallback(async (providerId: string) => {
    const response = await fetch(`${apiBase}/providers/${providerId}/courses`);
    if (!response.ok) throw new Error('Failed to fetch courses');
    const data = await response.json();
    setCourses(data);
  }, []);

  const syncCourse = useCallback(async (courseId: string) => {
    if (!selectedProvider) return;
    
    setCourses(prev => prev.map(c => 
      c.id === courseId ? { ...c, syncStatus: 'in_progress' as const } : c
    ));
    
    try {
      const response = await fetch(`${apiBase}/providers/${selectedProvider.id}/courses/${courseId}/sync`, {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error('Failed to sync course');
      
      setCourses(prev => prev.map(c => 
        c.id === courseId ? { ...c, syncStatus: 'synced' as const, lastSync: new Date().toISOString() } : c
      ));
    } catch (error) {
      setCourses(prev => prev.map(c => 
        c.id === courseId ? { ...c, syncStatus: 'error' as const } : c
      ));
      throw error;
    }
  }, [selectedProvider]);

  const linkCourse = useCallback(async (lmsCourseId: string, localCourseId: string) => {
    if (!selectedProvider) return;
    
    const response = await fetch(`${apiBase}/providers/${selectedProvider.id}/courses/${lmsCourseId}/link`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ localCourseId })
    });
    
    if (!response.ok) throw new Error('Failed to link course');
    
    setCourses(prev => prev.map(c => 
      c.id === lmsCourseId ? { ...c, syncStatus: 'synced' as const } : c
    ));
  }, [selectedProvider]);

  const unlinkCourse = useCallback(async (lmsCourseId: string) => {
    if (!selectedProvider) return;
    
    const response = await fetch(`${apiBase}/providers/${selectedProvider.id}/courses/${lmsCourseId}/unlink`, {
      method: 'POST'
    });
    
    if (!response.ok) throw new Error('Failed to unlink course');
    
    setCourses(prev => prev.map(c => 
      c.id === lmsCourseId ? { ...c, syncStatus: 'pending' as const } : c
    ));
  }, [selectedProvider]);

  // Student management
  const fetchStudents = useCallback(async (providerId: string, courseId?: string) => {
    const url = courseId 
      ? `${apiBase}/providers/${providerId}/courses/${courseId}/students`
      : `${apiBase}/providers/${providerId}/students`;
    
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch students');
    const data = await response.json();
    setStudents(data);
  }, []);

  const syncRoster = useCallback(async (providerId: string, courseId: string): Promise<SyncResult> => {
    setIsSyncing(true);
    setSyncProgress({
      current: 0,
      total: 100,
      status: 'Starting roster sync...',
      errors: [],
      startTime: new Date().toISOString()
    });
    
    try {
      const response = await fetch(`${apiBase}/providers/${providerId}/courses/${courseId}/roster/sync`, {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error('Failed to sync roster');
      
      // Poll for progress
      const pollInterval = setInterval(async () => {
        const progressRes = await fetch(`${apiBase}/providers/${providerId}/sync/progress`);
        if (progressRes.ok) {
          const progress = await progressRes.json();
          setSyncProgress(progress);
          
          if (progress.status === 'completed' || progress.status === 'failed') {
            clearInterval(pollInterval);
            setIsSyncing(false);
            
            if (progress.status === 'completed') {
              setLastSyncResult(progress.result);
              await fetchStudents(providerId, courseId);
            }
          }
        }
      }, 1000);
      
      // Set timeout for polling
      setTimeout(() => {
        clearInterval(pollInterval);
        if (isSyncing) {
          setIsSyncing(false);
        }
      }, 60000);
      
      return { success: true, coursesCreated: 0, coursesUpdated: 0, studentsImported: 0, enrollmentsProcessed: 0, errors: [], duration: 0 };
    } catch (error) {
      setIsSyncing(false);
      throw error;
    }
  }, [fetchStudents]);

  const updateRosterMapping = useCallback(async (mappings: RosterMapping[]) => {
    if (!selectedProvider) return;
    
    const response = await fetch(`${apiBase}/providers/${selectedProvider.id}/roster/mappings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mappings })
    });
    
    if (!response.ok) throw new Error('Failed to update roster mappings');
    
    setRosterMappings(mappings);
    setPendingRosterChanges(0);
  }, [selectedProvider]);

  const importStudents = useCallback(async (studentIds: string[]): Promise<{ success: number; failed: number }> => {
    if (!selectedProvider) return { success: 0, failed: 0 };
    
    const response = await fetch(`${apiBase}/providers/${selectedProvider.id}/students/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ studentIds })
    });
    
    if (!response.ok) throw new Error('Failed to import students');
    
    const result = await response.json();
    await fetchStudents(selectedProvider.id);
    return result;
  }, [selectedProvider, fetchStudents]);

  // Assignment management
  const fetchAssignments = useCallback(async (providerId: string, courseId: string) => {
    const response = await fetch(`${apiBase}/providers/${providerId}/courses/${courseId}/assignments`);
    if (!response.ok) throw new Error('Failed to fetch assignments');
    const data = await response.json();
    setAssignments(data);
  }, []);

  const syncAssignmentGrades = useCallback(async (assignmentId: string, grades: GradeSync[]) => {
    if (!selectedProvider) return;
    
    const response = await fetch(`${apiBase}/providers/${selectedProvider.id}/assignments/${assignmentId}/grades`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ grades })
    });
    
    if (!response.ok) throw new Error('Failed to sync grades');
  }, [selectedProvider]);

  // Sync operations
  const startFullSync = useCallback(async (providerId: string) => {
    setIsSyncing(true);
    setSyncProgress({
      current: 0,
      total: 100,
      status: 'Initializing full sync...',
      errors: [],
      startTime: new Date().toISOString()
    });
    
    try {
      const response = await fetch(`${apiBase}/providers/${providerId}/sync`, {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error('Failed to start sync');
      
      // Start polling for progress
      const pollInterval = setInterval(async () => {
        const progressRes = await fetch(`${apiBase}/providers/${providerId}/sync/progress`);
        if (progressRes.ok) {
          const progress = await progressRes.json();
          setSyncProgress(progress);
          
          if (progress.status === 'completed' || progress.status === 'failed') {
            clearInterval(pollInterval);
            setIsSyncing(false);
            
            if (progress.status === 'completed') {
              setLastSyncResult(progress.result);
              await fetchCourses(providerId);
              await fetchStudents(providerId);
            }
          }
        }
      }, 1000);
      
      // Timeout after 5 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        if (isSyncing) {
          setIsSyncing(false);
        }
      }, 300000);
    } catch (error) {
      setIsSyncing(false);
      throw error;
    }
  }, [fetchCourses, fetchStudents]);

  const cancelSync = useCallback(async () => {
    if (!selectedProvider) return;
    
    await fetch(`${apiBase}/providers/${selectedProvider.id}/sync/cancel`, {
      method: 'POST'
    });
    
    setIsSyncing(false);
    setSyncProgress(null);
  }, [selectedProvider]);

  // Bulk operations
  const bulkSyncCourses = useCallback(async (courseIds: string[]) => {
    if (!selectedProvider) return;
    
    const response = await fetch(`${apiBase}/providers/${selectedProvider.id}/courses/bulk-sync`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ courseIds })
    });
    
    if (!response.ok) throw new Error('Failed to bulk sync courses');
  }, [selectedProvider]);

  const bulkImportStudents = useCallback(async (providerId: string, studentIds: string[]): Promise<SyncResult> => {
    const response = await fetch(`${apiBase}/providers/${providerId}/students/bulk-import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ studentIds })
    });
    
    if (!response.ok) throw new Error('Failed to bulk import students');
    
    return response.json();
  }, []);

  const reconcileRosters = useCallback(async (providerId: string): Promise<SyncResult> => {
    const response = await fetch(`${apiBase}/providers/${providerId}/roster/reconcile`, {
      method: 'POST'
    });
    
    if (!response.ok) throw new Error('Failed to reconcile rosters');
    
    return response.json();
  }, []);

  // Utility functions
  const clearError = useCallback(() => {
    setConnectionError(null);
  }, []);

  const resetIntegration = useCallback(() => {
    setSelectedProvider(null);
    setCourses([]);
    setStudents([]);
    setAssignments([]);
    setRosterMappings([]);
    setSyncProgress(null);
    setLastSyncResult(null);
    setConnectionError(null);
  }, []);

  const exportConfiguration = useCallback(async (providerId: string): Promise<string> => {
    const response = await fetch(`${apiBase}/providers/${providerId}/export`);
    if (!response.ok) throw new Error('Failed to export configuration');
    return response.json();
  }, []);

  const importConfiguration = useCallback(async (config: string): Promise<boolean> => {
    const response = await fetch(`${apiBase}/providers/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ config })
    });
    
    if (!response.ok) return false;
    
    await fetchProviders();
    return true;
  }, [fetchProviders]);

  const value = useMemo<LMSIntegrationContextType>(() => ({
    providers,
    selectedProvider,
    fetchProviders,
    selectProvider,
    addProvider,
    updateProvider,
    deleteProvider,
    testConnection,
    initiateOAuth,
    handleOAuthCallback,
    getOAuthConfig,
    courses,
    fetchCourses,
    syncCourse,
    linkCourse,
    unlinkCourse,
    students,
    rosterMappings,
    fetchStudents,
    syncRoster,
    updateRosterMapping,
    importStudents,
    assignments,
    fetchAssignments,
    syncAssignmentGrades,
    isSyncing,
    syncProgress,
    lastSyncResult,
    startFullSync,
    cancelSync,
    bulkSyncCourses,
    bulkImportStudents,
    reconcileRosters,
    clearError,
    resetIntegration,
    exportConfiguration,
    importConfiguration
  }), [
    providers,
    selectedProvider,
    fetchProviders,
    selectProvider,
    addProvider,
    updateProvider,
    deleteProvider,
    testConnection,
    initiateOAuth,
    handleOAuthCallback,
    getOAuthConfig,
    courses,
    fetchCourses,
    syncCourse,
    linkCourse,
    unlinkCourse,
    students,
    rosterMappings,
    fetchStudents,
    syncRoster,
    updateRosterMapping,
    importStudents,
    assignments,
    fetchAssignments,
    syncAssignmentGrades,
    isSyncing,
    syncProgress,
    lastSyncResult,
    startFullSync,
    cancelSync,
    bulkSyncCourses,
    bulkImportStudents,
    reconcileRosters,
    clearError,
    resetIntegration,
    exportConfiguration,
    importConfiguration
  ]);

  return (
    <LMSIntegrationContext.Provider value={value}>
      {children}
    </LMSIntegrationContext.Provider>
  );
}

export function useLMSIntegration() {
  const context = useContext(LMSIntegrationContext);
  if (!context) {
    throw new Error('useLMSIntegration must be used within an LMSIntegrationProvider');
  }
  return context;
}
