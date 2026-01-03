/**
 * Create Post Modal
 * 
 * Modal for creating replies to forum threads
 */

import React, { useState } from 'react';
import { X, Loader } from 'lucide-react';
import { createPost } from '../../../services/collaborationService';

interface CreatePostModalProps {
  threadId: string;
  parentPostId?: string;
  onClose: () => void;
  onPostCreated: (content: string, parentPostId?: string) => void;
}

const CreatePostModal: React.FC<CreatePostModalProps> = ({
  threadId,
  parentPostId,
  onClose,
  onPostCreated
}) => {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (content.trim().length < 5) {
      setError('Reply must be at least 5 characters');
      return;
    }

    setLoading(true);

    try {
      const result = await createPost(threadId, content.trim(), parentPostId);
      
      if (result.success) {
        onPostCreated(content.trim(), parentPostId);
      } else {
        setError(result.error || 'Failed to create reply');
      }
    } catch (err) {
      setError('An error occurred while posting your reply');
      console.error('Create post error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {parentPostId ? 'Reply to Post' : 'Write a Reply'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6">
          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Content */}
          <div className="mb-6">
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={parentPostId ? "Write your reply..." : "Share your thoughts..."}
              rows={6}
              maxLength={5000}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              autoFocus
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              {content.length}/5000 characters
            </p>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || content.trim().length < 5}
              className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  <span>Posting...</span>
                </>
              ) : (
                <span>Post Reply</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreatePostModal;
