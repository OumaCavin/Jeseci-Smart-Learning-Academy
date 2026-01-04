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

// Phase 3 Contexts
export { AIProvider, useAI } from './AIContext';
export type {
  AIAnalysisResult,
  AICodeSnippet,
  AIConversation,
  AIMessage,
  AITokenUsage,
  AIFeatureConfig,
  AIContextType
} from './AIContext';

export { CurriculumProvider, useCurriculum } from './CurriculumContext';
export type {
  Resource,
  CourseModule,
  Course,
  LearningPath,
  CurriculumState,
  CurriculumContextType
} from './CurriculumContext';

export { AssessmentProvider, useAssessment } from './AssessmentContext';
export type {
  Question,
  Assessment,
  AssessmentSession,
  QuestionBankFilter,
  AssessmentContextType
} from './AssessmentContext';

export { AdminProvider, useAdmin } from './AdminContext';
export type {
  SystemUser,
  AuditLogEntry,
  SystemMetrics,
  SystemHealth,
  UserFilter,
  AuditLogFilter,
  BulkUserAction,
  AdminContextType
} from './AdminContext';

export { NotificationProvider, useNotifications } from './NotificationContext';
export type {
  Notification,
  ToastNotification,
  ChatMessage as NotificationChatMessage,
  Conversation,
  NotificationPreferences,
  NotificationContextType
} from './NotificationContext';

// Phase 4 Contexts
export { AIProvider as AILearningProvider, useAI as useAILearning } from './AILearningContext';
export type {
  SkillNode,
  LearningRecommendation,
  LearningPath,
  UserLearningProfile,
  AIRecommendationConfig,
  AIContextType as AILearningContextType
} from './AILearningContext';

export { VideoRoomProvider, useVideoRoom } from './VideoRoomContext';
export type {
  Peer,
  RoomConfig,
  MediaDevice,
  VideoRoomState,
  VideoRoomContextType
} from './VideoRoomContext';

export { ReportBuilderProvider, useReportBuilder } from './ReportBuilderContext';
export type {
  ReportMetric,
  ReportDimension,
  ReportFilter,
  ReportTimeRange,
  ReportVisualization,
  ReportColumn,
  SavedReport,
  ReportSchedule,
  ReportQuery,
  ReportData,
  ExportJob,
  ReportBuilderContextType
} from './ReportBuilderContext';

export { SchedulerProvider, useScheduler } from './SchedulerContext';
export type {
  ScheduledTask,
  TaskExecutionLog,
  CronSchedule,
  TaskTemplate,
  SchedulerContextType
} from './SchedulerContext';
