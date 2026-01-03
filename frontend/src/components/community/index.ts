// Community Components Barrel Export
// Centralized exports for all community and collaboration features

// Main Dashboard
export { default as CommunityDashboard } from './CommunityDashboard';

// User Connections
export { default as UserConnections } from './UserConnections';
export { default as ConnectionRequestModal } from './ConnectionRequestModal';

// Forum Components
export { default as ForumList } from './Forum/ForumList';
export { default as ThreadList } from './Forum/ThreadList';
export { default as ThreadDetail } from './Forum/ThreadDetail';
export { default as PostCard } from './Forum/PostCard';
export { default as CreateThreadModal } from './Forum/CreateThreadModal';
export { default as CreatePostModal } from './Forum/CreatePostModal';

// Comment Components
export { default as CommentList } from './Comments/CommentList';
export { default as CommentCard } from './Comments/CommentCard';
export { default as CommentForm } from './Comments/CommentForm';

// Types (re-exported from service)
export * from '../../services/collaborationService';
