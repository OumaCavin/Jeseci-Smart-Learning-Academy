import { useCallback, useEffect, useRef, useState } from 'react';
import { useWebSocket, WebSocketMessage, WebSocketConnectionState } from './useWebSocket';

// Types for code execution
export interface ExecutionRequest {
  code: string;
  language: string;
  timeout?: number;
  stdin?: string;
  sessionId?: string;
}

export interface ExecutionResponse {
  success: boolean;
  output: string;
  error?: string;
  executionTime?: number;
  memoryUsed?: number;
  testResults?: TestResult[];
}

export interface TestResult {
  name: string;
  passed: boolean;
  expected?: string;
  actual?: string;
  message?: string;
}

export interface ExecutionSession {
  id: string;
  status: 'idle' | 'running' | 'completed' | 'error';
  startTime: number;
  code: string;
  language: string;
}

export interface CodeExecutionContextType {
  // Execution state
  isExecuting: boolean;
  currentSession: ExecutionSession | null;
  executionHistory: ExecutionSession[];
  
  // Results
  currentResult: ExecutionResponse | null;
  resultStream: string[];
  
  // Actions
  execute: (request: ExecutionRequest) => Promise<ExecutionResponse>;
  executeStream: (request: ExecutionRequest) => void;
  cancelExecution: () => void;
  clearHistory: () => void;
  clearCurrentResult: () => void;
  
  // WebSocket connection state
  wsConnected: boolean;
  wsState: WebSocketConnectionState;
}

const CodeExecutionContext = createContext<CodeExecutionContextType | null>(null);

export function CodeExecutionProvider({ children }: { children: React.ReactNode }) {
  const [isExecuting, setIsExecuting] = useState(false);
  const [currentSession, setCurrentSession] = useState<ExecutionSession | null>(null);
  const [executionHistory, setExecutionHistory] = useState<ExecutionSession[]>([]);
  const [currentResult, setCurrentResult] = useState<ExecutionResponse | null>(null);
  const [resultStream, setResultStream] = useState<string[]>([]);
  
  const {
    sendMessage,
    isConnected: wsConnected,
    connectionState: wsState,
    lastMessage
  } = useWebSocket({
    url: '/ws/code-execution',
    autoConnect: true,
    reconnectInterval: 3000,
    maxReconnectAttempts: 5,
    onMessage: useCallback((message: WebSocketMessage) => {
      if (message.type === 'execution.stream') {
        setResultStream(prev => [...prev, message.payload]);
      } else if (message.type === 'execution.completed') {
        setCurrentResult(message.payload);
        setIsExecuting(false);
        setCurrentSession(prev => prev ? { ...prev, status: 'completed' } : null);
      } else if (message.type === 'execution.error') {
        setCurrentResult({ ...message.payload, success: false });
        setIsExecuting(false);
        setCurrentSession(prev => prev ? { ...prev, status: 'error' } : null);
      }
    }, [])
  });

  // Generate unique session ID
  const generateSessionId = useCallback(() => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }, []);

  // Execute code (REST API fallback)
  const execute = useCallback(async (request: ExecutionRequest): Promise<ExecutionResponse> => {
    const sessionId = generateSessionId();
    const session: ExecutionSession = {
      id: sessionId,
      status: 'running',
      startTime: Date.now(),
      code: request.code,
      language: request.language
    };

    setIsExecuting(true);
    setCurrentSession(session);
    setCurrentResult(null);
    setResultStream([]);
    
    // Add to history
    setExecutionHistory(prev => [...prev.slice(-49), session]);

    try {
      const response = await fetch('/api/code-execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...request,
          sessionId
        })
      });

      const result = await response.json();
      setCurrentResult(result);
      setCurrentSession(prev => prev ? { ...prev, status: result.success ? 'completed' : 'error' } : null);
      setIsExecuting(false);
      
      // Update history with completed status
      setExecutionHistory(prev => 
        prev.map(s => s.id === sessionId ? { ...s, status: result.success ? 'completed' : 'error' } : s)
      );

      return result;
    } catch (error) {
      const errorResult: ExecutionResponse = {
        success: false,
        output: '',
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
      setCurrentResult(errorResult);
      setCurrentSession(prev => prev ? { ...prev, status: 'error' } : null);
      setIsExecuting(false);
      return errorResult;
    }
  }, [generateSessionId]);

  // Execute with streaming (WebSocket)
  const executeStream = useCallback((request: ExecutionRequest) => {
    const sessionId = generateSessionId();
    const session: ExecutionSession = {
      id: sessionId,
      status: 'running',
      startTime: Date.now(),
      code: request.code,
      language: request.language
    };

    setIsExecuting(true);
    setCurrentSession(session);
    setCurrentResult(null);
    setResultStream([]);
    
    setExecutionHistory(prev => [...prev.slice(-49), session]);

    if (wsConnected && wsState === WebSocketConnectionState.OPEN) {
      sendMessage({
        type: 'execution.start',
        payload: {
          ...request,
          sessionId,
          stream: true
        }
      });
    } else {
      // Fallback to REST if WebSocket not available
      execute(request);
    }
  }, [wsConnected, wsState, sendMessage, execute, generateSessionId]);

  // Cancel ongoing execution
  const cancelExecution = useCallback(() => {
    if (currentSession) {
      sendMessage({
        type: 'execution.cancel',
        payload: { sessionId: currentSession.id }
      });
      setIsExecuting(false);
      setCurrentSession(prev => prev ? { ...prev, status: 'idle' } : null);
    }
  }, [currentSession, sendMessage]);

  // Clear history
  const clearHistory = useCallback(() => {
    setExecutionHistory([]);
  }, []);

  // Clear current result
  const clearCurrentResult = useCallback(() => {
    setCurrentResult(null);
    setResultStream([]);
    setCurrentSession(null);
  }, []);

  // Cleanup old sessions from history
  useEffect(() => {
    const now = Date.now();
    const maxAge = 24 * 60 * 60 * 1000; // 24 hours
    setExecutionHistory(prev => 
      prev.filter(session => now - session.startTime < maxAge)
    );
  }, []);

  const value: CodeExecutionContextType = {
    isExecuting,
    currentSession,
    executionHistory,
    currentResult,
    resultStream,
    execute,
    executeStream,
    cancelExecution,
    clearHistory,
    clearCurrentResult,
    wsConnected,
    wsState
  };

  return (
    <CodeExecutionContext.Provider value={value}>
      {children}
    </CodeExecutionContext.Provider>
  );
}

export function useCodeExecution() {
  const context = useContext(CodeExecutionContext);
  if (!context) {
    throw new Error('useCodeExecution must be used within a CodeExecutionProvider');
  }
  return context;
}
