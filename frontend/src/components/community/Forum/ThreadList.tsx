/**
 * Thread List Component
 * 
 * Displays threads within a forum
 */

import React from 'react';
import { MessageSquare, Eye, Clock, Lock, Pin } from 'lucide-react';
import { ForumThread } from '../../services/collaborationService';
import { formatDistanceToNow } from 'date-fns';

interface ThreadListProps {
  threads: ForumThread[];
  loading?: boolean;
  onThreadClick: (threadId: string) => void;
}

const ThreadList: React.FC<ThreadListProps> = ({ threads, loading = false, onThreadClick }) => {
  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="animate-pulse bg-gray-100 rounded-lg p-4">
            <div className="h-5 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  if (threads.length === 0) {
    return (
      <div className="text-center py-12">
        <MessageSquare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Threads Yet</h3>
        <p className="text-gray-500">Be the first to start a discussion!</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {threads.map((thread) => (
        <div
          key={thread.thread_id}
          onClick={() => onThreadClick(thread.thread_id)}
          className={`flex items-center justify-between p-4 rounded-lg border transition-all cursor-pointer ${
            thread.is_pinned
              ? 'bg-blue-50 border-blue-200 hover:bg-blue-100'
              : 'bg-white border-gray-200 hover:bg-gray-50'
          }`}
        >
          <div className="flex items-start space-x-4 flex-1 min-w-0">
            {/* Status Icons */}
            <div className="flex flex-col items-center space-y-1 pt-1">
              {thread.is_pinned && (
                <Pin className="w-4 h-4 text-blue-600" />
              )}
              {thread.is_locked && (
                <Lock className="w-4 h-4 text-gray-400" />
              )}
            </div>

            {/* Thread Info */}
            <div className="flex-1 min-w-0">
              <h4 className={`font-medium truncate ${
                thread.is_pinned ? 'text-blue-900' : 'text-gray-900'
              }`}>
                {thread.title}
              </h4>
              
              <div className="flex items-center space-x-3 mt-1 text-xs text-gray-500">
                <span>
                  by <span className="font-medium">{thread.author.username}</span>
                </span>
                
                {thread.created_at && (
                  <span className="flex items-center space-x-1">
                    <Clock className="w-3 h-3" />
                    <span>{formatDistanceToNow(new Date(thread.created_at), { addSuffix: true })}</span>
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="flex items-center space-x-4 text-sm text-gray-500 ml-4">
            <span className="flex items-center space-x-1">
              <MessageSquare className="w-4 h-4" />
              <span>{thread.reply_count}</span>
            </span>
            <span className="flex items-center space-x-1">
              <Eye className="w-4 h-4" />
              <span>{thread.view_count}</span>
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ThreadList;
