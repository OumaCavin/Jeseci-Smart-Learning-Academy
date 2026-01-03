/**
 * Thread Detail Component
 * 
 * Displays a complete thread with all posts
 */

import React, { useState, useEffect, useCallback } from 'react';
import { ArrowLeft, MessageSquare, Eye, Clock, Lock, Pin, Loader } from 'lucide-react';
import { getThread, createPost, likeForumPost, ThreadDetail, ForumPost } from '../../services/collaborationService';
import PostCard from './PostCard';
import CreatePostModal from './CreatePostModal';

interface ThreadDetailProps {
  threadId: string;
  onBack?: () => void;
}

const ThreadDetail: React.FC<ThreadDetailProps> = ({ threadId, onBack }) => {
  const [thread, setThread] = useState<ThreadDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showReplyModal, setShowReplyModal] = useState(false);
  const [replyingTo, setReplyingTo] = useState<string | null>(null);

  const loadThread = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await getThread(threadId);
      if (result.success && result.thread) {
        setThread(result.thread);
      } else {
        setError(result.error || 'Failed to load thread');
      }
    } catch (err) {
      setError('An error occurred while loading the thread');
      console.error('Load thread error:', err);
    } finally {
      setLoading(false);
    }
  }, [threadId]);

  useEffect(() => {
    loadThread();
  }, [loadThread]);

  const handlePostCreated = async (content: string, parentPostId?: string) => {
    const result = await createPost(threadId, content, parentPostId);
    
    if (result.success) {
      setShowReplyModal(false);
      setReplyingTo(null);
      loadThread();
    }
  };

  const handleLikePost = async (postId: string) => {
    await likeForumPost(postId);
    // Reload to get updated like count
    loadThread();
  };

  const handleReply = (postId: string) => {
    setReplyingTo(postId);
    setShowReplyModal(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-gray-600">Loading thread...</span>
      </div>
    );
  }

  if (error || !thread) {
    return (
      <div className="text-center py-12">
        <div className="text-red-500 mb-4">{error || 'Thread not found'}</div>
        <button
          onClick={loadThread}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Back Button */}
      {onBack && (
        <button
          onClick={onBack}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Forums</span>
        </button>
      )}

      {/* Thread Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <div className="flex items-start space-x-4">
          {/* Thread Status Icons */}
          <div className="flex flex-col items-center space-y-2 pt-1">
            {thread.is_pinned && (
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center" title="Pinned">
                <Pin className="w-4 h-4 text-blue-600" />
              </div>
            )}
            {thread.is_locked && (
              <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center" title="Locked">
                <Lock className="w-4 h-4 text-gray-600" />
              </div>
            )}
          </div>

          {/* Thread Info */}
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900">{thread.title}</h1>
            
            <div className="flex items-center space-x-4 mt-3 text-sm text-gray-500">
              <span className="flex items-center space-x-1">
                <span className="font-medium text-gray-700">{thread.author.username}</span>
              </span>
              <span className="flex items-center space-x-1">
                <Clock className="w-4 h-4" />
                <span>{new Date(thread.created_at || '').toLocaleDateString()}</span>
              </span>
              <span className="flex items-center space-x-1">
                <Eye className="w-4 h-4" />
                <span>{thread.view_count} views</span>
              </span>
              <span className="flex items-center space-x-1">
                <MessageSquare className="w-4 h-4" />
                <span>{thread.posts.length} posts</span>
              </span>
            </div>

            {/* Thread Content */}
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <div className="text-gray-800 whitespace-pre-wrap">{thread.content}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Posts */}
      <div className="space-y-4 mb-6">
        {thread.posts.map((post, index) => (
          <PostCard
            key={post.post_id}
            post={post}
            isOp={index === 0}
            onReply={handleReply}
            onLike={handleLikePost}
          />
        ))}
      </div>

      {/* Reply Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        {!thread.is_locked ? (
          <button
            onClick={() => {
              setReplyingTo(null);
              setShowReplyModal(true);
            }}
            className="w-full py-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-blue-500 hover:text-blue-600 transition-colors"
          >
            <MessageSquare className="w-5 h-5 inline-block mr-2" />
            Write a reply...
          </button>
        ) : (
          <div className="text-center py-4 text-gray-500">
            <Lock className="w-5 h-5 inline-block mr-2" />
            This thread is locked and no new replies are allowed.
          </div>
        )}
      </div>

      {/* Reply Modal */}
      {showReplyModal && (
        <CreatePostModal
          threadId={threadId}
          parentPostId={replyingTo || undefined}
          onClose={() => {
            setShowReplyModal(false);
            setReplyingTo(null);
          }}
          onPostCreated={handlePostCreated}
        />
      )}
    </div>
  );
};

export default ThreadDetail;
