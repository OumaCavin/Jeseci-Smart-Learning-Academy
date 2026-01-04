import React, { useState, useEffect } from 'react';
import ApiService from '../services/api';

interface User {
  id: string;
  username: string;
  displayName: string;
  avatar?: string;
  bio?: string;
  followers: number;
  following: number;
  snippets: number;
  joinedAt: string;
  isFollowing?: boolean;
  isFollower?: boolean;
}

const CommunityFollowers: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'followers' | 'following'>('followers');
  const [followers, setFollowers] = useState<User[]>([]);
  const [following, setFollowing] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setIsLoading(true);
      const [followersData, followingData] = await Promise.all([
        ApiService.getFollowers(),
        ApiService.getFollowing()
      ]);
      setFollowers(followersData);
      setFollowing(followingData);
    } catch (error) {
      console.error('Error loading users:', error);
      // Use mock data for demo
      const mockUsers: User[] = [
        {
          id: '1',
          username: 'sarah_chen',
          displayName: 'Sarah Chen',
          bio: 'AI Researcher and educator passionate about making machine learning accessible',
          followers: 1250,
          following: 340,
          snippets: 45,
          joinedAt: '2023-06-15',
          isFollowing: false
        },
        {
          id: '2',
          username: 'alex_dev',
          displayName: 'Alex Thompson',
          bio: 'Full-stack developer specializing in React and Node.js',
          followers: 890,
          following: 520,
          snippets: 78,
          joinedAt: '2023-08-22',
          isFollowing: true
        },
        {
          id: '3',
          username: 'maria_gonzalez',
          displayName: 'Maria Garcia',
          bio: 'Data scientist | Python enthusiast | Open source contributor',
          followers: 2100,
          following: 180,
          snippets: 62,
          joinedAt: '2023-04-10',
          isFollowing: false
        },
        {
          id: '4',
          username: 'james_wilson',
          displayName: 'James Wilson',
          bio: 'Building the future of education tech',
          followers: 567,
          following: 890,
          snippets: 23,
          joinedAt: '2023-11-05',
          isFollowing: true
        },
        {
          id: '5',
          username: 'priya_sharma',
          displayName: 'Priya Sharma',
          bio: 'Backend architect | Distributed systems | Cloud infrastructure',
          followers: 1890,
          following: 145,
          snippets: 91,
          joinedAt: '2023-03-18',
          isFollowing: false
        },
        {
          id: '6',
          username: 'david_kim',
          displayName: 'David Kim',
          bio: 'Mobile developer | React Native | iOS & Android',
          followers: 720,
          following: 410,
          snippets: 34,
          joinedAt: '2023-09-30',
          isFollowing: true
        }
      ];
      setFollowers(mockUsers);
      setFollowing(mockUsers.slice(1, 5));
    } finally {
      setIsLoading(false);
    }
  };

  const handleFollow = async (userId: string) => {
    try {
      await ApiService.followUser(userId);
      setFollowers(prev => prev.map(user =>
        user.id === userId ? { ...user, isFollowing: true, followers: user.followers + 1 } : user
      ));
      setFollowing(prev => prev.map(user =>
        user.id === userId ? { ...user, isFollowing: true } : user
      ));
      if (selectedUser && selectedUser.id === userId) {
        setSelectedUser(prev => prev ? { ...prev, isFollowing: true, followers: prev.followers + 1 } : null);
      }
    } catch (error) {
      console.error('Error following user:', error);
    }
  };

  const handleUnfollow = async (userId: string) => {
    try {
      await ApiService.unfollowUser(userId);
      setFollowers(prev => prev.map(user =>
        user.id === userId ? { ...user, isFollowing: false, followers: user.followers - 1 } : user
      ));
      setFollowing(prev => prev.map(user =>
        user.id === userId ? { ...user, isFollowing: false } : user
      ));
      if (selectedUser && selectedUser.id === userId) {
        setSelectedUser(prev => prev ? { ...prev, isFollowing: false, followers: prev.followers - 1 } : null);
      }
    } catch (error) {
      console.error('Error unfollowing user:', error);
    }
  };

  const currentUsers = activeTab === 'followers' ? followers : following;
  
  const filteredUsers = currentUsers.filter(user =>
    user.displayName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.username.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'long',
      year: 'numeric'
    });
  };

  if (isLoading) {
    return (
      <div className="community-followers">
        <div className="followers-loading">
          <div className="loading-spinner"></div>
          <p>Loading community connections...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="community-followers">
      <div className="followers-header">
        <div className="header-title">
          <h2>Community Connections</h2>
          <p>Manage your followers and who you follow</p>
        </div>
        <div className="search-box">
          <input
            type="text"
            placeholder="Search users..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <span className="search-icon">🔍</span>
        </div>
      </div>

      <div className="followers-tabs">
        <button
          className={`tab ${activeTab === 'followers' ? 'active' : ''}`}
          onClick={() => setActiveTab('followers')}
        >
          <span className="tab-icon">👥</span>
          Followers
          <span className="count">{followers.length}</span>
        </button>
        <button
          className={`tab ${activeTab === 'following' ? 'active' : ''}`}
          onClick={() => setActiveTab('following')}
        >
          <span className="tab-icon">👤</span>
          Following
          <span className="count">{following.length}</span>
        </button>
      </div>

      {filteredUsers.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">{activeTab === 'followers' ? '👥' : '👤'}</div>
          <h3>No {activeTab} found</h3>
          <p>
            {searchQuery
              ? `No users match "${searchQuery}"`
              : `No ${activeTab} to show`}
          </p>
          {searchQuery && (
            <button className="clear-search" onClick={() => setSearchQuery('')}>
              Clear Search
            </button>
          )}
        </div>
      ) : (
        <div className="users-list">
          {filteredUsers.map(user => (
            <div key={user.id} className="user-card" onClick={() => setSelectedUser(user)}>
              <div className="user-avatar">
                {user.avatar ? (
                  <img src={user.avatar} alt={user.displayName} />
                ) : (
                  <div className="avatar-placeholder">
                    {user.displayName.charAt(0).toUpperCase()}
                  </div>
                )}
              </div>
              <div className="user-info">
                <div className="user-name">
                  <h4>{user.displayName}</h4>
                  <span className="username">@{user.username}</span>
                </div>
                <p className="user-bio">{user.bio}</p>
                <div className="user-stats">
                  <span><strong>{user.followers}</strong> followers</span>
                  <span><strong>{user.following}</strong> following</span>
                  <span><strong>{user.snippets}</strong> snippets</span>
                </div>
              </div>
              <div className="user-actions">
                {user.isFollowing ? (
                  <button
                    className="btn-following"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleUnfollow(user.id);
                    }}
                  >
                    Following
                  </button>
                ) : (
                  <button
                    className="btn-follow"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleFollow(user.id);
                    }}
                  >
                    Follow
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedUser && (
        <div className="user-modal-overlay" onClick={() => setSelectedUser(null)}>
          <div className="user-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-avatar">
                {selectedUser.avatar ? (
                  <img src={selectedUser.avatar} alt={selectedUser.displayName} />
                ) : (
                  <div className="avatar-placeholder large">
                    {selectedUser.displayName.charAt(0).toUpperCase()}
                  </div>
                )}
              </div>
              <button className="close-btn" onClick={() => setSelectedUser(null)}>✕</button>
            </div>
            <div className="modal-body">
              <h2>{selectedUser.displayName}</h2>
              <span className="modal-username">@{selectedUser.username}</span>
              <p className="modal-bio">{selectedUser.bio}</p>
              <div className="modal-stats">
                <div className="stat">
                  <span className="stat-value">{selectedUser.followers}</span>
                  <span className="stat-label">Followers</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{selectedUser.following}</span>
                  <span className="stat-label">Following</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{selectedUser.snippets}</span>
                  <span className="stat-label">Snippets</span>
                </div>
              </div>
              <p className="modal-joined">Joined {formatDate(selectedUser.joinedAt)}</p>
            </div>
            <div className="modal-footer">
              {selectedUser.isFollowing ? (
                <button
                  className="btn-unfollow"
                  onClick={() => {
                    handleUnfollow(selectedUser.id);
                    setSelectedUser(null);
                  }}
                >
                  Unfollow
                </button>
              ) : (
                <button
                  className="btn-primary"
                  onClick={() => {
                    handleFollow(selectedUser.id);
                  }}
                >
                  Follow
                </button>
              )}
              <button className="btn-secondary">View Profile</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CommunityFollowers;
