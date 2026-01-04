/**
 * Comment Form Component
 * 
 * Form for adding comments to content
 */

import React, { useState } from 'react';
import { X, Loader } from 'lucide-react';
import { addComment } from '../../../services/collaborationService';

interface CommentFormProps {
  contentId: string;
  contentType: 'lesson' | 'course' | 'concept' | 'learning_path';
  parentCommentId?: string;
  onSubmit: () => void;
  onCancel: () => void;
}

const CommentForm: React.FC<CommentFormProps> = ({
  contentId,
  contentType,
  parentCommentId,
  onSubmit,
  onCancel
}) => {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (content.trim().length < 3) {
      setError('Comment must be at least 3 characters');
      return;
    }

    setLoading(true);

    try {
      const result = await addComment(
        contentId,
        contentType,
        content.trim(),
        parentCommentId
      );
      
      if (result.success) {
        onSubmit();
      } else {
        setError(result.error || 'Failed to add comment');
      }
    } catch (err) {
      setError('An error occurred while posting your comment');
      console.error('Add comment error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <form onSubmit={handleSubmit}>
        {/* Reply indicator */}
        {parentCommentId && (
          <div className="flex items-center justify-between mb-2 text-sm text-gray-500">
            <span>Replying to a comment</span>
            <button
              type="button"
              onClick={onCancel}
              className="text-blue-600 hover:underline"
            >
              Cancel reply
            </button>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-3 p-2 bg-red-50 text-red-700 rounded text-sm">
            {error}
          </div>
        )}

        {/* Textarea */}
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Share your thoughts, questions, or insights..."
          rows={3}
          maxLength={2000}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          required
        />

        {/* Character count and actions */}
        <div className="flex items-center justify-between mt-3">
          <span className="text-xs text-gray-500">
            {content.length}/2000 characters
          </span>

          <div className="flex items-center space-x-2">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-gray-700 hover:bg-gray-200 rounded-lg transition-colors text-sm"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || content.trim().length < 3}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 text-sm"
            >
              {loading ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  <span>Posting...</span>
                </>
              ) : (
                <span>Post Comment</span>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default CommentForm;
