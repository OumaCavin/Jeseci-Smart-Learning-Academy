// Hooks exports
export { useWebSocket } from './useWebSocket';
export type { 
  WebSocketMessage, 
  WebSocketMessageType, 
  WebSocketConnectionState,
  WebSocketConfig,
  UseWebSocketReturn 
} from './useWebSocket';

export { useCodeExecution } from './useCodeExecution';
export type { 
  UseCodeExecutionOptions, 
  UseCodeExecutionReturn 
} from './useCodeExecution';

export { useLMSIntegration } from './useLMSIntegration';
export type { 
  UseLMSIntegrationOptions, 
  UseLMSIntegrationReturn 
} from './useLMSIntegration';

// Phase 2: Collaboration
export { useCollaborationSession } from './useCollaborationSession';
export type { 
  UseCollaborationSessionOptions,
  UseCollaborationSessionReturn 
} from './useCollaborationSession';

// Phase 2: Gamification
export { useGamification } from './useGamification';
export type { 
  UseGamificationOptions,
  UseGamificationReturn 
} from './useGamification';

// Phase 2: Analytics
export { 
  usePerformanceMetrics, 
  useEngagementData, 
  useStudentAnalytics 
} from './useAnalytics';
export type { 
  UsePerformanceMetricsOptions,
  UsePerformanceMetricsReturn,
  UseEngagementDataOptions,
  UseEngagementDataReturn,
  UseStudentAnalyticsOptions,
  UseStudentAnalyticsReturn
} from './useAnalytics';

// Phase 3: AI Features
export { useCodeAnalysis } from './ai/useCodeAnalysis';
export type { 
  AIAnalysisSuggestion,
  CodeAnalysisResult,
  UseCodeAnalysisOptions,
  UseCodeAnalysisReturn 
} from './ai/useCodeAnalysis';

// Phase 3: Content Management
export { useCourseBuilder } from './content/useCourseBuilder';
export type { 
  CourseModuleData,
  ResourceData,
  CourseData,
  UseCourseBuilderOptions,
  UseCourseBuilderReturn 
} from './content/useCourseBuilder';

// Phase 3: Assessment
export { useExamSession } from './assessment/useExamSession';
export type { 
  ExamQuestion,
  ExamSessionData,
  ExamResult,
  UseExamSessionOptions,
  UseExamSessionReturn 
} from './assessment/useExamSession';

// Phase 3: System Administration
export { useSystemHealth } from './admin/useSystemHealth';
export type { 
  SystemMetrics,
  HealthComponent,
  SystemHealth,
  AuditLogEntry,
  AuditLogFilter,
  UseSystemHealthOptions,
  UseSystemHealthReturn 
} from './admin/useSystemHealth';

// Phase 4: AI Learning
export { useSkillGraph } from './ai/useSkillGraph';
export type { 
  UseSkillGraphOptions,
  UseSkillGraphReturn 
} from './ai/useSkillGraph';

// Phase 4: Video Communication
export { useWebRTC } from './communication/useWebRTC';
export type { 
  UseWebRTCOptions,
  UseWebRTCReturn 
} from './communication/useWebRTC';
