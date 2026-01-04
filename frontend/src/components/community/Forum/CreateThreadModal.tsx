/**
 * Create Thread Modal
 * 
 * Modal for creating new forum threads
 */

import React, { useState } from 'react';
import { X, Loader } from 'lucide-react';
import { Forum, createThread } from '../../../services/collaborationService';

interface CreateThreadModalProps {
  forums: Forum[];
  onClose: () => void;
  onThreadCreated: (thread: { thread_id: string; forum_id: string }) => void;
}

const CreateThreadModal: React.FC<CreateThreadModalProps> = ({ forums, onClose, onThreadCreated }) => {
  const [selectedForum, setSelectedForum] = useState<string>('');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!selectedForum) {
      setError('Please select a forum');
      return;
    }

    if (title.trim().length < 5) {
      setError('Title must be at least 5 characters');
      return;
    }

    if (content.trim().length < 20) {
      setError('Content must be at least 20 characters');
      return;
    }

    setLoading(true);

    try {
      const result = await createThread(selectedForum, title.trim(), content.trim());
      
      if (result.success && result.thread_id) {
        onThreadCreated({
          thread_id: result.thread_id,
          forum_id: selectedForum
        });
      } else {
        setError(result.error || 'Failed to create thread');
      }
    } catch (err) {
      setError('An error occurred while creating the thread');
      console.error('Create thread error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Create New Thread</h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 140px)' }}>
          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Forum Selection */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Forum <span className="text-red-500">*</span>
            </label>
            <select
              value={selectedForum}
              onChange={(e) => setSelectedForum(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              <option value="">Choose a forum...</option>
              {forums.map((forum) => (
                <option key={forum.forum_id} value={forum.forum_id}>
                  {forum.icon} {forum.name}
                </option>
              ))}
            </select>
          </div>

          {/* Thread Title */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Thread Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="What would you like to discuss?"
              maxLength={200}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              {title.length}/200 characters
            </p>
          </div>

          {/* Thread Content */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Content <span className="text-red-500">*</span>
            </label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Share your thoughts, questions, or ideas..."
              rows={6}
              maxLength={5000}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              {content.length}/5000 characters
            </p>
          </div>

          {/* Guidelines */}
          <div className="bg-blue-50 rounded-lg p-4 mb-6">
            <h4 className="text-sm font-medium text-blue-900 mb-2">Thread Guidelines</h4>
            <ul className="text-xs text-blue-700 space-y-1">
              <li>• Be respectful and constructive in discussions</li>
              <li>• Search before posting to avoid duplicates</li>
              <li>• Use clear, descriptive titles</li>
              <li>• Provide context and details in your posts</li>
            </ul>
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
              disabled={loading}
              className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  <span>Creating...</span>
                </>
              ) : (
                <span>Create Thread</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateThreadModal;
