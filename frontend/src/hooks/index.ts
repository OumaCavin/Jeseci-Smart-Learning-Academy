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
