import { useCallback, useRef, useState } from 'react';
import { ExecutionRequest, ExecutionResponse, TestResult, ExecutionSession } from '../contexts/CodeExecutionContext';

// Debounce helper
function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;
  
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };
    
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);
  };
}

interface UseCodeExecutionOptions {
  autoCancel?: boolean;
  maxHistorySize?: number;
  saveToHistory?: boolean;
  onSuccess?: (result: ExecutionResponse) => void;
  onError?: (error: Error) => void;
  onStream?: (chunk: string) => void;
}

interface UseCodeExecutionReturn {
  // State
  isExecuting: boolean;
  currentSession: ExecutionSession | null;
  executionHistory: ExecutionSession[];
  currentResult: ExecutionResponse | null;
  resultStream: string[];
  
  // Actions
  execute: (request: ExecutionRequest) => Promise<ExecutionResponse>;
  executeStream: (request: ExecutionRequest) => void;
  cancelExecution: () => void;
  clearHistory: () => void;
  clearCurrentResult: () => void;
  getHistory: () => ExecutionSession[];
  replayExecution: (sessionId: string) => Promise<ExecutionResponse>;
  exportHistory: () => string;
  importHistory: (data: string) => boolean;
}

export function useCodeExecution(options: UseCodeExecutionOptions = {}): UseCodeExecutionReturn {
  const {
    autoCancel = true,
    maxHistorySize = 50,
    saveToHistory = true,
    onSuccess,
    onError,
    onStream
  } = options;

  const [isExecuting, setIsExecuting] = useState(false);
  const [currentSession, setCurrentSession] = useState<ExecutionSession | null>(null);
  const [executionHistory, setExecutionHistory] = useState<ExecutionSession[]>([]);
  const [currentResult, setCurrentResult] = useState<ExecutionResponse | null>(null);
  const [resultStream, setResultStream] = useState<string[]>([]);

  const abortControllerRef = useRef<AbortController | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Generate unique session ID
  const generateSessionId = useCallback(() => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }, []);

  // Execute code via REST API
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
    
    if (saveToHistory) {
      setExecutionHistory(prev => [...prev.slice(-maxHistorySize + 1), session]);
    }

    // Create abort controller for cancellation
    abortControllerRef.current = new AbortController();

    try {
      const controller = abortControllerRef.current;
      const response = await fetch('/api/code-execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...request,
          sessionId,
          timeout: request.timeout || 30000 // Default 30s timeout
        }),
        signal: controller.signal
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP ${response.status}: Execution failed`);
      }

      const result = await response.json();
      
      setCurrentResult(result);
      setCurrentSession(prev => prev ? { ...prev, status: result.success ? 'completed' : 'error' } : null);
      setIsExecuting(false);

      if (saveToHistory) {
        setExecutionHistory(prev =>
          prev.map(s => s.id === sessionId ? { ...s, status: result.success ? 'completed' : 'error' } : s)
        );
      }

      if (result.success) {
        onSuccess?.(result);
      } else {
        onError?.(new Error(result.error || 'Execution failed'));
      }

      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      const errorResult: ExecutionResponse = {
        success: false,
        output: '',
        error: errorMessage
      };

      setCurrentResult(errorResult);
      setCurrentSession(prev => prev ? { ...prev, status: 'error' } : null);
      setIsExecuting(false);

      onError?.(error instanceof Error ? error : new Error(errorMessage));
      return errorResult;
    }
  }, [generateSessionId, saveToHistory, maxHistorySize, onSuccess, onError]);

  // Execute with streaming output
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

    if (saveToHistory) {
      setExecutionHistory(prev => [...prev.slice(-maxHistorySize + 1), session]);
    }

    // Use Server-Sent Events for streaming
    const eventSource = new EventSource(
      `/api/code-execute/stream?sessionId=${encodeURIComponent(sessionId)}&code=${encodeURIComponent(request.code)}&language=${encodeURIComponent(request.language)}`
    );

    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      // Connection opened
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'stream') {
          setResultStream(prev => [...prev, data.chunk]);
          onStream?.(data.chunk);
        } else if (data.type === 'result') {
          const result: ExecutionResponse = data.result;
          setCurrentResult(result);
          setCurrentSession(prev => prev ? { ...prev, status: result.success ? 'completed' : 'error' } : null);
          setIsExecuting(false);
          eventSource.close();
          
          if (saveToHistory) {
            setExecutionHistory(prev =>
              prev.map(s => s.id === sessionId ? { ...s, status: result.success ? 'completed' : 'error' } : s)
            );
          }
          
          if (result.success) {
            onSuccess?.(result);
          } else {
            onError?.(new Error(result.error || 'Execution failed'));
          }
        }
      } catch (parseError) {
        // Handle non-JSON messages (raw output)
        setResultStream(prev => [...prev, event.data]);
        onStream?.(event.data);
      }
    };

    eventSource.onerror = (error) => {
      const errorResult: ExecutionResponse = {
        success: false,
        output: resultStream.join(''),
        error: 'Connection lost during execution'
      };
      
      setCurrentResult(errorResult);
      setCurrentSession(prev => prev ? { ...prev, status: 'error' } : null);
      setIsExecuting(false);
      eventSource.close();
      
      onError?.(new Error('Connection lost during execution'));
    };
  }, [generateSessionId, saveToHistory, maxHistorySize, resultStream, onStream, onSuccess, onError]);

  // Cancel ongoing execution
  const cancelExecution = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    // Cancel via API
    if (currentSession) {
      fetch(`/api/code-execute/${currentSession.id}/cancel`, {
        method: 'POST'
      }).catch(console.error);
    }

    setIsExecuting(false);
    setCurrentSession(prev => prev ? { ...prev, status: 'idle' } : null);
  }, [currentSession]);

  // Clear execution history
  const clearHistory = useCallback(() => {
    setExecutionHistory([]);
  }, []);

  // Clear current result
  const clearCurrentResult = useCallback(() => {
    setCurrentResult(null);
    setResultStream([]);
    setCurrentSession(null);
  }, []);

  // Get full execution history
  const getHistory = useCallback(() => {
    return executionHistory;
  }, [executionHistory]);

  // Replay a previous execution
  const replayExecution = useCallback(async (sessionId: string): Promise<ExecutionResponse> => {
    const session = executionHistory.find(s => s.id === sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }

    return execute({
      code: session.code,
      language: session.language
    });
  }, [executionHistory, execute]);

  // Export history as JSON
  const exportHistory = useCallback(() => {
    return JSON.stringify({
      version: '1.0',
      exportedAt: new Date().toISOString(),
      executions: executionHistory
    }, null, 2);
  }, [executionHistory]);

  // Import history from JSON
  const importHistory = useCallback((data: string): boolean => {
    try {
      const parsed = JSON.parse(data);
      if (Array.isArray(parsed.executions)) {
        setExecutionHistory(parsed.executions.slice(-maxHistorySize));
        return true;
      }
      return false;
    } catch {
      return false;
    }
  }, [maxHistorySize]);

  return {
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
    getHistory,
    replayExecution,
    exportHistory,
    importHistory
  };
}

import { useCallback, useState, useRef } from 'react';
