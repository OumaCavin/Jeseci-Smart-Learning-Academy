/**
 * Forum List Component
 * 
 * Displays all available discussion forums
 */

import React from 'react';
import { MessageCircle, Plus, Eye, MessageSquare } from 'lucide-react';
import { Forum } from '../../../services/collaborationService';

interface ForumListProps {
  forums: Forum[];
  onThreadClick: (threadId: string) => void;
  onCreateThread: () => void;
}

const ForumList: React.FC<ForumListProps> = ({ forums, onThreadClick, onCreateThread }) => {
  if (forums.length === 0) {
    return (
      <div className="text-center py-12">
        <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Forums Available</h3>
        <p className="text-gray-500">Discussion forums will appear here soon.</p>
      </div>
    );
  }

  const formatLastActivity = (dateString?: string) => {
    if (!dateString) return 'No activity';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
      const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
      return `${diffInMinutes} min ago`;
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)} hours ago`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `${diffInDays} days ago`;
    }
  };

  return (
    <div>
      {/* Actions */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Discussion Forums</h2>
          <p className="text-sm text-gray-500">Join conversations with the community</p>
        </div>
        <button
          onClick={onCreateThread}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>New Thread</span>
        </button>
      </div>

      {/* Forum Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {forums.map((forum) => (
          <div
            key={forum.forum_id}
            className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md hover:border-blue-300 transition-all cursor-pointer group"
            onClick={() => {
              // Navigate to forum threads - would typically use React Router
              console.log('Navigate to forum:', forum.forum_id);
            }}
          >
            <div className="flex items-start space-x-4">
              {/* Forum Icon */}
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-2xl flex-shrink-0">
                {forum.icon || '💬'}
              </div>

              {/* Forum Info */}
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                  {forum.name}
                </h3>
                <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                  {forum.description}
                </p>

                {/* Stats */}
                <div className="flex items-center space-x-4 mt-3 text-xs text-gray-500">
                  <span className="flex items-center space-x-1">
                    <MessageSquare className="w-3.5 h-3.5" />
                    <span>{forum.thread_count} threads</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <Eye className="w-3.5 h-3.5" />
                    <span>{forum.post_count} posts</span>
                  </span>
                </div>

                {/* Last Activity */}
                {forum.last_activity && (
                  <p className="text-xs text-gray-400 mt-2">
                    Last activity: {formatLastActivity(forum.last_activity)}
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Forum Categories Legend */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Forum Categories</h3>
        <div className="flex flex-wrap gap-2">
          {forums.map((forum) => (
            <span
              key={forum.forum_id}
              className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700"
            >
              <span className="mr-1.5">{forum.icon}</span>
              {forum.name}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ForumList;
