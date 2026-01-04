import React, { useState, useEffect, useCallback } from 'react';
import {
  Users,
  User,
  Crown,
  Shield,
  MessageSquare,
  Mail,
  MoreVertical,
  Search,
  Filter,
  X,
  CheckCircle,
  AlertCircle,
  LoadingSpinner
} from 'lucide-react';
import advancedCollaborationService, {
  StudyGroupMember
} from '../../services/advancedCollaborationService';

interface StudyGroupMembersProps {
  groupId: string;
  groupName: string;
  isOwner?: boolean;
  isAdmin?: boolean;
  onClose?: () => void;
}

interface MemberWithProfile extends StudyGroupMember {
  username?: string;
  first_name?: string;
  last_name?: string;
  avatar_url?: string;
  last_active_at?: string;
}

const StudyGroupMembers: React.FC<StudyGroupMembersProps> = ({
  groupId,
  groupName,
  isOwner = false,
  isAdmin = false,
  onClose
}) => {
  const [members, setMembers] = useState<MemberWithProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterRole, setFilterRole] = useState<string>('all');
  const [selectedMember, setSelectedMember] = useState<MemberWithProfile | null>(null);
  const [showMemberModal, setShowMemberModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchMembers = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await advancedCollaborationService.getGroupMembers(groupId);

      if (response.success && response.data) {
        setMembers(response.data as MemberWithProfile[]);
      } else {
        setError(response.error || 'Failed to load members');
      }
    } catch (err) {
      setError('An error occurred while loading members');
      console.error('Error fetching group members:', err);
    } finally {
      setLoading(false);
    }
  }, [groupId]);

  useEffect(() => {
    fetchMembers();
  }, [fetchMembers]);

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'owner':
        return <Crown size={14} className="text-yellow-500" />;
      case 'admin':
        return <Shield size={14} className="text-blue-500" />;
      default:
        return <User size={14} className="text-gray-500" />;
    }
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'owner':
        return 'bg-yellow-100 text-yellow-800';
      case 'admin':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleRemoveMember = async (member: MemberWithProfile) => {
    if (!confirm(`Are you sure you want to remove ${member.username || 'this member'} from the group?`)) {
      return;
    }

    try {
      setActionLoading(true);
      setError(null);

      const response = await advancedCollaborationService.removeGroupMember(
        groupId,
        member.user_id.toString()
      );

      if (response.success) {
        setSuccessMessage('Member removed successfully');
        fetchMembers();
        setShowMemberModal(false);
      } else {
        setError(response.error || 'Failed to remove member');
      }
    } catch (err) {
      setError('An error occurred while removing member');
      console.error('Error removing member:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handlePromoteToAdmin = async (member: MemberWithProfile) => {
    try {
      setActionLoading(true);
      setError(null);

      const response = await advancedCollaborationService.updateGroupMemberRole(
        groupId,
        member.user_id.toString(),
        'admin'
      );

      if (response.success) {
        setSuccessMessage('Member promoted to admin');
        fetchMembers();
      } else {
        setError(response.error || 'Failed to promote member');
      }
    } catch (err) {
      setError('An error occurred while promoting member');
      console.error('Error promoting member:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDemoteFromAdmin = async (member: MemberWithProfile) => {
    try {
      setActionLoading(true);
      setError(null);

      const response = await advancedCollaborationService.updateGroupMemberRole(
        groupId,
        member.user_id.toString(),
        'member'
      );

      if (response.success) {
        setSuccessMessage('Admin demoted to member');
        fetchMembers();
      } else {
        setError(response.error || 'Failed to demote member');
      }
    } catch (err) {
      setError('An error occurred while demoting member');
      console.error('Error demoting member:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const filteredMembers = members.filter(member => {
    const matchesSearch = !searchQuery ||
      member.username?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      member.first_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      member.last_name?.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesRole = filterRole === 'all' || member.role === filterRole;

    return matchesSearch && matchesRole;
  });

  const roleCounts = {
    owner: members.filter(m => m.role === 'owner').length,
    admin: members.filter(m => m.role === 'admin').length,
    member: members.filter(m => m.role === 'member').length
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <LoadingSpinner size={40} className="animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[80vh] overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Users className="text-blue-500" size={24} />
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Members</h2>
            <p className="text-sm text-gray-500">{groupName}</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X size={20} className="text-gray-500" />
        </button>
      </div>

      {/* Success/Error Messages */}
      {successMessage && (
        <div className="mx-6 mt-4 p-3 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2">
          <CheckCircle size={18} className="text-green-500" />
          <span className="text-green-700 text-sm">{successMessage}</span>
          <button
            onClick={() => setSuccessMessage(null)}
            className="ml-auto text-green-500 hover:text-green-700"
          >
            <X size={14} />
          </button>
        </div>
      )}

      {error && (
        <div className="mx-6 mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
          <AlertCircle size={18} className="text-red-500" />
          <span className="text-red-700 text-sm">{error}</span>
          <button
            onClick={() => setError(null)}
            className="ml-auto text-red-500 hover:text-red-700"
          >
            <X size={14} />
          </button>
        </div>
      )}

      {/* Filters */}
      <div className="px-6 py-4 border-b border-gray-100">
        <div className="flex flex-wrap gap-3">
          <div className="flex-1 min-w-[200px] relative">
            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search members..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter size={18} className="text-gray-400" />
            <select
              value={filterRole}
              onChange={(e) => setFilterRole(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Roles</option>
              <option value="owner">Owners ({roleCounts.owner})</option>
              <option value="admin">Admins ({roleCounts.admin})</option>
              <option value="member">Members ({roleCounts.member})</option>
            </select>
          </div>
        </div>
      </div>

      {/* Members List */}
      <div className="overflow-y-auto max-h-[400px] p-4">
        {filteredMembers.length === 0 ? (
          <div className="text-center py-8">
            <Users size={48} className="mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500">No members found</p>
          </div>
        ) : (
          <div className="space-y-2">
            {filteredMembers.map((member) => (
              <div
                key={member.membership_id}
                className="flex items-center gap-4 p-3 hover:bg-gray-50 rounded-lg transition-colors cursor-pointer"
                onClick={() => {
                  setSelectedMember(member);
                  setShowMemberModal(true);
                }}
              >
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  {member.avatar_url ? (
                    <img
                      src={member.avatar_url}
                      alt={member.username}
                      className="w-full h-full rounded-full object-cover"
                    />
                  ) : (
                    <User className="text-blue-500" size={20} />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900 truncate">
                      {member.first_name && member.last_name
                        ? `${member.first_name} ${member.last_name}`
                        : member.username || 'Unknown User'}
                    </span>
                    {getRoleIcon(member.role)}
                  </div>
                  <p className="text-sm text-gray-500">@{member.username}</p>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleBadgeColor(member.role)}`}>
                  {member.role}
                </span>
                <MoreVertical size={18} className="text-gray-400" />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Member Detail Modal */}
      {showMemberModal && selectedMember && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                    {selectedMember.avatar_url ? (
                      <img
                        src={selectedMember.avatar_url}
                        alt={selectedMember.username}
                        className="w-full h-full rounded-full object-cover"
                      />
                    ) : (
                      <User className="text-blue-500" size={32} />
                    )}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {selectedMember.first_name && selectedMember.last_name
                        ? `${selectedMember.first_name} ${selectedMember.last_name}`
                        : selectedMember.username || 'Unknown User'}
                    </h3>
                    <p className="text-gray-500">@{selectedMember.username}</p>
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium mt-2 ${getRoleBadgeColor(selectedMember.role)}`}>
                      {getRoleIcon(selectedMember.role)}
                      {selectedMember.role}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setShowMemberModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X size={20} className="text-gray-500" />
                </button>
              </div>

              <div className="space-y-3 text-sm">
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-500">Joined</span>
                  <span className="text-gray-900">
                    {new Date(selectedMember.joined_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-500">Last Active</span>
                  <span className="text-gray-900">
                    {selectedMember.last_active_at
                      ? new Date(selectedMember.last_active_at).toLocaleDateString()
                      : 'Unknown'}
                  </span>
                </div>
              </div>

              {/* Admin Actions */}
              {(isOwner || isAdmin) && (
                <div className="mt-6 pt-4 border-t border-gray-200 space-y-2">
                  <button
                    onClick={() => {
                      // Open chat with member
                    }}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                  >
                    <MessageSquare size={18} />
                    Send Message
                  </button>
                  <button
                    onClick={() => {
                      // Send invite/email
                    }}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <Mail size={18} />
                    Send Invite
                  </button>
                  {(isOwner || isAdmin) && selectedMember.role !== 'owner' && (
                    <>
                      {selectedMember.role === 'member' ? (
                        <button
                          onClick={() => {
                            handlePromoteToAdmin(selectedMember);
                            setShowMemberModal(false);
                          }}
                          disabled={actionLoading}
                          className="w-full flex items-center justify-center gap-2 px-4 py-2 border border-blue-300 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                        >
                          <Shield size={18} />
                          Promote to Admin
                        </button>
                      ) : selectedMember.role === 'admin' && isOwner ? (
                        <button
                          onClick={() => {
                            handleDemoteFromAdmin(selectedMember);
                            setShowMemberModal(false);
                          }}
                          disabled={actionLoading}
                          className="w-full flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 text-gray-600 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                          <Users size={18} />
                          Demote to Member
                        </button>
                      ) : null}
                      <button
                        onClick={() => {
                          handleRemoveMember(selectedMember);
                          setShowMemberModal(false);
                        }}
                        disabled={actionLoading}
                        className="w-full flex items-center justify-center gap-2 px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                      >
                        <X size={18} />
                        Remove from Group
                      </button>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudyGroupMembers;
