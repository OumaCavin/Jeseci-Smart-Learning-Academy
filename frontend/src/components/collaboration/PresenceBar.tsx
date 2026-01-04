import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useCollaborationSession, Peer } from '../../hooks/useCollaborationSession';

// Icons
const MoreIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" />
  </svg>
);

const CrownIcon = () => (
  <svg className="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
  </svg>
);

const typingIndicator = (
  <span className="flex space-x-1">
    <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
    <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
    <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
  </span>
);

interface PresenceBarProps {
  roomId: string;
  maxDisplay?: number;
  showNames?: boolean;
  showLabels?: boolean;
  compact?: boolean;
  onParticipantClick?: (peer: Peer) => void;
}

export function PresenceBar({
  roomId,
  maxDisplay = 5,
  showNames = true,
  showLabels = true,
  compact = false,
  onParticipantClick
}: PresenceBarProps) {
  const {
    isConnected,
    peers,
    localPeer,
    connectionQuality,
    joinRoom,
    leaveRoom,
    isUserTyping
  } = useCollaborationSession({ roomId });

  const [showDropdown, setShowDropdown] = useState<string | null>(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Click outside handler
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Get typing users
  const typingUsers = peers.filter(p => p.isTyping);
  const displayedPeers = peers.slice(0, maxDisplay);
  const remainingCount = Math.max(0, peers.length - maxDisplay);

  // Connection quality indicator
  const getConnectionIndicator = () => {
    const colors = {
      excellent: 'bg-green-500',
      good: 'bg-green-400',
      poor: 'bg-yellow-500',
      disconnected: 'bg-red-500'
    };
    
    return (
      <div className="flex items-center gap-1.5">
        <div className={`w-2 h-2 rounded-full ${colors[connectionQuality]} ${connectionQuality === 'poor' ? 'animate-pulse' : ''}`} />
        {showLabels && (
          <span className="text-xs text-gray-500 capitalize">{connectionQuality}</span>
        )}
      </div>
    );
  };

  return (
    <div className="flex items-center gap-3">
      {/* Connection status */}
      {getConnectionIndicator()}

      {/* Local user */}
      {localPeer && (
        <div className="flex items-center gap-2">
          <div className="relative">
            <div 
              className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium"
              style={{ backgroundColor: localPeer.color }}
            >
              {localPeer.name.charAt(0).toUpperCase()}
            </div>
            <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 border-2 border-white dark:border-gray-800 rounded-full" />
          </div>
          {!compact && showNames && (
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {localPeer.name} (You)
            </span>
          )}
        </div>
      )}

      {/* Remote peers */}
      <div className="flex items-center -space-x-2">
        {displayedPeers.map((peer) => (
          <div
            key={peer.userId}
            ref={dropdownRef}
            className="relative"
          >
            <button
              onClick={() => onParticipantClick?.(peer)}
              onMouseEnter={() => setShowDropdown(peer.userId)}
              onMouseLeave={() => setShowDropdown(null)}
              className="relative group"
            >
              <div 
                className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium 
                         border-2 border-white dark:border-gray-800 transition-transform hover:scale-110 hover:z-10"
                style={{ backgroundColor: peer.color }}
              >
                {peer.avatar ? (
                  <img src={peer.avatar} alt={peer.name} className="w-full h-full rounded-full object-cover" />
                ) : (
                  peer.name.charAt(0).toUpperCase()
                )}
              </div>
              
              {/* Online indicator */}
              <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 border-2 border-white dark:border-gray-800 rounded-full" />
              
              {/* Typing indicator */}
              {peer.isTyping && (
                <div className="absolute -top-2 left-1/2 -translate-x-1/2 bg-gray-800 dark:bg-gray-600 rounded px-1">
                  {typingIndicator}
                </div>
              )}

              {/* Cursor position badge (if available) */}
              {peer.cursor && !peer.isTyping && (
                <div className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full border-2 border-white dark:border-gray-800"
                     style={{ backgroundColor: peer.color }} />
              )}

              {/* Tooltip */}
              {showDropdown === peer.userId && (
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 
                              bg-gray-900 dark:bg-gray-700 text-white text-xs rounded shadow-lg 
                              whitespace-nowrap z-50">
                  <div className="flex items-center gap-1">
                    <CrownIcon />
                    <span className="font-medium">{peer.name}</span>
                  </div>
                  {peer.cursor && (
                    <div className="text-gray-400 mt-0.5">
                      Line {peer.cursor.lineNumber}, Col {peer.cursor.column}
                    </div>
                  )}
                </div>
              )}
            </button>
          </div>
        ))}

        {/* Remaining count badge */}
        {remainingCount > 0 && (
          <div 
            className="relative"
            onMouseEnter={() => setDropdownOpen(true)}
            onMouseLeave={() => setDropdownOpen(false)}
          >
            <button className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center 
                             justify-center text-gray-600 dark:text-gray-300 text-xs font-medium
                             border-2 border-white dark:border-gray-800 hover:bg-gray-300 
                             dark:hover:bg-gray-600 transition-colors"
            >
              +{remainingCount}
            </button>

            {/* Dropdown with all users */}
            {dropdownOpen && (
              <div className="absolute bottom-full right-0 mb-2 w-48 bg-white dark:bg-gray-800 
                            rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 
                            overflow-hidden z-50">
                <div className="px-3 py-2 border-b border-gray-200 dark:border-gray-700 
                              bg-gray-50 dark:bg-gray-750">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {peers.length} participants
                  </span>
                </div>
                <div className="max-h-48 overflow-y-auto">
                  {peers.slice(maxDisplay).map((peer) => (
                    <button
                      key={peer.userId}
                      onClick={() => onParticipantClick?.(peer)}
                      className="w-full px-3 py-2 flex items-center gap-2 hover:bg-gray-50 
                               dark:hover:bg-gray-700 transition-colors"
                    >
                      <div 
                        className="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs"
                        style={{ backgroundColor: peer.color }}
                      >
                        {peer.name.charAt(0).toUpperCase()}
                      </div>
                      <span className="text-sm text-gray-700 dark:text-gray-300 truncate">
                        {peer.name}
                      </span>
                      {peer.isTyping && (
                        <span className="text-xs text-gray-400 ml-auto">typing...</span>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Typing indicator text */}
      {typingUsers.length > 0 && !compact && (
        <div className="text-xs text-gray-500">
          {typingUsers.length === 1 
            ? `${typingUsers[0].name} is typing...`
            : `${typingUsers.length} people are typing...`
          }
        </div>
      )}

      {/* Connection actions (for development) */}
      {!isConnected && (
        <button
          onClick={joinRoom}
          className="text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400"
        >
          Connect
        </button>
      )}
    </div>
  );
}

