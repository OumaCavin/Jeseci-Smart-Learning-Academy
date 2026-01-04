import { useCallback, useEffect, useRef, useState } from 'react';

// WebSocket message types
export type WebSocketMessageType = 
  | 'connection.established'
  | 'connection.error'
  | 'connection.close'
  | 'connection.reconnecting'
  | 'execution.stream'
  | 'execution.completed'
  | 'execution.error'
  | 'execution.started'
  | 'execution.cancelled'
  | 'sync.progress'
  | 'sync.completed'
  | 'sync.error'
  | 'notification'
  | 'chat.message'
  | 'collaboration.presence'
  | 'collaboration.update'
  | 'dashboard.metric'
  | 'lms.sync.progress'
  | 'lms.sync.completed'
  | 'lms.sync.error'
  | 'agent.message'
  | 'agent.status';

export type WebSocketConnectionState = 'connecting' | 'open' | 'closing' | 'closed' | 'error' | 'reconnecting';

export interface WebSocketMessage<T = unknown> {
  type: WebSocketMessageType;
  payload: T;
  timestamp: string;
  messageId?: string;
}

export interface WebSocketConfig {
  url: string;
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
  onMessage?: (message: WebSocketMessage) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  onReconnecting?: (attempt: number) => void;
  onReconnectSuccess?: () => void;
  authToken?: string;
}

interface UseWebSocketReturn {
  sendMessage: (message: WebSocketMessage) => boolean;
  isConnected: boolean;
  connectionState: WebSocketConnectionState;
  lastMessage: WebSocketMessage | null;
  reconnect: () => void;
  disconnect: () => void;
  connectionError: Error | null;
  reconnectAttempts: number;
}

export function useWebSocket(config: WebSocketConfig): UseWebSocketReturn {
  const {
    url,
    autoConnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    heartbeatInterval = 30000,
    onMessage,
    onOpen,
    onClose,
    onError,
    onReconnecting,
    onReconnectSuccess,
    authToken
  } = config;

  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState<WebSocketConnectionState>('closed');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [connectionError, setConnectionError] = useState<Error | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const heartbeatIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const messageQueueRef = useRef<WebSocketMessage[]>([]);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setConnectionState('connecting');
    setConnectionError(null);

    try {
      const wsUrl = authToken ? `${url}?token=${encodeURIComponent(authToken)}` : url;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setConnectionState('open');
        setReconnectAttempts(0);
        reconnectAttemptsRef.current = 0;
        
        // Send queued messages
        while (messageQueueRef.current.length > 0) {
          const queuedMessage = messageQueueRef.current.shift();
          if (queuedMessage) {
            ws.send(JSON.stringify(queuedMessage));
          }
        }
        
        // Start heartbeat
        heartbeatIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping', payload: { timestamp: Date.now() } }));
          }
        }, heartbeatInterval);

        onOpen?.();
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage;
          setLastMessage(message);
          onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        setConnectionState('error');
        setConnectionError(new Error('WebSocket connection error'));
        onError?.(error);
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        setConnectionState('closed');
        clearInterval(heartbeatIntervalRef.current!);
        onClose?.();

        // Auto-reconnect if not intentionally closed
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          setConnectionState('reconnecting');
          reconnectAttemptsRef.current++;
          setReconnectAttempts(reconnectAttemptsRef.current);
          onReconnecting?.(reconnectAttemptsRef.current);

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };
    } catch (error) {
      setConnectionState('error');
      setConnectionError(error instanceof Error ? error : new Error('Failed to create WebSocket connection'));
    }
  }, [url, authToken, heartbeatInterval, maxReconnectAttempts, reconnectInterval, onMessage, onOpen, onClose, onError, onReconnecting]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'Client disconnect');
      wsRef.current = null;
    }
    
    setIsConnected(false);
    setConnectionState('closed');
    setReconnectAttempts(0);
    reconnectAttemptsRef.current = 0;
  }, []);

  // Send message
  const sendMessage = useCallback((message: WebSocketMessage): boolean => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
      return true;
    }
    
    // Queue message for reconnection
    messageQueueRef.current.push(message);
    return false;
  }, []);

  // Manual reconnect
  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttemptsRef.current = 0;
    setReconnectAttempts(0);
    connect();
  }, [disconnect, connect]);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    sendMessage,
    isConnected,
    connectionState,
    lastMessage,
    reconnect,
    disconnect,
    connectionError,
    reconnectAttempts
  };
}

import { useCallback, useEffect, useRef, useState } from 'react';
