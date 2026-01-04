import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useCollaborationSession, ChatMessage } from '../../hooks/useCollaborationSession';

// Icons
const SendIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
  </svg>
);

const CloseIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

const CodeIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
  </svg>
);

const ImageIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
  </svg>
);

const UsersIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
  </svg>
);

interface ChatPanelProps {
  roomId: string;
  isOpen: boolean;
  onClose: () => void;
  maxHeight?: string;
  showHeader?: boolean;
  compact?: boolean;
}

export function ChatPanel({
  roomId,
  isOpen,
  onClose,
  maxHeight = '400px',
  showHeader = true,
  compact = false
}: ChatPanelProps) {
  const {
    chatMessages,
    unreadCount,
    sendMessage,
    clearUnread,
    peers
  } = useCollaborationSession({ roomId, autoConnect: false });

  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<ChatMessage['type']>('text');
  const [isCodeMode, setIsCodeMode] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // Clear unread when opened
  useEffect(() => {
    if (isOpen) {
      clearUnread();
    }
  }, [isOpen, clearUnread]);

  // Handle send
  const handleSend = useCallback(() => {
    if (!message.trim()) return;

    sendMessage(message, messageType);
    setMessage('');
    setMessageType('text');
    setIsCodeMode(false);
  }, [message, messageType, sendMessage]);

  // Handle key press
  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  // Format timestamp
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Get user initials
  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  // Find user color
  const getUserColor = (userId: string) => {
    const peer = peers.find(p => p.userId === userId);
    return peer?.color || '#6B7280';
  };

  if (!isOpen) return null;

  return (
    <div className="flex flex-col bg-white dark:bg-gray-800 rounded-lg shadow-lg border 
                   border-gray-200 dark:border-gray-700 overflow-hidden"
         style={{ maxHeight }}>
      
      {/* Header */}
      {showHeader && (
        <div className="flex items-center justify-between px-4 py-3 border-b 
                      border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-750">
          <div className="flex items-center gap-2">
            <UsersIcon />
            <span className="font-medium text-gray-900 dark:text-gray-100">
              Chat
            </span>
            <span className="text-xs text-gray-500 bg-gray-200 dark:bg-gray-700 px-2 py-0.5 rounded-full">
              {peers.length + 1}
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 
                     rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          >
            <CloseIcon />
          </button>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {chatMessages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <UsersIcon />
            <p className="text-sm mt-2">No messages yet</p>
            <p className="text-xs mt-1">Start the conversation!</p>
          </div>
        ) : (
          chatMessages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-2 ${msg.type === 'system' ? 'justify-center' : ''}`}
            >
              {msg.type === 'system' ? (
                <span className="text-xs text-gray-400 bg-gray-100 dark:bg-gray-700 
                               px-2 py-1 rounded-full">
                  {msg.content}
                </span>
              ) : (
                <>
                  {/* Avatar */}
                  <div 
                    className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center 
                             text-white text-xs font-medium"
                    style={{ backgroundColor: getUserColor(msg.userId) }}
                  >
                    {msg.userAvatar ? (
                      <img src={msg.userAvatar} alt="" className="w-full h-full rounded-full object-cover" />
                    ) : (
                      getInitials(msg.userName)
                    )}
                  </div>

                  {/* Message content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-baseline gap-2">
                      <span className="font-medium text-sm text-gray-900 dark:text-gray-100">
                        {msg.userName}
                      </span>
                      <span className="text-xs text-gray-400">
                        {formatTime(msg.timestamp)}
                      </span>
                    </div>
                    
                    {msg.type === 'code' ? (
                      <div className="mt-1">
                        <div className="bg-gray-900 dark:bg-gray-950 rounded-lg p-3 overflow-x-auto">
                          <pre className="text-xs text-gray-100 font-mono">
                            <code>{msg.content}</code>
                          </pre>
                        </div>
                        {msg.codeLanguage && (
                          <span className="text-xs text-gray-500 mt-1 block">
                            {msg.codeLanguage}
                          </span>
                        )}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-700 dark:text-gray-300 mt-0.5 
                                   whitespace-pre-wrap break-words">
                        {msg.content}
                      </p>
                    )}
                  </div>
                </>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 dark:border-gray-700 p-3">
        {/* Mode toggle */}
        <div className="flex items-center gap-2 mb-2">
          <button
            onClick={() => {
              setIsCodeMode(false);
              setMessageType('text');
            }}
            className={`px-2 py-1 text-xs rounded transition-colors ${
              !isCodeMode 
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' 
                : 'text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            Text
          </button>
          <button
            onClick={() => {
              setIsCodeMode(true);
              setMessageType('code');
            }}
            className={`px-2 py-1 text-xs rounded transition-colors flex items-center gap-1 ${
              isCodeMode 
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' 
                : 'text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <CodeIcon />
            Code
          </button>
        </div>

        {/* Input field */}
        <div className="flex items-end gap-2">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder={isCodeMode ? 'Paste code snippet...' : 'Type a message...'}
            className={`flex-1 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 
                     rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                     placeholder-gray-400 resize-none focus:ring-2 focus:ring-blue-500 
                     focus:border-blue-500 ${isCodeMode ? 'font-mono' : ''}`}
            rows={isCodeMode ? 4 : 2}
            disabled={!isOpen}
          />
          
          <button
            onClick={handleSend}
            disabled={!message.trim()}
            className="p-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg 
                     disabled:opacity-50 disabled:cursor-not-allowed transition-colors
                     flex-shrink-0"
          >
            <SendIcon />
          </button>
        </div>

        {/* Unread indicator */}
        {unreadCount > 0 && (
          <div className="text-xs text-blue-600 dark:text-blue-400 mt-1">
            {unreadCount} new message{unreadCount > 1 ? 's' : ''}
          </div>
        )}
      </div>
    </div>
  );
}

