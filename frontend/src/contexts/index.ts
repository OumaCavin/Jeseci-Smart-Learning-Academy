// Contexts exports
export { CodeExecutionProvider, useCodeExecution } from './CodeExecutionContext';
export type { 
  ExecutionRequest, 
  ExecutionResponse, 
  TestResult, 
  ExecutionSession,
  CodeExecutionContextType 
} from './CodeExecutionContext';

export { LMSIntegrationProvider, useLMSIntegration } from './LMSIntegrationContext';
export type {
  LMSProvider,
  LMSCourse,
  LMSStudent,
  LMSAssignment,
  SyncProgress,
  SyncResult,
  RosterMapping,
  OAuthConfig,
  LMSIntegrationState,
  LMSIntegrationContextType
} from './LMSIntegrationContext';

export { CollaborationProvider, useCollaboration } from './CollaborationContext';
export type {
  CollaboratorPresence,
  ChatMessage,
  CursorPosition,
  CollaborationSession,
  CollaboratorState,
  CollaborationContextType
} from './CollaborationContext';

export { GamificationProvider, useGamification } from './GamificationContext';
export type {
  UserBadge,
  Achievement,
  LeaderboardEntry,
  XPTransaction,
  GamificationState,
  GamificationContextType
} from './GamificationContext';

export { AnalyticsProvider, useAnalytics } from './AnalyticsContext';
export type {
  StudentAnalytics,
  CourseAnalytics,
  SkillMetrics,
  EngagementData,
  PerformanceTrend,
  AnalyticsContextType
} from './AnalyticsContext';
