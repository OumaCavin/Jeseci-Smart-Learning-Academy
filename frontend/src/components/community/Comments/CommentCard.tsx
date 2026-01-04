/**
 * Comment Card Component
 * 
 * Displays a single content comment
 */

import React, { useState } from 'react';
import { Heart, MessageSquare, MoreHorizontal } from 'lucide-react';
import { ContentComment } from '../../../services/collaborationService';
import { formatDistanceToNow } from 'date-fns';

interface CommentCardProps {
  comment: ContentComment;
  onReply?: (commentId: string) => void;
  onLike?: (commentId: string) => void;
  isReply?: boolean;
}

const CommentCard: React.FC<CommentCardProps> = ({
  comment,
  onReply,
  onLike,
  isReply = false
}) => {
  const [liked, setLiked] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const handleLike = () => {
    if (!liked) {
      setLiked(true);
      onLike?.(comment.comment_id);
    }
  };

  const authorInitials = comment.author.first_name
    ? `${comment.author.first_name.charAt(0)}${comment.author.last_name?.charAt(0) || ''}`
    : comment.author.username.charAt(0).toUpperCase();

  return (
    <div className={`flex space-x-3 ${isReply ? 'ml-12' : ''}`}>
      {/* Avatar */}
      <div className="flex-shrink-0">
        {comment.author.avatar_url ? (
          <img
            src={comment.author.avatar_url}
            alt={comment.author.username}
            className={`rounded-full ${isReply ? 'w-8 h-8' : 'w-10 h-10'}`}
          />
        ) : (
          <div className={`bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-medium ${
            isReply ? 'w-8 h-8 text-sm' : 'w-10 h-10'
          }`}>
            {authorInitials}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className={`font-medium text-gray-900 ${isReply ? 'text-sm' : ''}`}>
              {comment.author.first_name && comment.author.last_name
                ? `${comment.author.first_name} ${comment.author.last_name}`
                : comment.author.username}
            </span>
            {!isReply && (
              <span className="text-gray-500 text-sm">@{comment.author.username}</span>
            )}
            <span className="text-xs text-gray-400">
              {formatDistanceToNow(new Date(comment.created_at || new Date()), { addSuffix: true })}
            </span>
          </div>

          {/* Menu */}
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-1 text-gray-400 hover:text-gray-600 rounded"
            >
              <MoreHorizontal className={`w-4 h-4 ${isReply ? 'w-3 h-3' : ''}`} />
            </button>
            {showMenu && (
              <div className="absolute right-0 mt-1 w-28 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-10">
                <button className="w-full px-3 py-1.5 text-left text-xs text-gray-700 hover:bg-gray-50">
                  Copy
                </button>
                <button className="w-full px-3 py-1.5 text-left text-xs text-gray-700 hover:bg-gray-50">
                  Report
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Comment Content */}
        <div className={`mt-1 text-gray-800 ${isReply ? 'text-sm' : ''}`}>
          {comment.content}
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-4 mt-2">
          <button
            onClick={handleLike}
            className={`flex items-center space-x-1 text-xs transition-colors ${
              liked ? 'text-red-500' : 'text-gray-500 hover:text-red-500'
            }`}
          >
            <Heart className={`w-3.5 h-3.5 ${liked ? 'fill-current' : ''}`} />
            <span>{comment.like_count + (liked ? 1 : 0)}</span>
          </button>

          <button
            onClick={() => onReply?.(comment.comment_id)}
            className="flex items-center space-x-1 text-xs text-gray-500 hover:text-blue-600 transition-colors"
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Reply</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default CommentCard;
