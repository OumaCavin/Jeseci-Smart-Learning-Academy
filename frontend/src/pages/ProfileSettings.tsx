import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/api';

interface ProfileFormData {
  first_name: string;
  last_name: string;
  bio: string;
  avatar_url: string;
}

interface PreferenceFormData {
  learning_style: string;
  skill_level: string;
  daily_goal_minutes: number;
  preferred_difficulty: string;
  preferred_content_type: string;
  notifications_enabled: boolean;
  email_reminders: boolean;
  dark_mode: boolean;
  auto_play_videos: boolean;
}

interface NotificationSettingsData {
  email_notifications: boolean;
  push_notifications: boolean;
  course_updates: boolean;
  community_mentions: boolean;
  achievement_alerts: boolean;
  weekly_digest: boolean;
  marketing_emails: boolean;
}

const ProfileSettings: React.FC = () => {
  const { user } = useAuth();
  const [activeSection, setActiveSection] = useState<'profile' | 'preferences' | 'notifications' | 'streak'>('profile');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const [profileData, setProfileData] = useState<ProfileFormData>({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    bio: '',
    avatar_url: ''
  });

  const [preferences, setPreferences] = useState<PreferenceFormData>({
    learning_style: user?.learning_style || 'visual',
    skill_level: user?.skill_level || 'beginner',
    daily_goal_minutes: 30,
    preferred_difficulty: 'intermediate',
    preferred_content_type: 'text',
    notifications_enabled: true,
    email_reminders: true,
    dark_mode: false,
    auto_play_videos: true
  });

  const [notificationSettings, setNotificationSettings] = useState<NotificationSettingsData>({
    email_notifications: true,
    push_notifications: true,
    course_updates: true,
    community_mentions: true,
    achievement_alerts: true,
    weekly_digest: true,
    marketing_emails: false
  });

  const [streakData, setStreakData] = useState<any>(null);

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      setLoading(true);
      const [profile, streak] = await Promise.all([
        apiService.getUserProfile(),
        apiService.getLearningStreak()
      ]);

      if (profile && typeof profile === 'object') {
        setProfileData(prev => ({
          ...prev,
          first_name: profile.first_name || prev.first_name,
          last_name: profile.last_name || prev.last_name,
          bio: profile.bio || '',
          avatar_url: profile.avatar_url || ''
        }));
      }

      setStreakData(streak);
    } catch (error) {
      console.error('Error loading user data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      await apiService.updateProfile(profileData);
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to update profile' });
    } finally {
      setLoading(false);
    }
  };

  const handlePreferencesSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      await apiService.updatePreferences(preferences);
      setMessage({ type: 'success', text: 'Preferences updated successfully!' });
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to update preferences' });
    } finally {
      setLoading(false);
    }
  };

  const handleNotificationSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      await apiService.updateNotificationSettings(notificationSettings);
      setMessage({ type: 'success', text: 'Notification settings updated successfully!' });
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to update notification settings' });
    } finally {
      setLoading(false);
    }
  };

  const renderProfileSection = () => (
    <div className="profile-section">
      <h3>Profile Information</h3>
      <form onSubmit={handleProfileSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="first_name">First Name</label>
            <input
              type="text"
              id="first_name"
              value={profileData.first_name}
              onChange={(e) => setProfileData(prev => ({ ...prev, first_name: e.target.value }))}
              placeholder="Enter your first name"
            />
          </div>
          <div className="form-group">
            <label htmlFor="last_name">Last Name</label>
            <input
              type="text"
              id="last_name"
              value={profileData.last_name}
              onChange={(e) => setProfileData(prev => ({ ...prev, last_name: e.target.value }))}
              placeholder="Enter your last name"
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="bio">Bio</label>
          <textarea
            id="bio"
            value={profileData.bio}
            onChange={(e) => setProfileData(prev => ({ ...prev, bio: e.target.value }))}
            placeholder="Tell us about yourself..."
            rows={4}
          />
        </div>

        <div className="form-group">
          <label htmlFor="avatar_url">Avatar URL</label>
          <input
            type="url"
            id="avatar_url"
            value={profileData.avatar_url}
            onChange={(e) => setProfileData(prev => ({ ...prev, avatar_url: e.target.value }))}
            placeholder="https://example.com/avatar.jpg"
          />
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>
    </div>
  );

  const renderPreferencesSection = () => (
    <div className="preferences-section">
      <h3>Learning Preferences</h3>
      <form onSubmit={handlePreferencesSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="learning_style">Learning Style</label>
            <select
              id="learning_style"
              value={preferences.learning_style}
              onChange={(e) => setPreferences(prev => ({ ...prev, learning_style: e.target.value }))}
            >
              <option value="visual">Visual Learner</option>
              <option value="auditory">Auditory Learner</option>
              <option value="kinesthetic">Kinesthetic Learner</option>
              <option value="reading">Reading/Writing Learner</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="skill_level">Skill Level</label>
            <select
              id="skill_level"
              value={preferences.skill_level}
              onChange={(e) => setPreferences(prev => ({ ...prev, skill_level: e.target.value }))}
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="daily_goal_minutes">Daily Learning Goal (minutes)</label>
            <input
              type="number"
              id="daily_goal_minutes"
              value={preferences.daily_goal_minutes}
              onChange={(e) => setPreferences(prev => ({ ...prev, daily_goal_minutes: parseInt(e.target.value) || 30 }))}
              min={5}
              max={300}
            />
          </div>
          <div className="form-group">
            <label htmlFor="preferred_difficulty">Preferred Difficulty</label>
            <select
              id="preferred_difficulty"
              value={preferences.preferred_difficulty}
              onChange={(e) => setPreferences(prev => ({ ...prev, preferred_difficulty: e.target.value }))}
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="preferred_content_type">Preferred Content Type</label>
          <select
            id="preferred_content_type"
            value={preferences.preferred_content_type}
            onChange={(e) => setPreferences(prev => ({ ...prev, preferred_content_type: e.target.value }))}
          >
            <option value="text">Text</option>
            <option value="video">Video</option>
            <option value="interactive">Interactive</option>
            <option value="mixed">Mixed</option>
          </select>
        </div>

        <div className="form-group">
          <h4>Display Settings</h4>
          <div className="checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={preferences.dark_mode}
                onChange={(e) => setPreferences(prev => ({ ...prev, dark_mode: e.target.checked }))}
              />
              <span>Dark Mode</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={preferences.auto_play_videos}
                onChange={(e) => setPreferences(prev => ({ ...prev, auto_play_videos: e.target.checked }))}
              />
              <span>Auto-play Videos</span>
            </label>
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Saving...' : 'Save Preferences'}
          </button>
        </div>
      </form>
    </div>
  );

  const renderNotificationsSection = () => (
    <div className="notifications-section">
      <h3>Notification Settings</h3>
      <form onSubmit={handleNotificationSubmit}>
        <div className="form-group">
          <h4>Notification Channels</h4>
          <div className="checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={notificationSettings.email_notifications}
                onChange={(e) => setNotificationSettings(prev => ({ ...prev, email_notifications: e.target.checked }))}
              />
              <span>Email Notifications</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={notificationSettings.push_notifications}
                onChange={(e) => setNotificationSettings(prev => ({ ...prev, push_notifications: e.target.checked }))}
              />
              <span>Push Notifications</span>
            </label>
          </div>
        </div>

        <div className="form-group">
          <h4>Notification Types</h4>
          <div className="checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={notificationSettings.course_updates}
                onChange={(e) => setNotificationSettings(prev => ({ ...prev, course_updates: e.target.checked }))}
              />
              <span>Course Updates</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={notificationSettings.community_mentions}
                onChange={(e) => setNotificationSettings(prev => ({ ...prev, community_mentions: e.target.checked }))}
              />
              <span>Community Mentions</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={notificationSettings.achievement_alerts}
                onChange={(e) => setNotificationSettings(prev => ({ ...prev, achievement_alerts: e.target.checked }))}
              />
              <span>Achievement Alerts</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={notificationSettings.weekly_digest}
                onChange={(e) => setNotificationSettings(prev => ({ ...prev, weekly_digest: e.target.checked }))}
              />
              <span>Weekly Digest</span>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={notificationSettings.marketing_emails}
                onChange={(e) => setNotificationSettings(prev => ({ ...prev, marketing_emails: e.target.checked }))}
              />
              <span>Marketing Emails</span>
            </label>
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Saving...' : 'Save Notification Settings'}
          </button>
        </div>
      </form>
    </div>
  );

  const renderStreakSection = () => (
    <div className="streak-section">
      <h3>Learning Streak</h3>
      {streakData ? (
        <div className="streak-stats">
          <div className="streak-card">
            <span className="streak-icon">🔥</span>
            <span className="streak-value">{streakData.current_streak || 0}</span>
            <span className="streak-label">Current Streak</span>
          </div>
          <div className="streak-card">
            <span className="streak-icon">🏆</span>
            <span className="streak-value">{streakData.longest_streak || 0}</span>
            <span className="streak-label">Longest Streak</span>
          </div>
          <div className="streak-card">
            <span className="streak-icon">📅</span>
            <span className="streak-value">{streakData.total_days_learned || 0}</span>
            <span className="streak-label">Total Days</span>
          </div>
          <div className="streak-card">
            <span className="streak-icon">⏱️</span>
            <span className="streak-value">{streakData.total_minutes || 0}</span>
            <span className="streak-label">Total Minutes</span>
          </div>
        </div>
      ) : (
        <p>No streak data available yet. Start learning to build your streak!</p>
      )}
    </div>
  );

  return (
    <div className="profile-settings-page">
      <div className="settings-header">
        <h2>Settings</h2>
        <p>Manage your profile, preferences, and notifications</p>
      </div>

      {message && (
        <div className={`settings-message ${message.type}`}>
          {message.text}
          <button onClick={() => setMessage(null)}>×</button>
        </div>
      )}

      <div className="settings-layout">
        <nav className="settings-nav">
          <button
            className={activeSection === 'profile' ? 'active' : ''}
            onClick={() => setActiveSection('profile')}
          >
            👤 Profile
          </button>
          <button
            className={activeSection === 'preferences' ? 'active' : ''}
            onClick={() => setActiveSection('preferences')}
          >
            ⚙️ Learning Preferences
          </button>
          <button
            className={activeSection === 'notifications' ? 'active' : ''}
            onClick={() => setActiveSection('notifications')}
          >
            🔔 Notifications
          </button>
          <button
            className={activeSection === 'streak' ? 'active' : ''}
            onClick={() => setActiveSection('streak')}
          >
            🔥 Learning Streak
          </button>
        </nav>

        <div className="settings-content">
          {activeSection === 'profile' && renderProfileSection()}
          {activeSection === 'preferences' && renderPreferencesSection()}
          {activeSection === 'notifications' && renderNotificationsSection()}
          {activeSection === 'streak' && renderStreakSection()}
        </div>
      </div>
    </div>
  );
};

export default ProfileSettings;
