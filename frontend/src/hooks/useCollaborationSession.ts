import { useCallback, useRef, useState, useEffect } from 'react';
import { useCollaboration, Peer, ChatMessage, CodeOperation, CursorPosition, SelectionRange } from '../contexts/CollaborationContext';

// Throttle function for cursor updates
function throttle<T extends (...args: unknown[]) => unknown>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle = false;
  
  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
}

interface UseCollaborationSessionOptions {
  roomId: string;
  fileId: string;
  onPeerJoin?: (peer: Peer) => void;
  onPeerLeave?: (userId: string) => void;
  onOperation?: (operation: CodeOperation) => void;
  onChatMessage?: (message: ChatMessage) => void;
  autoConnect?: boolean;
}

interface UseCollaborationSessionReturn {
  // Connection state
  isConnected: boolean;
  isConnecting: boolean;
  connectionQuality: 'excellent' | 'good' | 'poor' | 'disconnected';
  
  // Participants
  peers: Peer[];
  localPeer: Peer | null;
  
  // Document state
  documentVersion: number;
  syncStatus: 'synced' | 'syncing' | 'conflict' | 'offline';
  
  // Chat
  chatMessages: ChatMessage[];
  unreadCount: number;
  
  // Actions
  joinRoom: () => Promise<void>;
  leaveRoom: () => Promise<void>;
  sendOperation: (operation: Omit<CodeOperation, 'id' | 'userId' | 'timestamp'>) => void;
  updateCursor: (position: CursorPosition) => void;
  updateSelection: (selection: SelectionRange | null) => void;
  sendMessage: (content: string, type?: ChatMessage['type'], codeLanguage?: string) => void;
  clearUnread: () => void;
  
  // Utility
  getPeerById: (userId: string) => Peer | undefined;
  isUserTyping: (userId: string) => boolean;
  getActivePeers: () => Peer[];
}

export function useCollaborationSession(options: UseCollaborationSessionOptions): UseCollaborationSessionReturn {
  const {
    roomId,
    fileId,
    onPeerJoin,
    onPeerLeave,
    onOperation,
    onChatMessage,
    autoConnect = true
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionQuality, setConnectionQuality] = useState<'excellent' | 'good' | 'poor' | 'disconnected'>('disconnected');
  const [peers, setPeers] = useState<Peer[]>([]);
  const [documentVersion, setDocumentVersion] = useState(0);
  const [syncStatus, setSyncStatus] = useState<'synced' | 'syncing' | 'conflict' | 'offline'>('offline');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  
  const {
    state,
    createSession,
    joinSession,
    leaveSession,
    sendOperation: wsSendOperation,
    updateCursor: wsUpdateCursor,
    updateSelection: wsUpdateSelection,
    sendMessage: wsSendMessage,
    clearUnread: wsClearUnread,
    getPeerById: ctxGetPeerById
  } = useCollaboration();

  const localPeerRef = useRef<Peer | null>(null);

  // Create or join session
  const joinRoom = useCallback(async () => {
    setIsConnecting(true);
    
    try {
      // Try to join existing session first
      try {
        await joinSession(roomId);
      } catch {
        // Create new session if doesn't exist
        const session = await createSession(`Collaboration Session`, fileId);
        if (session.id !== roomId) {
          // If we created a new session, update roomId
          roomId = session.id;
        }
      }
      
      setIsConnected(true);
      setSyncStatus('synced');
      setConnectionQuality('excellent');
    } catch (error) {
      console.error('Failed to join room:', error);
      setSyncStatus('offline');
      setConnectionQuality('disconnected');
    } finally {
      setIsConnecting(false);
    }
  }, [roomId, fileId, createSession, joinSession]);

  // Leave room
  const leaveRoom = useCallback(async () => {
    await leaveSession();
    setIsConnected(false);
    setSyncStatus('offline');
    setPeers([]);
    setChatMessages([]);
    setUnreadCount(0);
  }, [leaveSession]);

  // Send operation with throttling
  const sendOperation = useCallback(throttle((operation: Omit<CodeOperation, 'id' | 'userId' | 'timestamp'>) => {
    if (!isConnected) return;
    wsSendOperation(operation);
  }, 50) as (operation: Omit<CodeOperation, 'id' | 'userId' | 'timestamp'>) => void, [isConnected, wsSendOperation]);

  // Send cursor update with throttling
  const updateCursor = useCallback(throttle((position: CursorPosition) => {
    if (!isConnected) return;
    wsUpdateCursor(position);
  }, 50) as (position: CursorPosition) => void, [isConnected, wsUpdateCursor]);

  // Send selection update with throttling
  const updateSelection = useCallback(throttle((selection: SelectionRange | null) => {
    if (!isConnected) return;
    wsUpdateSelection(selection);
  }, 100) as (selection: SelectionRange | null) => void, [isConnected, wsUpdateSelection]);

  // Send chat message
  const sendMessage = useCallback((content: string, type?: ChatMessage['type'], codeLanguage?: string) => {
    if (!isConnected) return;
    wsSendMessage(content, type, codeLanguage);
  }, [isConnected, wsSendMessage]);

  // Clear unread count
  const clearUnread = useCallback(() => {
    wsClearUnread();
    setUnreadCount(0);
  }, [wsClearUnread]);

  // Check if user is typing
  const isUserTyping = useCallback((userId: string): boolean => {
    return peers.some(p => p.userId === userId && p.isTyping);
  }, [peers]);

  // Get active peers (active in last 30 seconds)
  const getActivePeers = useCallback((): Peer[] => {
    const thirtySecondsAgo = new Date(Date.now() - 30000);
    return peers.filter(p => new Date(p.lastActive) > thirtySecondsAgo);
  }, [peers]);

  // Sync with context state
  useEffect(() => {
    setPeers(state.state.peers);
    setDocumentVersion(state.state.documentVersion);
    setSyncStatus(state.state.syncStatus);
    setChatMessages(state.state.chatMessages);
    setUnreadCount(state.state.unreadCount);
    setConnectionQuality(state.state.connectionQuality);
    setIsConnected(state.state.isConnected);
    setIsConnecting(state.state.isConnecting);
    
    localPeerRef.current = {
      userId: state.state.localUserId,
      name: state.state.localUserName,
      color: '#3B82F6',
      cursor: null,
      selection: null,
      isTyping: false,
      lastActive: new Date().toISOString()
    };
  }, [state.state]);

  // Auto-connect
  useEffect(() => {
    if (autoConnect && roomId) {
      joinRoom();
    }
    
    return () => {
      if (autoConnect) {
        leaveRoom();
      }
    };
  }, [autoConnect, roomId, joinRoom, leaveRoom]);

  // Callback effects
  useEffect(() => {
    const newPeer = peers.find(p => !state.state.peers.find(sp => sp.userId === p.userId));
    if (newPeer && onPeerJoin) {
      onPeerJoin(newPeer);
    }
  }, [peers, onPeerJoin]);

  useEffect(() => {
    const leftPeer = state.state.peers.find(p => !peers.find(sp => sp.userId === p.userId));
    if (leftPeer && onPeerLeave) {
      onPeerLeave(leftPeer.userId);
    }
  }, [state.state.peers, peers, onPeerLeave]);

  return {
    isConnected,
    isConnecting,
    connectionQuality,
    peers,
    localPeer: localPeerRef.current,
    documentVersion,
    syncStatus,
    chatMessages,
    unreadCount,
    joinRoom,
    leaveRoom,
    sendOperation,
    updateCursor,
    updateSelection,
    sendMessage,
    clearUnread,
    getPeerById: ctxGetPeerById,
    isUserTyping,
    getActivePeers
  };
}

import { useCallback, useRef, useState, useEffect } from 'react';
