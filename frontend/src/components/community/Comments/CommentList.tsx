/**
 * Comment List Component
 * 
 * Displays a list of comments for content
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Loader, MessageSquare } from 'lucide-react';
import { getContentComments, likeComment, ContentComment } from '../../../services/collaborationService';
import CommentCard from './CommentCard';
import CommentForm from './CommentForm';

interface CommentListProps {
  contentId: string;
  contentType: 'lesson' | 'course' | 'concept' | 'learning_path';
  onCommentAdded?: () => void;
}

const CommentList: React.FC<CommentListProps> = ({
  contentId,
  contentType,
  onCommentAdded
}) => {
  const [comments, setComments] = useState<ContentComment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [replyingTo, setReplyingTo] = useState<string | null>(null);

  const loadComments = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await getContentComments(contentId, contentType);
      if (result.success) {
        setComments(result.comments);
      } else {
        setError('Failed to load comments');
      }
    } catch (err) {
      setError('An error occurred while loading comments');
      console.error('Load comments error:', err);
    } finally {
      setLoading(false);
    }
  }, [contentId, contentType]);

  useEffect(() => {
    loadComments();
  }, [loadComments]);

  const handleCommentAdded = () => {
    setShowForm(false);
    setReplyingTo(null);
    loadComments();
    onCommentAdded?.();
  };

  const handleLike = async (commentId: string) => {
    await likeComment(commentId);
    loadComments();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader className="w-6 h-6 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Loading comments...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-red-500 mb-2">{error}</div>
        <button
          onClick={loadComments}
          className="text-blue-600 hover:underline"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="mt-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <MessageSquare className="w-5 h-5 text-gray-500" />
          <h3 className="text-lg font-semibold text-gray-900">
            Comments ({comments.length})
          </h3>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
        >
          {showForm ? 'Cancel' : 'Add Comment'}
        </button>
      </div>

      {/* Comment Form */}
      {showForm && (
        <div className="mb-6">
          <CommentForm
            contentId={contentId}
            contentType={contentType}
            parentCommentId={replyingTo || undefined}
            onSubmit={handleCommentAdded}
            onCancel={() => {
              setShowForm(false);
              setReplyingTo(null);
            }}
          />
        </div>
      )}

      {/* Comments List */}
      {comments.length === 0 ? (
        <div className="text-center py-8 bg-gray-50 rounded-lg">
          <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No comments yet. Be the first to comment!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {comments.map((comment) => (
            <div key={comment.comment_id} className="bg-white rounded-lg border border-gray-200 p-4">
              <CommentCard
                comment={comment}
                onReply={(commentId) => {
                  setReplyingTo(commentId);
                  setShowForm(true);
                }}
                onLike={handleLike}
              />

              {/* Nested replies could be rendered here */}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CommentList;
