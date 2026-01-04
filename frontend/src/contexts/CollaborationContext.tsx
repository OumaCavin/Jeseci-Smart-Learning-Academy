import { createContext, useContext, useCallback, useState, useEffect, useRef, useMemo } from 'react';
import { useWebSocket, WebSocketMessage } from '../hooks/useWebSocket';

// Types for collaboration
export interface Peer {
  userId: string;
  name: string;
  email?: string;
  avatar?: string;
  color: string;
  cursor: CursorPosition | null;
  selection: SelectionRange | null;
  isTyping: boolean;
  lastActive: string;
}

export interface CollaboratorPresence {
  userId: string;
  name: string;
  avatar?: string;
  color: string;
  status: 'online' | 'away' | 'busy' | 'offline';
  lastSeen: string;
}

export interface CollaboratorState {
  isConnected: boolean;
  peers: Peer[];
  localUserId: string;
  localUserName: string;
  documentVersion: number;
  syncStatus: 'synced' | 'syncing' | 'conflict' | 'offline';
  connectionQuality: 'excellent' | 'good' | 'poor' | 'disconnected';
}

export interface CursorPosition {
  lineNumber: number;
  column: number;
}

export interface SelectionRange {
  startLineNumber: number;
  startColumn: number;
  endLineNumber: number;
  endColumn: number;
}

export interface ChatMessage {
  id: string;
  userId: string;
  userName: string;
  userAvatar?: string;
  content: string;
  timestamp: string;
  type: 'text' | 'code' | 'system';
  codeLanguage?: string;
}

export interface CodeOperation {
  id: string;
  type: 'insert' | 'delete' | 'replace';
  position: number;
  text?: string;
  length?: number;
  version: number;
  userId: string;
  timestamp: string;
}

export interface CollaborationSession {
  id: string;
  name: string;
  fileId: string;
  createdBy: string;
  createdAt: string;
  participants: string[];
  isActive: boolean;
  permissions: 'read' | 'write' | 'admin';
}

export interface CollaborationState {
  // Session state
  currentSession: CollaborationSession | null;
  isConnected: boolean;
  isConnecting: boolean;
  
  // Participants
  peers: Peer[];
  localUserId: string;
  localUserName: string;
  
  // Document state
  documentVersion: number;
  pendingOperations: CodeOperation[];
  
  // Communication
  chatMessages: ChatMessage[];
  unreadCount: number;
  
  // Sync status
  syncStatus: 'synced' | 'syncing' | 'conflict' | 'offline';
  connectionQuality: 'excellent' | 'good' | 'poor' | 'disconnected';
}

export interface CollaborationContextType {
  // State
  state: CollaborationState;
  
  // Session management
  createSession: (name: string, fileId: string) => Promise<CollaborationSession>;
  joinSession: (sessionId: string) => Promise<void>;
  leaveSession: () => Promise<void>;
  endSession: () => Promise<void>;
  
  // Participant management
  inviteParticipant: (email: string) => Promise<void>;
  removeParticipant: (userId: string) => Promise<void>;
  updatePermissions: (userId: string, permissions: 'read' | 'write' | 'admin') => Promise<void>;
  
  // Document operations
  sendOperation: (operation: Omit<CodeOperation, 'id' | 'userId' | 'timestamp'>) => void;
  updateCursor: (position: CursorPosition) => void;
  updateSelection: (selection: SelectionRange | null) => void;
  
  // Chat
  sendMessage: (content: string, type?: ChatMessage['type'], codeLanguage?: string) => void;
  clearUnread: () => void;
  
  // Utility
  reconnect: () => void;
  getPeerById: (userId: string) => Peer | undefined;
  getPeerColor: (userId: string) => string;
}

const CollaborationContext = createContext<CollaborationContextType | null>(null);

// Generate consistent color from user ID
function getColorFromUserId(userId: string): string {
  const colors = [
    '#EF4444', '#F97316', '#F59E0B', '#84CC16', '#22C55E',
    '#14B8A6', '#06B6D4', '#3B82F6', '#6366F1', '#8B5CF6',
    '#A855F7', '#D946EF', '#EC4899', '#F43F5E'
  ];
  
  let hash = 0;
  for (let i = 0; i < userId.length; i++) {
    hash = userId.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  return colors[Math.abs(hash) % colors.length];
}

export function CollaborationProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<CollaborationState>({
    currentSession: null,
    isConnected: false,
    isConnecting: false,
    peers: [],
    localUserId: '',
    localUserName: '',
    documentVersion: 0,
    pendingOperations: [],
    chatMessages: [],
    unreadCount: 0,
    syncStatus: 'offline',
    connectionQuality: 'disconnected'
  });

  const localUserId = useRef<string>('');
  const localUserName = useRef<string>('');
  const operationQueue = useRef<CodeOperation[]>([]);
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  // WebSocket connection
  const {
    sendMessage: wsSendMessage,
    isConnected: wsConnected,
    connectionState: wsState,
    reconnect: wsReconnect,
    lastMessage
  } = useWebSocket({
    url: '/ws/collab',
    autoConnect: false,
    reconnectInterval: 3000,
    maxReconnectAttempts: 10,
    onMessage: useCallback((message: WebSocketMessage) => {
      handleIncomingMessage(message);
    }, [])
  });

  // Handle incoming WebSocket messages
  const handleIncomingMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'collab.session.joined':
        handleSessionJoined(message.payload);
        break;
      case 'collab.peer.joined':
        handlePeerJoined(message.payload);
        break;
      case 'collab.peer.left':
        handlePeerLeft(message.payload);
        break;
      case 'collab.cursor.update':
        handleCursorUpdate(message.payload);
        break;
      case 'collab.selection.update':
        handleSelectionUpdate(message.payload);
        break;
      case 'collab.operation':
        handleOperation(message.payload);
        break;
      case 'collab.chat.message':
        handleChatMessage(message.payload);
        break;
      case 'collab.sync.progress':
        setState(prev => ({ ...prev, syncStatus: 'syncing' }));
        break;
      case 'collab.sync.completed':
        setState(prev => ({ ...prev, syncStatus: 'synced', documentVersion: message.payload.version }));
        break;
      case 'collab.connection.quality':
        setState(prev => ({ ...prev, connectionQuality: message.payload }));
        break;
    }
  }, []);

  // Session handlers
  const handleSessionJoined = useCallback((payload: { session: CollaborationSession; peers: Peer[] }) => {
    setState(prev => ({
      ...prev,
      currentSession: payload.session,
      peers: payload.peers,
      isConnected: true,
      isConnecting: false,
      syncStatus: 'synced',
      connectionQuality: 'excellent'
    }));
  }, []);

  const handlePeerJoined = useCallback((peer: Peer) => {
    setState(prev => ({
      ...prev,
      peers: [...prev.peers.filter(p => p.userId !== peer.userId), peer]
    }));
  }, []);

  const handlePeerLeft = useCallback((payload: { userId: string }) => {
    setState(prev => ({
      ...prev,
      peers: prev.peers.filter(p => p.userId !== payload.userId)
    }));
  }, []);

  const handleCursorUpdate = useCallback((payload: { userId: string; cursor: CursorPosition }) => {
    setState(prev => ({
      ...prev,
      peers: prev.peers.map(p => 
        p.userId === payload.userId 
          ? { ...p, cursor: payload.cursor, lastActive: new Date().toISOString() }
          : p
      )
    }));
  }, []);

  const handleSelectionUpdate = useCallback((payload: { userId: string; selection: SelectionRange | null }) => {
    setState(prev => ({
      ...prev,
      peers: prev.peers.map(p => 
        p.userId === payload.userId 
          ? { ...p, selection: payload.selection, lastActive: new Date().toISOString() }
          : p
      )
    }));
  }, []);

  const handleOperation = useCallback((operation: CodeOperation) => {
    setState(prev => ({
      ...prev,
      documentVersion: operation.version,
      peers: prev.peers.map(p =>
        p.userId === operation.userId
          ? { ...p, isTyping: false, lastActive: new Date().toISOString() }
          : p
      )
    }));
  }, []);

  const handleChatMessage = useCallback((message: ChatMessage) => {
    setState(prev => {
      const isOwnMessage = message.userId === localUserId.current;
      return {
        ...prev,
        chatMessages: [...prev.chatMessages, message],
        unreadCount: isOwnMessage ? prev.unreadCount : prev.unreadCount + 1
      };
    });
  }, []);

  // Session management
  const createSession = useCallback(async (name: string, fileId: string): Promise<CollaborationSession> => {
    const response = await fetch('/api/collab/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, fileId })
    });

    if (!response.ok) {
      throw new Error('Failed to create session');
    }

    const session = await response.json();
    await joinSession(session.id);
    return session;
  }, []);

  const joinSession = useCallback(async (sessionId: string) => {
    setState(prev => ({ ...prev, isConnecting: true }));

    // Get user info
    const userResponse = await fetch('/api/users/me');
    if (userResponse.ok) {
      const userData = await userResponse.json();
      localUserId.current = userData.id;
      localUserName.current = userData.name;
      
      setState(prev => ({
        ...prev,
        localUserId: userData.id,
        localUserName: userData.name
      }));
    }

    // Join WebSocket room
    wsSendMessage({
      type: 'collab.join',
      payload: { sessionId },
      timestamp: new Date().toISOString()
    });
  }, [wsSendMessage]);

  const leaveSession = useCallback(async () => {
    if (state.currentSession) {
      wsSendMessage({
        type: 'collab.leave',
        payload: { sessionId: state.currentSession.id },
        timestamp: new Date().toISOString()
      });

      await fetch(`/api/collab/sessions/${state.currentSession.id}/leave`, {
        method: 'POST'
      });

      setState(prev => ({
        ...prev,
        currentSession: null,
        peers: [],
        isConnected: false,
        chatMessages: [],
        unreadCount: 0,
        syncStatus: 'offline'
      }));
    }
  }, [state.currentSession, wsSendMessage]);

  const endSession = useCallback(async () => {
    if (state.currentSession) {
      await fetch(`/api/collab/sessions/${state.currentSession.id}`, {
        method: 'DELETE'
      });

      setState(prev => ({
        ...prev,
        currentSession: null,
        peers: [],
        isConnected: false,
        chatMessages: [],
        unreadCount: 0,
        syncStatus: 'offline'
      }));
    }
  }, [state.currentSession]);

  // Participant management
  const inviteParticipant = useCallback(async (email: string) => {
    if (!state.currentSession) return;

    const response = await fetch(`/api/collab/sessions/${state.currentSession.id}/invite`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });

    if (!response.ok) {
      throw new Error('Failed to invite participant');
    }
  }, [state.currentSession]);

  const removeParticipant = useCallback(async (userId: string) => {
    if (!state.currentSession) return;

    await fetch(`/api/collab/sessions/${state.currentSession.id}/participants/${userId}`, {
      method: 'DELETE'
    });

    setState(prev => ({
      ...prev,
      peers: prev.peers.filter(p => p.userId !== userId)
    }));
  }, [state.currentSession]);

  const updatePermissions = useCallback(async (userId: string, permissions: 'read' | 'write' | 'admin') => {
    if (!state.currentSession) return;

    await fetch(`/api/collab/sessions/${state.currentSession.id}/participants/${userId}/permissions`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ permissions })
    });
  }, [state.currentSession]);

  // Document operations
  const sendOperation = useCallback((operation: Omit<CodeOperation, 'id' | 'userId' | 'timestamp'>) => {
    if (!state.isConnected) return;

    const fullOperation: CodeOperation = {
      ...operation,
      id: `op_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      userId: localUserId.current,
      timestamp: new Date().toISOString()
    };

    // Queue operation for reliability
    operationQueue.current.push(fullOperation);

    wsSendMessage({
      type: 'collab.operation',
      payload: fullOperation,
      timestamp: new Date().toISOString()
    });

    // Mark self as typing
    setState(prev => ({
      ...prev,
      peers: prev.peers.map(p =>
        p.userId === localUserId.current
          ? { ...p, isTyping: true, lastActive: new Date().toISOString() }
          : p
      )
    }));

    // Clear typing indicator after delay
    setTimeout(() => {
      setState(prev => ({
        ...prev,
        peers: prev.peers.map(p =>
          p.userId === localUserId.current
            ? { ...p, isTyping: false }
            : p
        )
      }));
    }, 2000);
  }, [state.isConnected, wsSendMessage]);

  const updateCursor = useCallback((position: CursorPosition) => {
    if (!state.isConnected) return;

    wsSendMessage({
      type: 'collab.cursor.update',
      payload: { userId: localUserId.current, cursor: position },
      timestamp: new Date().toISOString()
    });
  }, [state.isConnected, wsSendMessage]);

  const updateSelection = useCallback((selection: SelectionRange | null) => {
    if (!state.isConnected) return;

    wsSendMessage({
      type: 'collab.selection.update',
      payload: { userId: localUserId.current, selection },
      timestamp: new Date().toISOString()
    });
  }, [state.isConnected, wsSendMessage]);

  // Chat
  const sendMessage = useCallback((content: string, type: ChatMessage['type'] = 'text', codeLanguage?: string) => {
    if (!state.isConnected || !localUserId.current) return;

    const message: ChatMessage = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      userId: localUserId.current,
      userName: localUserName.current,
      content,
      timestamp: new Date().toISOString(),
      type,
      codeLanguage
    };

    wsSendMessage({
      type: 'collab.chat.message',
      payload: message,
      timestamp: new Date().toISOString()
    });

    // Optimistic update
    setState(prev => ({
      ...prev,
      chatMessages: [...prev.chatMessages, message]
    }));
  }, [state.isConnected, wsSendMessage]);

  const clearUnread = useCallback(() => {
    setState(prev => ({ ...prev, unreadCount: 0 }));
  }, []);

  // Reconnect
  const reconnect = useCallback(() => {
    if (state.currentSession) {
      wsReconnect();
    }
  }, [state.currentSession, wsReconnect]);

  // Utility functions
  const getPeerById = useCallback((userId: string) => {
    return state.peers.find(p => p.userId === userId);
  }, [state.peers]);

  const getPeerColor = useCallback((userId: string) => {
    if (userId === localUserId.current) {
      return getColorFromUserId(userId);
    }
    const peer = state.peers.find(p => p.userId === userId);
    return peer?.color || getColorFromUserId(userId);
  }, [state.peers]);

  // Update connection state
  useEffect(() => {
    setState(prev => ({
      ...prev,
      isConnected: wsConnected,
      isConnecting: wsState === 'connecting',
      connectionQuality: wsConnected ? 'excellent' : 'disconnected'
    }));
  }, [wsConnected, wsState]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
    };
  }, []);

  const value = useMemo<CollaborationContextType>(() => ({
    state,
    createSession,
    joinSession,
    leaveSession,
    endSession,
    inviteParticipant,
    removeParticipant,
    updatePermissions,
    sendOperation,
    updateCursor,
    updateSelection,
    sendMessage,
    clearUnread,
    reconnect,
    getPeerById,
    getPeerColor
  }), [state, createSession, joinSession, leaveSession, endSession, inviteParticipant, 
      removeParticipant, updatePermissions, sendOperation, updateCursor, updateSelection,
      sendMessage, clearUnread, reconnect, getPeerById, getPeerColor]);

  return (
    <CollaborationContext.Provider value={value}>
      {children}
    </CollaborationContext.Provider>
  );
}

export function useCollaboration() {
  const context = useContext(CollaborationContext);
  if (!context) {
    throw new Error('useCollaboration must be used within a CollaborationProvider');
  }
  return context;
}
