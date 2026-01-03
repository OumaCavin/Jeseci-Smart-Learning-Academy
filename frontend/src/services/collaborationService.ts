/**
 * Collaboration Service for Jeseci Smart Learning Academy
 * 
 * Handles all API calls for collaboration and community features
 * including user connections, discussion forums, and content comments.
 */

import { apiService } from '../api';

// ============================================================================
// Types
// ============================================================================

export interface User {
  user_id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  avatar_url?: string;
}

export interface Connection {
  connection_id: string;
  status: 'pending' | 'accepted' | 'blocked';
  created_at?: string;
  updated_at?: string;
  user: User;
}

export interface ConnectionRequest {
  connection_id: string;
  created_at?: string;
  requester: User;
}

export interface Forum {
  forum_id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  thread_count: number;
  post_count: number;
  last_activity?: string;
}

export interface ForumThread {
  thread_id: string;
  title: string;
  view_count: number;
  reply_count: number;
  is_pinned: boolean;
  is_locked: boolean;
  created_at?: string;
  updated_at?: string;
  author: {
    username: string;
    first_name?: string;
    last_name?: string;
  };
}

export interface ThreadDetail extends ForumThread {
  content: string;
  forum_id: string;
  forum_name: string;
  posts: ForumPost[];
}

export interface ForumPost {
  post_id: string;
  content: string;
  like_count: number;
  is_accepted_answer: boolean;
  created_at?: string;
  updated_at?: string;
  author: {
    username: string;
    first_name?: string;
    last_name?: string;
    avatar_url?: string;
  };
}

export interface ContentComment {
  comment_id: string;
  content: string;
  like_count: number;
  parent_comment_id?: string;
  created_at?: string;
  updated_at?: string;
  author: {
    username: string;
    first_name?: string;
    last_name?: string;
    avatar_url?: string;
  };
}

export interface Pagination {
  page: number;
  limit: number;
  total_count: number;
  total_pages?: number;
}

export interface ThreadListResponse {
  success: boolean;
  threads: ForumThread[];
  pagination: Pagination;
  error?: string;
}

export interface ThreadResponse {
  success: boolean;
  thread?: ThreadDetail;
  error?: string;
}

// ============================================================================
// API Functions
// ============================================================================

/**
 * Create a connection request to another user
 */
export const sendConnectionRequest = async (targetUserId: number): Promise<{
  success: boolean;
  connection_id?: string;
  status?: string;
  error?: string;
}> => {
  try {
    const response = await apiService.post('/walker/connection_create', {
      target_user_id: targetUserId
    });
    return response.data;
  } catch (error: any) {
    console.error('Error sending connection request:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to send connection request'
    };
  }
};

/**
 * Accept or reject a connection request
 */
export const respondToConnection = async (
  connectionId: string,
  action: 'accept' | 'reject'
): Promise<{
  success: boolean;
  connection_id?: string;
  status?: string;
  error?: string;
}> => {
  try {
    const response = await apiService.post('/walker/connection_respond', {
      connection_id: connectionId,
      action: action
    });
    return response.data;
  } catch (error: any) {
    console.error('Error responding to connection:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to respond to connection'
    };
  }
};

/**
 * Get user's connections
 */
export const getConnections = async (
  status?: 'pending' | 'accepted' | 'blocked'
): Promise<{
  success: boolean;
  connections: Connection[];
  total: number;
}> => {
  try {
    const response = await apiService.get('/walker/connections_list', {
      params: { status }
    });
    return response.data;
  } catch (error: any) {
    console.error('Error getting connections:', error);
    return {
      success: false,
      connections: [],
      total: 0
    };
  }
};

/**
 * Get pending connection requests
 */
export const getConnectionRequests = async (): Promise<{
  success: boolean;
  requests: ConnectionRequest[];
  total: number;
}> => {
  try {
    const response = await apiService.get('/walker/connection_requests');
    return response.data;
  } catch (error: any) {
    console.error('Error getting connection requests:', error);
    return {
      success: false,
      requests: [],
      total: 0
    };
  }
};

/**
 * Remove a connection
 */
export const removeConnection = async (connectionId: string): Promise<{
  success: boolean;
  message?: string;
  error?: string;
}> => {
  try {
    const response = await apiService.post('/walker/connection_remove', {
      connection_id: connectionId
    });
    return response.data;
  } catch (error: any) {
    console.error('Error removing connection:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to remove connection'
    };
  }
};

/**
 * Search for users to connect with
 */
export const searchUsers = async (
  query: string,
  limit: number = 10
): Promise<{
  success: boolean;
  users: User[];
  total: number;
}> => {
  try {
    const response = await apiService.get('/walker/users_search', {
      params: { query, limit }
    });
    return response.data;
  } catch (error: any) {
    console.error('Error searching users:', error);
    return {
      success: false,
      users: [],
      total: 0
    };
  }
};

// ============================================================================
// Forum API Functions
// ============================================================================

/**
 * Get all forums
 */
export const getForums = async (): Promise<{
  success: boolean;
  forums: Forum[];
  total: number;
}> => {
  try {
    const response = await apiService.get('/walker/forums_list');
    return response.data;
  } catch (error: any) {
    console.error('Error getting forums:', error);
    return {
      success: false,
      forums: [],
      total: 0
    };
  }
};

/**
 * Create a new forum thread
 */
export const createThread = async (
  forumId: string,
  title: string,
  content: string
): Promise<{
  success: boolean;
  thread_id?: string;
  forum_id?: string;
  created_at?: string;
  error?: string;
}> => {
  try {
    const response = await apiService.post('/walker/forum_thread_create', {
      forum_id: forumId,
      title: title,
      content: content
    });
    return response.data;
  } catch (error: any) {
    console.error('Error creating thread:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to create thread'
    };
  }
};

/**
 * Get threads for a forum
 */
export const getThreads = async (
  forumId: string,
  page: number = 1,
  limit: number = 20
): Promise<ThreadListResponse> => {
  try {
    const response = await apiService.get('/walker/forum_threads', {
      params: { forum_id: forumId, page, limit }
    });
    return response.data;
  } catch (error: any) {
    console.error('Error getting threads:', error);
    return {
      success: false,
      threads: [],
      pagination: { page, limit, total_count: 0 }
    };
  }
};

/**
 * Get a single thread with all posts
 */
export const getThread = async (threadId: string): Promise<ThreadResponse> => {
  try {
    const response = await apiService.get('/walker/forum_thread', {
      params: { thread_id: threadId }
    });
    return response.data;
  } catch (error: any) {
    console.error('Error getting thread:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to get thread'
    };
  }
};

/**
 * Create a reply post in a thread
 */
export const createPost = async (
  threadId: string,
  content: string,
  parentPostId?: string
): Promise<{
  success: boolean;
  post_id?: string;
  thread_id?: string;
  created_at?: string;
  error?: string;
}> => {
  try {
    const response = await apiService.post('/walker/forum_post_create', {
      thread_id: threadId,
      content: content,
      parent_post_id: parentPostId || ''
    });
    return response.data;
  } catch (error: any) {
    console.error('Error creating post:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to create post'
    };
  }
};

/**
 * Like/unlike a forum post
 */
export const likeForumPost = async (postId: string): Promise<{
  success: boolean;
  like_count?: number;
  error?: string;
}> => {
  try {
    const response = await apiService.post('/walker/forum_post_like', {
      post_id: postId
    });
    return response.data;
  } catch (error: any) {
    console.error('Error liking post:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to like post'
    };
  }
};

// ============================================================================
// Content Comment API Functions
// ============================================================================

/**
 * Add a comment to content (lesson, course, concept, etc.)
 */
export const addComment = async (
  contentId: string,
  contentType: 'lesson' | 'course' | 'concept' | 'learning_path',
  content: string,
  parentCommentId?: string
): Promise<{
  success: boolean;
  comment_id?: string;
  content_id?: string;
  content_type?: string;
  created_at?: string;
  error?: string;
}> => {
  try {
    const response = await apiService.post('/walker/content_comment_add', {
      content_id: contentId,
      content_type: contentType,
      content: content,
      parent_comment_id: parentCommentId || ''
    });
    return response.data;
  } catch (error: any) {
    console.error('Error adding comment:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to add comment'
    };
  }
};

/**
 * Get comments for content
 */
export const getContentComments = async (
  contentId: string,
  contentType: 'lesson' | 'course' | 'concept' | 'learning_path',
  page: number = 1,
  limit: number = 50
): Promise<{
  success: boolean;
  comments: ContentComment[];
  pagination: Pagination;
  error?: string;
}> => {
  try {
    const response = await apiService.get('/walker/content_comments', {
      params: { content_id: contentId, content_type: contentType, page, limit }
    });
    return response.data;
  } catch (error: any) {
    console.error('Error getting comments:', error);
    return {
      success: false,
      comments: [],
      pagination: { page, limit, total_count: 0 }
    };
  }
};

/**
 * Like/unlike a comment
 */
export const likeComment = async (commentId: string): Promise<{
  success: boolean;
  like_count?: number;
  error?: string;
}> => {
  try {
    const response = await apiService.post('/walker/content_comment_like', {
      comment_id: commentId
    });
    return response.data;
  } catch (error: any) {
    console.error('Error liking comment:', error);
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to like comment'
    };
  }
};

export default {
  // Connections
  sendConnectionRequest,
  respondToConnection,
  getConnections,
  getConnectionRequests,
  removeConnection,
  searchUsers,
  // Forums
  getForums,
  createThread,
  getThreads,
  getThread,
  createPost,
  likeForumPost,
  // Comments
  addComment,
  getContentComments,
  likeComment
};
