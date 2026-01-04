/**
 * Post Card Component
 * 
 * Displays a single forum post with author info and actions
 */

import React, { useState } from 'react';
import { Heart, MessageSquare, Check, Clock, MoreHorizontal } from 'lucide-react';
import { ForumPost } from '../../../services/collaborationService';
import { formatDistanceToNow } from 'date-fns';

interface PostCardProps {
  post: ForumPost;
  isOp?: boolean;
  onReply?: (postId: string) => void;
  onLike?: (postId: string) => void;
}

const PostCard: React.FC<PostCardProps> = ({ post, isOp = false, onReply, onLike }) => {
  const [liked, setLiked] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const handleLike = () => {
    if (!liked) {
      setLiked(true);
      onLike?.(post.post_id);
    }
  };

  const authorInitials = post.author.first_name
    ? `${post.author.first_name.charAt(0)}${post.author.last_name?.charAt(0) || ''}`
    : post.author.username.charAt(0).toUpperCase();

  return (
    <div className={`flex space-x-4 p-4 rounded-lg ${
      post.is_accepted_answer ? 'bg-green-50 border border-green-200' : 'bg-white'
    }`}>
      {/* Avatar */}
      <div className="flex-shrink-0">
        {post.author.avatar_url ? (
          <img
            src={post.author.avatar_url}
            alt={post.author.username}
            className="w-10 h-10 rounded-full"
          />
        ) : (
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-medium">
            {authorInitials}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="font-medium text-gray-900">
              {post.author.first_name && post.author.last_name
                ? `${post.author.first_name} ${post.author.last_name}`
                : post.author.username}
            </span>
            <span className="text-gray-500">@{post.author.username}</span>
            {isOp && (
              <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">
                OP
              </span>
            )}
            {post.is_accepted_answer && (
              <span className="flex items-center space-x-1 px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
                <Check className="w-3 h-3" />
                <span>Answer</span>
              </span>
            )}
          </div>

          {/* Menu */}
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-1 text-gray-400 hover:text-gray-600 rounded"
            >
              <MoreHorizontal className="w-4 h-4" />
            </button>
            {showMenu && (
              <div className="absolute right-0 mt-1 w-32 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-10">
                <button className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50">
                  Copy Link
                </button>
                <button className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50">
                  Report
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Timestamp */}
        <div className="flex items-center space-x-1 text-xs text-gray-400 mt-1">
          <Clock className="w-3 h-3" />
          <span>{formatDistanceToNow(new Date(post.created_at || new Date()), { addSuffix: true })}</span>
        </div>

        {/* Post Content */}
        <div className="mt-3 text-gray-800 whitespace-pre-wrap">
          {post.content}
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-4 mt-4">
          <button
            onClick={handleLike}
            className={`flex items-center space-x-1.5 text-sm transition-colors ${
              liked ? 'text-red-500' : 'text-gray-500 hover:text-red-500'
            }`}
          >
            <Heart className={`w-4 h-4 ${liked ? 'fill-current' : ''}`} />
            <span>{post.like_count + (liked ? 1 : 0)}</span>
          </button>

          <button
            onClick={() => onReply?.(post.post_id)}
            className="flex items-center space-x-1.5 text-sm text-gray-500 hover:text-blue-600 transition-colors"
          >
            <MessageSquare className="w-4 h-4" />
            <span>Reply</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default PostCard;
