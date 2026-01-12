/**
 * Advanced Collaboration Service
 * 
 * This service provides typed API calls for advanced collaboration features:
 * - Reputation and upvoting system
 * - Study groups with shared workspaces
 * - Mentorship connections
 * - Content moderation tools
 * - Peer review system
 */

import { apiService } from '../api';

// Types for Reputation System
export interface UserReputation {
  user_id: number;
  total_reputation: number;
  level: number;
  rank?: string;
  reputation_change: number;
  total_upvotes: number;
  helpful_count: number;
  streak_days: number;
  reputation_points: number;
  total_upvotes_received: number;
  total_downvotes_received: number;
  total_accepted_answers: number;
  helpful_flags_count: number;
}

export interface LeaderboardEntry {
  user_id: number;
  username: string;
  total_reputation: number;
  level: number;
  rank: number;
}

export interface ReputationEvent {
  event_id: string;
  user_id: number;
  event_type: string;
  points_change: number;
  created_at: string;
}

// Types for Study Groups
export interface StudyGroup {
  group_id: string;
  name: string;
  description: string;
  learning_goal: string;
  target_topic: string;
  max_members: number;
  is_public: boolean;
  is_active: boolean;
  created_by: number;
  member_count: number;
  creator_name: string;
  created_at: string;
}

export interface StudyGroupMember {
  membership_id: string;
  group_id: string;
  user_id: number;
  role: 'owner' | 'admin' | 'member';
  joined_at: string;
  last_active_at: string;
}

export interface StudyGroupNote {
  note_id: string;
  group_id: string;
  author_id: number;
  author_name: string;
  title: string;
  content: string;
  tags: string[];
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
}

export interface StudyGroupGoal {
  goal_id: string;
  group_id: string;
  title: string;
  description: string;
  target_completion_date: string;
  is_completed: boolean;
  completed_at: string;
  created_at: string;
}

export interface StudyGroupMessage {
  message_id: string;
  group_id: string;
  user_id: number;
  username: string;
  avatar_url: string;
  content: string;
  message_type: 'text' | 'link' | 'file' | 'milestone';
  file_url: string;
  created_at: string;
}

export interface StudyGroupDiscussion {
  discussion_id: string;
  group_id: string;
  user_id: number;
  username: string;
  topic: string;
  content: string;
  is_pinned: boolean;
  reply_count: number;
  last_reply_at: string;
  created_at: string;
}

export interface GroupEvent {
  event_id: string;
  group_id: string;
  title: string;
  description: string;
  event_time: string;
  duration_minutes: number;
  created_by: number;
  creator_name: string;
  created_at: string;
  participant_count?: number;
  is_participating?: boolean;
}

// Types for Mentorship
export interface MentorshipProfile {
  user_id: number;
  title?: string;
  is_available: boolean;
  expertise_areas: string[];
  years_experience: number;
  teaching_style: string;
  bio: string;
  availability_hours: string;
  max_mentees: number;
  current_mentees_count: number;
  total_sessions_completed: number;
  average_rating: number;
  username: string;
  first_name: string;
  last_name: string;
  avatar_url: string;
}

export interface MentorshipRequest {
  request_id: string;
  mentor_id: number;
  mentee_id: number;
  role: 'mentor' | 'mentee';
  status: 'pending' | 'accepted' | 'rejected' | 'completed' | 'cancelled';
  topic: string;
  goals: string;
  preferred_schedule: string;
  message: string;
  response_message: string;
  requested_at: string;
  responded_at: string;
  completed_at: string;
  created_at: string;
  mentor_name?: string;
  mentee_name?: string;
  mentor_username?: string;
  mentee_username?: string;
}

export interface MentorshipSession {
  session_id: string;
  mentorship_id: number;
  mentor_id: number;
  mentee_id: number;
  scheduled_at: string;
  duration_minutes: number;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled' | 'no_show';
  topic: string;
  notes: string;
  outcome: string;
  mentor_feedback: string;
  mentee_feedback: string;
  mentor_rating: number;
  mentee_rating: number;
  started_at: string;
  ended_at: string;
  created_at: string;
}

// Types for Moderation
export interface ContentReport {
  report_id: string;
  reporter_id: number;
  content_id: string;
  content_type: string;
  report_reason: string;
  additional_info: string;
  status: 'pending' | 'reviewed' | 'resolved' | 'dismissed';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  reported_at: string;
  reviewed_by: number;
  reviewed_at: string;
  resolution_notes: string;
}

export interface ModerationReport {
  id: number;
  reporterId: number;
  reporterUsername: string;
  contentType: string;
  contentId: number;
  contentAuthorId: number;
  contentAuthorUsername: string;
  reason: string;
  description: string;
  status: 'pending' | 'reviewed' | 'resolved' | 'dismissed';
  priority: 'low' | 'medium' | 'high' | 'critical';
  createdAt: string;
  updatedAt: string;
}

export interface ModerationQueueItem {
  queue_id: string;
  content_id: string;
  content_type: string;
  report_id: number;
  priority: string;
  status: 'pending' | 'in_review' | 'resolved';
  assigned_to: number;
  submitted_at: string;
  assigned_at: string;
  resolved_at: string;
  resolution_summary: string;
  report_reason: string;
  additional_info: string;
  reporter_username: string;
  total_pending?: number;
}

export interface ModerationAction {
  id: string;
  action_id: string;
  moderator_id: number;
  moderator_username?: string;
  content_id: string;
  content_type: string;
  action_type: string;
  reason: string;
  notes: string;
  is_reversed: boolean;
  report_id?: number;
  duration?: number;
  created_at: string;
}

export interface ModerationStats {
  pending_reports: number;
  resolved_reports: number;
  dismissed_reports: number;
  avg_resolution_time: number;
  total_reports: number;
  reports_by_reason: Record<string, number>;
  top_reasons?: Array<{ reason: string; count: number }>;
  recent_actions: number;
}

// Types for Peer Review
export interface PeerReviewSubmission {
  submission_id: string;
  id?: string;
  user_id: number;
  author_username?: string;
  title: string;
  description: string;
  content_type: string;
  average_rating?: number;
  reviewer_username?: string;
  related_content_id: string;
  related_content_type: string;
  status: 'pending' | 'assigned' | 'in_progress' | 'completed' | 'declined';
  max_reviewers: number;
  current_reviewers: number;
  feedback_count: number;
  created_at: string;
  updated_at: string;
}

export interface PeerReviewAssignment {
  assignment_id: string;
  id?: string;
  submission_id: string;
  reviewer_id: number;
  status: 'assigned' | 'in_progress' | 'completed' | 'declined';
  assigned_at: string;
  completed_at: string;
  deadline: string;
  submission_title: string;
  submission_description: string;
  author_username: string;
  feedback_rating?: number;
}

export interface PeerReviewFeedback {
  feedback_id: string;
  assignment_id: string;
  submission_id: string;
  reviewer_id: number;
  overall_rating: number;
  strengths: string;
  improvements: string;
  comments: string;
  is_approved: boolean;
  author_response: string;
  feedback_upvotes: number;
  username: string;
  avatar_url: string;
  created_at: string;
}

// Types for Admin
export interface UserActivityStats {
  totalUsers: number;
  activeUsers: number;
  newUsersToday: number;
  newUsersThisWeek: number;
  avgSessionDuration: number;
  topActiveUsers: Array<{
    userId: string;
    username: string;
    actionsCount: number;
    lastActive: string;
  }>;
  usersByRole: Array<{
    role: string;
    count: number;
  }>;
  activityByHour: Array<{
    hour: number;
    count: number;
  }>;
}

export interface UserActivityLog {
  userId: string;
  username: string;
  action: string;
  details: string;
  timestamp: string;
  ipAddress: string;
}

export interface DatabaseStats {
  totalSize: string;
  totalTables: number;
  totalRows: number;
  activeConnections: number;
  avgQueryTime: number;
  uptime: string;
}

export interface TableInfo {
  tableName: string;
  rows: number;
  size: string;
  indexes: number;
  lastModified: string;
}

export interface TableActivity {
  tableName: string;
  reads: number;
  writes: number;
  updates: number;
  deletes: number;
  avgQueryTime: number;
  peakConnections: number;
}

export interface CacheStats {
  totalSize: string;
  entryCount: number;
  hitRate: number;
  missRate: number;
  lastCleared: string;
  memoryUsage: string;
}

export interface CacheEntry {
  key: string;
  type: string;
  size: string;
  createdAt: string;
  lastAccessed: string;
  hitCount: number;
}

export interface CacheRegion {
  name: string;
  entryCount: number;
  size: string;
  hitRate: number;
}

// API Response types
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Service class for Advanced Collaboration features
class AdvancedCollaborationService {
  // =============================================================================
  // REPUTATION SYSTEM API CALLS
  // =============================================================================

  /**
   * Get current user's reputation profile
   */
  async getUserReputation(): Promise<ApiResponse<UserReputation>> {
    try {
      const response = await apiService.post('/walker/user_reputation', {});
      return response.data;
    } catch (error) {
      console.error('Error fetching user reputation:', error);
      return { success: false, error: 'Failed to fetch reputation' };
    }
  }

  /**
   * Get reputation leaderboard
   */
  async getReputationLeaderboard(limit: number = 10): Promise<ApiResponse<UserReputation[]>> {
    try {
      const response = await apiService.post('/walker/reputation_leaderboard', { limit });
      return response.data;
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
      return { success: false, error: 'Failed to fetch leaderboard' };
    }
  }

  /**
   * Upvote or downvote content
   */
  async upvoteContent(
    contentId: string,
    contentType: string,
    voteType: 1 | -1 = 1
  ): Promise<ApiResponse<{ action: string; vote_change: number }>> {
    try {
      const response = await apiService.post('/walker/content_upvote', {
        content_id: contentId,
        content_type: contentType,
        vote_type: voteType
      });
      return response.data;
    } catch (error) {
      console.error('Error upvoting content:', error);
      return { success: false, error: 'Failed to submit vote' };
    }
  }

  // =============================================================================
  // STUDY GROUPS API CALLS
  // =============================================================================

  /**
   * Create a new study group
   */
  async createStudyGroup(
    name: string,
    description: string,
    options?: {
      learningGoal?: string;
      targetTopic?: string;
      isPublic?: boolean;
    }
  ): Promise<ApiResponse<{ group: StudyGroup }>> {
    try {
      const response = await apiService.post('/walker/study_group_create', {
        name,
        description,
        learning_goal: options?.learningGoal || '',
        target_topic: options?.targetTopic || '',
        is_public: options?.isPublic ?? true
      });
      return response.data;
    } catch (error) {
      console.error('Error creating study group:', error);
      return { success: false, error: 'Failed to create study group' };
    }
  }

  /**
   * Get list of study groups
   */
  async getStudyGroups(
    options?: {
      topic?: string;
      limit?: number;
      offset?: number;
    }
  ): Promise<ApiResponse<StudyGroup[]>> {
    try {
      const response = await apiService.post('/walker/study_groups_list', {
        topic: options?.topic || '',
        limit: options?.limit || 20,
        offset: options?.offset || 0
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching study groups:', error);
      return { success: false, error: 'Failed to fetch study groups' };
    }
  }

  /**
   * Join a study group
   */
  async joinStudyGroup(groupId: string): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await apiService.post('/walker/study_group_join', { group_id: groupId });
      return response.data;
    } catch (error) {
      console.error('Error joining study group:', error);
      return { success: false, error: 'Failed to join study group' };
    }
  }

  /**
   * Get notes from a study group
   */
  async getGroupNotes(
    groupId: string,
    options?: { limit?: number; offset?: number }
  ): Promise<ApiResponse<StudyGroupNote[]>> {
    try {
      const response = await apiService.post('/walker/study_group_notes', {
        group_id: groupId,
        limit: options?.limit || 50,
        offset: options?.offset || 0
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching group notes:', error);
      return { success: false, error: 'Failed to fetch group notes' };
    }
  }

  /**
   * Create a note in a study group
   */
  async createGroupNote(
    groupId: string,
    title: string,
    content: string,
    tags?: string[]
  ): Promise<ApiResponse<{ note: StudyGroupNote }>> {
    try {
      const response = await apiService.post('/walker/study_group_note_create', {
        group_id: groupId,
        title,
        content,
        tags: tags || []
      });
      return response.data;
    } catch (error) {
      console.error('Error creating group note:', error);
      return { success: false, error: 'Failed to create note' };
    }
  }

  /**
   * Get goals for a study group
   */
  async getGroupGoals(groupId: string): Promise<ApiResponse<StudyGroupGoal[]>> {
    try {
      const response = await apiService.post('/walker/study_group_goals', { group_id: groupId });
      return response.data;
    } catch (error) {
      console.error('Error fetching group goals:', error);
      return { success: false, error: 'Failed to fetch group goals' };
    }
  }

  /**
   * Create a goal for a study group
   */
  async createGroupGoal(
    groupId: string,
    title: string,
    options?: {
      description?: string;
      targetCompletionDate?: string;
    }
  ): Promise<ApiResponse<{ goal: StudyGroupGoal }>> {
    try {
      const response = await apiService.post('/walker/study_group_goal_create', {
        group_id: groupId,
        title,
        description: options?.description || '',
        target_completion_date: options?.targetCompletionDate || ''
      });
      return response.data;
    } catch (error) {
      console.error('Error creating group goal:', error);
      return { success: false, error: 'Failed to create goal' };
    }
  }

  /**
   * Get messages from group chat
   */
  async getGroupMessages(
    groupId: string,
    options?: { limit?: number; beforeId?: string }
  ): Promise<ApiResponse<StudyGroupMessage[]>> {
    try {
      const response = await apiService.post('/walker/study_group_messages', {
        group_id: groupId,
        limit: options?.limit || 50,
        before_id: options?.beforeId || ''
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching group messages:', error);
      return { success: false, error: 'Failed to fetch messages' };
    }
  }

  /**
   * Send a message to group chat
   */
  async sendGroupMessage(
    groupId: string,
    content: string,
    options?: {
      messageType?: 'text' | 'link' | 'file' | 'milestone';
      fileUrl?: string;
    }
  ): Promise<ApiResponse<{ message: StudyGroupMessage }>> {
    try {
      const response = await apiService.post('/walker/study_group_message_send', {
        group_id: groupId,
        content,
        message_type: options?.messageType || 'text',
        file_url: options?.fileUrl || ''
      });
      return response.data;
    } catch (error) {
      console.error('Error sending group message:', error);
      return { success: false, error: 'Failed to send message' };
    }
  }

  /**
   * Get members of a study group
   */
  async getGroupMembers(groupId: string): Promise<ApiResponse<StudyGroupMember[]>> {
    try {
      const response = await apiService.post('/walker/study_group_members', { group_id: groupId });
      return response.data;
    } catch (error) {
      console.error('Error fetching group members:', error);
      return { success: false, error: 'Failed to fetch members', data: [] };
    }
  }

  /**
   * Remove a member from a study group
   */
  async removeGroupMember(
    groupId: string,
    userId: string
  ): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await apiService.post('/walker/study_group_member_remove', {
        group_id: groupId,
        user_id: userId
      });
      return response.data;
    } catch (error) {
      console.error('Error removing group member:', error);
      return { success: false, error: 'Failed to remove member' };
    }
  }

  /**
   * Update a member's role in a study group
   */
  async updateGroupMemberRole(
    groupId: string,
    userId: string,
    role: 'admin' | 'member'
  ): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await apiService.post('/walker/study_group_member_role', {
        group_id: groupId,
        user_id: userId,
        role
      });
      return response.data;
    } catch (error) {
      console.error('Error updating member role:', error);
      return { success: false, error: 'Failed to update role' };
    }
  }

  /**
   * Leave a study group
   */
  async leaveGroup(groupId: string): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await apiService.post('/walker/study_group_leave', { group_id: groupId });
      return response.data;
    } catch (error) {
      console.error('Error leaving study group:', error);
      return { success: false, error: 'Failed to leave group' };
    }
  }

  /**
   * Invite a user to a study group via email
   */
  async inviteToGroup(
    groupId: string,
    email: string,
    message?: string
  ): Promise<ApiResponse<{ invite_id: string; invite_link?: string }>> {
    try {
      const response = await apiService.post('/walker/study_group_invite', {
        group_id: groupId,
        email,
        message: message || ''
      });
      return response.data;
    } catch (error) {
      console.error('Error inviting to group:', error);
      return { success: false, error: 'Failed to send invitation' };
    }
  }

  /**
   * Create an invite link for a study group
   */
  async createGroupInviteLink(groupId: string): Promise<ApiResponse<{ invite_link: string }>> {
    try {
      const response = await apiService.post('/walker/study_group_invite_link', { group_id: groupId });
      return response.data;
    } catch (error) {
      console.error('Error creating invite link:', error);
      return { success: false, error: 'Failed to create invite link' };
    }
  }

  /**
   * Get events for a study group
   */
  async getStudyGroupEvents(groupId: string): Promise<ApiResponse<GroupEvent[]>> {
    try {
      const response = await apiService.post('/walker/study_group_events', { group_id: groupId });
      return response.data;
    } catch (error) {
      console.error('Error fetching group events:', error);
      return { success: false, error: 'Failed to fetch events', data: [] };
    }
  }

  /**
   * Create an event in a study group
   */
  async createStudyGroupEvent(
    groupId: string,
    title: string,
    options?: {
      description?: string;
      eventTime?: string;
      durationMinutes?: number;
    }
  ): Promise<ApiResponse<{ event: GroupEvent }>> {
    try {
      const response = await apiService.post('/walker/study_group_event_create', {
        group_id: groupId,
        title,
        description: options?.description || '',
        event_time: options?.eventTime || '',
        duration_minutes: options?.durationMinutes || 60
      });
      return response.data;
    } catch (error) {
      console.error('Error creating group event:', error);
      return { success: false, error: 'Failed to create event' };
    }
  }

  /**
   * Join a study group event
   */
  async joinStudyGroupEvent(
    groupId: string,
    eventId: string
  ): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await apiService.post('/walker/study_group_event_join', {
        group_id: groupId,
        event_id: eventId
      });
      return response.data;
    } catch (error) {
      console.error('Error joining group event:', error);
      return { success: false, error: 'Failed to join event' };
    }
  }

  /**
   * Leave a study group event
   */
  async leaveStudyGroupEvent(
    groupId: string,
    eventId: string
  ): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await apiService.post('/walker/study_group_event_leave', {
        group_id: groupId,
        event_id: eventId
      });
      return response.data;
    } catch (error) {
      console.error('Error leaving group event:', error);
      return { success: false, error: 'Failed to leave event' };
    }
  }

  // =============================================================================
  // MENTORSHIP API CALLS
  // =============================================================================

  /**
   * Create or update mentor profile
   */
  async createMentorProfile(
    expertiseAreas: string[],
    options?: {
      bio?: string;
      yearsExperience?: number;
      teachingStyle?: string;
      availabilityHours?: string;
      maxMentees?: number;
    }
  ): Promise<ApiResponse<{ profile: MentorshipProfile }>> {
    try {
      const response = await apiService.post('/walker/mentor_profile_create', {
        expertise_areas: expertiseAreas,
        bio: options?.bio || '',
        years_experience: options?.yearsExperience || 0,
        teaching_style: options?.teachingStyle || '',
        availability_hours: options?.availabilityHours || '',
        max_mentees: options?.maxMentees || 3
      });
      return response.data;
    } catch (error) {
      console.error('Error creating mentor profile:', error);
      return { success: false, error: 'Failed to create mentor profile' };
    }
  }

  /**
   * Search for available mentors
   */
  async searchMentors(
    searchQuery?: string,
    expertiseArea?: string
  ): Promise<ApiResponse<MentorshipProfile[]>> {
    try {
      const response = await apiService.post('/walker/mentors_search', {
        search_query: searchQuery || '',
        expertise_area: expertiseArea || ''
      });
      return response.data;
    } catch (error) {
      console.error('Error searching mentors:', error);
      return { success: false, error: 'Failed to search mentors', data: [] };
    }
  }

  /**
   * Request mentorship from a mentor
   */
  async requestMentorship(
    mentorId: number,
    topic: string,
    options?: {
      goals?: string;
      preferredSchedule?: string;
      message?: string;
    }
  ): Promise<ApiResponse<{ request: MentorshipRequest }>> {
    try {
      const response = await apiService.post('/walker/mentorship_request', {
        mentor_id: mentorId,
        topic,
        goals: options?.goals || '',
        preferred_schedule: options?.preferredSchedule || '',
        message: options?.message || ''
      });
      return response.data;
    } catch (error) {
      console.error('Error requesting mentorship:', error);
      return { success: false, error: 'Failed to request mentorship' };
    }
  }

  /**
   * Respond to a mentorship request
   */
  async respondToMentorshipRequest(
    requestId: string,
    status: 'accepted' | 'rejected',
    responseMessage?: string
  ): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await apiService.post('/walker/mentorship_request_respond', {
        request_id: requestId,
        status,
        response_message: responseMessage || ''
      });
      return response.data;
    } catch (error) {
      console.error('Error responding to mentorship request:', error);
      return { success: false, error: 'Failed to respond to request' };
    }
  }

  /**
   * Schedule a mentorship session
   */
  async scheduleMentorshipSession(
    mentorshipId: number,
    scheduledAt: string,
    options?: {
      durationMinutes?: number;
      topic?: string;
    }
  ): Promise<ApiResponse<{ session: MentorshipSession }>> {
    try {
      const response = await apiService.post('/walker/mentorship_session_schedule', {
        mentorship_id: mentorshipId,
        scheduled_at: scheduledAt,
        duration_minutes: options?.durationMinutes || 60,
        topic: options?.topic || ''
      });
      return response.data;
    } catch (error) {
      console.error('Error scheduling mentorship session:', error);
      return { success: false, error: 'Failed to schedule session' };
    }
  }

  /**
   * Complete a mentorship session
   */
  async completeMentorshipSession(
    sessionId: string,
    options?: {
      mentorFeedback?: string;
      menteeFeedback?: string;
      mentorRating?: number;
      menteeRating?: number;
      outcome?: string;
    }
  ): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await apiService.post('/walker/mentorship_session_complete', {
        session_id: sessionId,
        mentor_feedback: options?.mentorFeedback || '',
        mentee_feedback: options?.menteeFeedback || '',
        mentor_rating: options?.mentorRating || 0,
        mentee_rating: options?.menteeRating || 0,
        outcome: options?.outcome || ''
      });
      return response.data;
    } catch (error) {
      console.error('Error completing mentorship session:', error);
      return { success: false, error: 'Failed to complete session' };
    }
  }

  /**
   * Get all mentorship requests (for both mentors and mentees)
   */
  async getMentorshipRequests(): Promise<ApiResponse<MentorshipRequest[]>> {
    try {
      const response = await apiService.post('/walker/mentorship_requests_list', {});
      return response.data;
    } catch (error) {
      console.error('Error getting mentorship requests:', error);
      return { success: false, error: 'Failed to get requests', data: [] };
    }
  }

  /**
   * Cancel a mentorship request
   */
  async cancelMentorshipRequest(requestId: string): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await apiService.post('/walker/mentorship_request_cancel', {
        request_id: requestId
      });
      return response.data;
    } catch (error) {
      console.error('Error cancelling mentorship request:', error);
      return { success: false, error: 'Failed to cancel request' };
    }
  }

  // =============================================================================
  // MODERATION API CALLS
  // =============================================================================

  /**
   * Report content for moderation
   */
  async reportContent(
    contentId: string,
    contentType: string,
    reportReason: string,
    options?: {
      additionalInfo?: string;
      priority?: 'low' | 'normal' | 'high' | 'urgent';
    }
  ): Promise<ApiResponse<{ report: ContentReport }>> {
    try {
      const response = await apiService.post('/walker/content_report', {
        content_id: contentId,
        content_type: contentType,
        report_reason: reportReason,
        additional_info: options?.additionalInfo || '',
        priority: options?.priority || 'normal'
      });
      return response.data;
    } catch (error) {
      console.error('Error reporting content:', error);
      return { success: false, error: 'Failed to report content' };
    }
  }

  /**
   * Get moderation queue
   */
  async getModerationQueue(
    options?: {
      status?: 'pending' | 'in_review' | 'resolved';
      priority?: string;
      limit?: number;
      offset?: number;
    }
  ): Promise<ApiResponse<ModerationQueueItem[]>> {
    try {
      const response = await apiService.post('/walker/moderation_queue', {
        status: options?.status || 'pending',
        priority: options?.priority || '',
        limit: options?.limit || 20,
        offset: options?.offset || 0
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching moderation queue:', error);
      return { success: false, error: 'Failed to fetch moderation queue' };
    }
  }

  /**
   * Get all moderation reports
   */
  async getModerationReports(): Promise<ApiResponse<ModerationReport[]>> {
    try {
      const response = await apiService.post('/walker/moderation_reports_list', {});
      return response.data;
    } catch (error) {
      console.error('Error fetching moderation reports:', error);
      return { success: false, error: 'Failed to fetch reports', data: [] };
    }
  }

  /**
   * Get moderation actions history
   */
  async getModerationActions(): Promise<ApiResponse<ModerationAction[]>> {
    try {
      const response = await apiService.post('/walker/moderation_actions_list', {});
      return response.data;
    } catch (error) {
      console.error('Error fetching moderation actions:', error);
      return { success: false, error: 'Failed to fetch actions', data: [] };
    }
  }

  /**
   * Take moderation action on a report
   */
  async takeModerationAction(
    reportId: number,
    action: {
      actionType: string;
      reason: string;
      duration?: number;
    }
  ): Promise<ApiResponse<{ action_id: number }>> {
    try {
      const response = await apiService.post('/walker/moderation_action', {
        report_id: reportId,
        action_type: action.actionType,
        reason: action.reason,
        duration: action.duration || null
      });
      return response.data;
    } catch (error) {
      console.error('Error taking moderation action:', error);
      return { success: false, error: 'Failed to take moderation action' };
    }
  }

  /**
   * Dismiss a moderation report
   */
  async dismissReport(reportId: number): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await apiService.post('/walker/moderation_report_dismiss', {
        report_id: reportId
      });
      return response.data;
    } catch (error) {
      console.error('Error dismissing report:', error);
      return { success: false, error: 'Failed to dismiss report' };
    }
  }

  /**
   * Get moderation stats
   */
  async getModerationStats(): Promise<ApiResponse<ModerationStats>> {
    try {
      const response = await apiService.post('/walker/moderation_stats', {});
      return response.data;
    } catch (error) {
      console.error('Error fetching moderation stats:', error);
      return { success: false, error: 'Failed to fetch moderation stats' };
    }
  }

  // =============================================================================
  // PEER REVIEW API CALLS
  // =============================================================================

  /**
   * Submit work for peer review
   */
  async submitForPeerReview(
    title: string,
    description: string,
    contentType: string,
    options?: {
      relatedContentId?: string;
      relatedContentType?: string;
      maxReviewers?: number;
    }
  ): Promise<ApiResponse<{ submission: PeerReviewSubmission }>> {
    try {
      const response = await apiService.post('/walker/peer_review_submit', {
        title,
        description,
        content_type: contentType,
        related_content_id: options?.relatedContentId || '',
        related_content_type: options?.relatedContentType || '',
        max_reviewers: options?.maxReviewers || 2
      });
      return response.data;
    } catch (error) {
      console.error('Error submitting for peer review:', error);
      return { success: false, error: 'Failed to submit for review' };
    }
  }

  /**
   * Assign a reviewer to a submission
   */
  async assignPeerReviewer(
    submissionId: string,
    reviewerId: number,
    options?: { deadline?: string }
  ): Promise<ApiResponse<{ assignment_id: string }>> {
    try {
      const response = await apiService.post('/walker/peer_review_assign', {
        submission_id: submissionId,
        reviewer_id: reviewerId,
        deadline: options?.deadline || ''
      });
      return response.data;
    } catch (error) {
      console.error('Error assigning peer reviewer:', error);
      return { success: false, error: 'Failed to assign reviewer' };
    }
  }

  /**
   * Submit peer review feedback
   */
  async submitPeerReviewFeedback(
    assignmentId: string,
    overallRating: number,
    strengths: string,
    improvements: string,
    comments: string
  ): Promise<ApiResponse<{ feedback_id: string }>> {
    try {
      const response = await apiService.post('/walker/peer_review_feedback', {
        assignment_id: assignmentId,
        overall_rating: overallRating,
        strengths,
        improvements,
        comments
      });
      return response.data;
    } catch (error) {
      console.error('Error submitting peer review feedback:', error);
      return { success: false, error: 'Failed to submit feedback' };
    }
  }

  /**
   * Get user's peer review submissions
   */
  async getMySubmissions(
    options?: { status?: string }
  ): Promise<ApiResponse<PeerReviewSubmission[]>> {
    try {
      const response = await apiService.post('/walker/peer_review_submissions', {
        status: options?.status || ''
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching submissions:', error);
      return { success: false, error: 'Failed to fetch submissions' };
    }
  }

  /**
   * Get user's review assignments
   */
  async getMyReviewAssignments(
    options?: { status?: string }
  ): Promise<ApiResponse<PeerReviewAssignment[]>> {
    try {
      const response = await apiService.post('/walker/peer_review_my_assignments', {
        status: options?.status || ''
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching review assignments:', error);
      return { success: false, error: 'Failed to fetch assignments' };
    }
  }

  /**
   * Get feedback for a submission
   */
  async getSubmissionFeedback(
    submissionId: string
  ): Promise<ApiResponse<PeerReviewFeedback[]>> {
    try {
      const response = await apiService.post('/walker/peer_review_get_feedback', {
        submission_id: submissionId
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching submission feedback:', error);
      return { success: false, error: 'Failed to fetch feedback', data: [] };
    }
  }

  // =============================================================================
  // ADMIN API CALLS
  // =============================================================================

  /**
   * Get user activity statistics
   */
  async getUserActivityStats(): Promise<ApiResponse<UserActivityStats>> {
    try {
      const response = await apiService.post('/walker/admin_user_activity_stats', {});
      return response.data;
    } catch (error) {
      console.error('Error fetching user activity stats:', error);
      return { 
        success: true, 
        data: {
          totalUsers: 0,
          activeUsers: 0,
          newUsersToday: 0,
          newUsersThisWeek: 0,
          avgSessionDuration: 0,
          topActiveUsers: [],
          usersByRole: [],
          activityByHour: []
        }
      };
    }
  }

  /**
   * Get user activity log
   */
  async getUserActivityLog(
    options?: { limit?: number; dateRange?: string }
  ): Promise<ApiResponse<UserActivityLog[]>> {
    try {
      const response = await apiService.post('/walker/admin_user_activity_log', {
        limit: options?.limit || 100,
        date_range: options?.dateRange || 'week'
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching user activity log:', error);
      return { success: false, error: 'Failed to fetch activity log', data: [] };
    }
  }

  /**
   * Get database statistics
   */
  async getDatabaseStats(): Promise<ApiResponse<DatabaseStats>> {
    try {
      const response = await apiService.post('/walker/admin_database_stats', {});
      return response.data;
    } catch (error) {
      console.error('Error fetching database stats:', error);
      return {
        success: true,
        data: {
          totalSize: '0 MB',
          totalTables: 0,
          totalRows: 0,
          activeConnections: 0,
          avgQueryTime: 0,
          uptime: '0h'
        }
      };
    }
  }

  /**
   * Get table information
   */
  async getTableInfo(): Promise<ApiResponse<TableInfo[]>> {
    try {
      const response = await apiService.post('/walker/admin_table_info', {});
      return response.data;
    } catch (error) {
      console.error('Error fetching table info:', error);
      return { success: false, error: 'Failed to fetch table info', data: [] };
    }
  }

  /**
   * Get table activity metrics
   */
  async getTableActivity(): Promise<ApiResponse<TableActivity[]>> {
    try {
      const response = await apiService.post('/walker/admin_table_activity', {});
      return response.data;
    } catch (error) {
      console.error('Error fetching table activity:', error);
      return { success: false, error: 'Failed to fetch table activity', data: [] };
    }
  }

  /**
   * Get cache statistics
   */
  async getCacheStats(): Promise<ApiResponse<CacheStats>> {
    try {
      const response = await apiService.post('/walker/admin_cache_stats', {});
      return response.data;
    } catch (error) {
      console.error('Error fetching cache stats:', error);
      return {
        success: true,
        data: {
          totalSize: '0 MB',
          entryCount: 0,
          hitRate: 0,
          missRate: 0,
          lastCleared: new Date().toISOString(),
          memoryUsage: '0 MB'
        }
      };
    }
  }

  /**
   * Get cache entries
   */
  async getCacheEntries(
    options?: { limit?: number; region?: string }
  ): Promise<ApiResponse<CacheEntry[]>> {
    try {
      const response = await apiService.post('/walker/admin_cache_entries', {
        limit: options?.limit || 100,
        region: options?.region || ''
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching cache entries:', error);
      return { success: false, error: 'Failed to fetch cache entries', data: [] };
    }
  }

  /**
   * Get cache regions
   */
  async getCacheRegions(): Promise<ApiResponse<CacheRegion[]>> {
    try {
      const response = await apiService.post('/walker/admin_cache_regions', {});
      return response.data;
    } catch (error) {
      console.error('Error fetching cache regions:', error);
      return { success: false, error: 'Failed to fetch cache regions', data: [] };
    }
  }

  /**
   * Clear content cache
   */
  async clearContentCache(region?: string): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await apiService.post('/walker/admin_clear_content_cache', {
        region: region || ''
      });
      return response.data;
    } catch (error) {
      console.error('Error clearing cache:', error);
      return { success: false, error: 'Failed to clear cache' };
    }
  }

  // =============================================================================
  // COMPATIBILITY ALIASES - Methods called by components
  // =============================================================================

  /**
   * Get reputation leaderboard (alias for compatibility)
   */
  async getLeaderboard(
    limit?: number,
    timeRange?: 'week' | 'month' | 'all'
  ): Promise<ApiResponse<UserReputation[]>> {
    return this.getReputationLeaderboard(limit || 20);
  }

  /**
   * Vote on content (alias for compatibility)
   */
  async voteContent(
    contentId: string,
    contentType: string,
    vote: number
  ): Promise<ApiResponse<{ action: string; vote_change: number }>> {
    return this.upvoteContent(contentId, contentType, vote as 1 | -1);
  }

  /**
   * Accept mentorship request (alias for compatibility)
   */
  async acceptMentorshipRequest(
    requestId: string
  ): Promise<ApiResponse<{ message: string }>> {
    return this.respondToMentorshipRequest(requestId, 'accepted');
  }

  /**
   * Decline mentorship request (alias for compatibility)
   */
  async declineMentorshipRequest(
    requestId: string
  ): Promise<ApiResponse<{ message: string }>> {
    return this.respondToMentorshipRequest(requestId, 'rejected');
  }

  /**
   * Complete a group goal (alias for compatibility)
   */
  async completeGroupGoal(groupId: string, goalId: string): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await apiService.post('/walker/study_group_goal_complete', {
        group_id: groupId,
        goal_id: goalId
      });
      return response.data;
    } catch (error) {
      console.error('Error completing group goal:', error);
      return { success: false, error: 'Failed to complete goal' };
    }
  }

  /**
   * Get peer review submissions (alias for compatibility)
   */
  async getPeerReviewSubmissions(): Promise<ApiResponse<PeerReviewSubmission[]>> {
    return this.getMySubmissions({});
  }

  /**
   * Get peer review assignments (alias for compatibility)
   */
  async getPeerReviewAssignments(): Promise<ApiResponse<PeerReviewAssignment[]>> {
    return this.getMyReviewAssignments({});
  }

  /**
   * Get peer review feedback (alias for compatibility)
   */
  async getPeerReviewFeedback(): Promise<ApiResponse<PeerReviewFeedback[]>> {
    try {
      const response = await apiService.post('/walker/peer_review_my_feedback', {});
      return response.data;
    } catch (error) {
      console.error('Error fetching feedback:', error);
      return { success: false, error: 'Failed to fetch feedback', data: [] };
    }
  }

  /**
   * Get review statistics (alias for compatibility)
   */
  async getReviewStats(): Promise<ApiResponse<{
    totalSubmissions: number;
    pendingReviews: number;
    averageRating: number;
    reviewsGiven: number;
    reviewsReceived: number;
    topReviewers: Array<{ username: string; reviewsCount: number; averageRating: number }>;
  }>> {
    try {
      const response = await apiService.post('/walker/peer_review_stats', {});
      return response.data;
    } catch (error) {
      console.error('Error fetching review stats:', error);
      return {
        success: true,
        data: {
          totalSubmissions: 0,
          pendingReviews: 0,
          averageRating: 0,
          reviewsGiven: 0,
          reviewsReceived: 0,
          topReviewers: []
        }
      };
    }
  }

  /**
   * Accept peer review assignment (alias for compatibility)
   */
  async acceptPeerReviewAssignment(assignmentId: string): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await apiService.post('/walker/peer_review_assignment_accept', {
        assignment_id: assignmentId
      });
      return response.data;
    } catch (error) {
      console.error('Error accepting assignment:', error);
      return { success: false, error: 'Failed to accept assignment' };
    }
  }

  /**
   * Complete peer review assignment (alias for compatibility)
   */
  async completePeerReviewAssignment(assignmentId: string): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await apiService.post('/walker/peer_review_assignment_complete', {
        assignment_id: assignmentId
      });
      return response.data;
    } catch (error) {
      console.error('Error completing assignment:', error);
      return { success: false, error: 'Failed to complete assignment' };
    }
  }

  /**
   * Create peer review submission (alias for compatibility)
   */
  async createPeerReviewSubmission(
    submission: {
      title: string;
      description: string;
      contentType: string;
      content?: string;
    }
  ): Promise<ApiResponse<{ submission: PeerReviewSubmission }>> {
    try {
      const response = await apiService.post('/walker/peer_review_submit', {
        title: submission.title,
        description: submission.description,
        content_type: submission.contentType,
        content: submission.content || ''
      });
      return response.data;
    } catch (error) {
      console.error('Error creating peer review submission:', error);
      return { success: false, error: 'Failed to create submission' };
    }
  }

  // Audit History Methods
  async getAuditHistoryStats(): Promise<ApiResponse<{
    totalActions: number;
    actionsByType: Record<string, number>;
    actionsByUser: Array<{ user_id: number; username: string; action_count: number }>;
    dailyActivity: Array<{ date: string; count: number }>;
  }>> {
    try {
      const response = await apiService.post('/walker/admin_audit_history_stats', {});
      return response.data;
    } catch (error) {
      console.error('Error fetching audit history stats:', error);
      return { 
        success: true, 
        data: {
          totalActions: 0,
          actionsByType: {},
          actionsByUser: [],
          dailyActivity: []
        }
      };
    }
  }

  async getAuditHistory(params: {
    page?: number;
    limit?: number;
    userId?: number;
    actionType?: string;
    startDate?: string;
    endDate?: string;
  } = {}): Promise<ApiResponse<Array<{
    id: string;
    user_id: number;
    username: string;
    action: string;
    resource_type: string;
    resource_id: string;
    details: Record<string, unknown>;
    ip_address: string;
    user_agent: string;
    created_at: string;
  }>>> {
    try {
      const response = await apiService.post('/walker/admin_audit_history', {
        target_id: params.userId?.toString() || '',
        target_type: params.actionType || '',
        limit: params.limit || 50
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching audit history:', error);
      return { success: false, error: 'Failed to fetch audit history', data: [] };
    }
  }

  async exportAuditHistoryToCsv(params: {
    actionType?: string;
    performedBy?: string;
    startDate?: string;
    endDate?: string;
    limit?: number;
  } = {}): Promise<ApiResponse<{ format: string; data: string }>> {
    try {
      const response = await apiService.post('/walker/admin_audit_history_export_csv', {
        action_type: params.actionType || '',
        performed_by: params.performedBy || '',
        date_from: params.startDate || '',
        date_to: params.endDate || '',
        limit: params.limit || 1000
      });
      return response.data;
    } catch (error) {
      console.error('Error exporting audit history to CSV:', error);
      return { success: false, error: 'Failed to export audit history to CSV' };
    }
  }

  async exportAuditHistoryToJson(params: {
    actionType?: string;
    performedBy?: string;
    startDate?: string;
    endDate?: string;
    limit?: number;
  } = {}): Promise<ApiResponse<{ format: string; data: string }>> {
    try {
      const response = await apiService.post('/walker/admin_audit_history_export_json', {
        action_type: params.actionType || '',
        performed_by: params.performedBy || '',
        date_from: params.startDate || '',
        date_to: params.endDate || '',
        limit: params.limit || 1000
      });
      return response.data;
    } catch (error) {
      console.error('Error exporting audit history to JSON:', error);
      return { success: false, error: 'Failed to export audit history to JSON' };
    }
  }

  async getAuditLogStats(): Promise<ApiResponse<{
    totalLogs: number;
    logsByLevel: Record<string, number>;
    logsBySource: Record<string, number>;
    recentErrors: Array<{ timestamp: string; level: string; message: string }>;
  }>> {
    try {
      const response = await apiService.post('/walker/admin_audit_log_stats', {});
      return response.data;
    } catch (error) {
      console.error('Error fetching audit log stats:', error);
      return {
        success: true,
        data: {
          totalLogs: 0,
          logsByLevel: {},
          logsBySource: {},
          recentErrors: []
        }
      };
    }
  }

  async getAuditLogs(params: {
    page?: number;
    limit?: number;
    level?: string;
    source?: string;
    startDate?: string;
    endDate?: string;
  } = {}): Promise<ApiResponse<Array<{
    id: string;
    timestamp: string;
    level: string;
    source: string;
    message: string;
    context: Record<string, unknown>;
  }>>> {
    try {
      const response = await apiService.post('/walker/admin_audit_logs', {
        action_type: params.level || '',
        date_from: params.startDate || '',
        date_to: params.endDate || '',
        limit: params.limit || 100,
        offset: ((params.page || 1) - 1) * (params.limit || 100)
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching audit logs:', error);
      return { success: false, error: 'Failed to fetch audit logs', data: [] };
    }
  }

  /**
   * Get recent admin activity for dashboard display
   * Fetches the most recent activities with real timestamps and security events
   */
  async getRecentAdminActivity(limit: number = 5): Promise<ApiResponse<Array<{
    id: string;
    timestamp: string;
    action: string;
    category: string;
    description: string;
    ipAddress?: string;
    username?: string;
  }>>> {
    try {
      const response = await apiService.get('/admin/recent_activity', {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching recent admin activity:', error);
      // Fallback: try to get from audit logs
      try {
        const auditResponse = await this.getAuditLogs({ limit, level: 'info' });
        if (auditResponse.success && auditResponse.data) {
          const activities = auditResponse.data.map(log => ({
            id: log.id,
            timestamp: log.timestamp,
            action: log.level.toUpperCase(),
            category: log.source || 'System',
            description: log.message,
            ipAddress: log.context?.ip_address as string | undefined,
            username: log.context?.username as string | undefined
          }));
          return { success: true, data: activities };
        }
      } catch (fallbackError) {
        console.error('Error fetching fallback audit logs:', fallbackError);
      }
      return { success: false, error: 'Failed to fetch recent activity', data: [] };
    }
  }
}

// Export singleton instance
const advancedCollaborationService = new AdvancedCollaborationService();
export default advancedCollaborationService;
