// Notification Settings Page
// Allows users to configure their notification preferences

import React, { useState, useEffect } from 'react';
import { 
  Bell, 
  Mail, 
  Smartphone, 
  Trophy, 
  GraduationCap, 
  BookOpen, 
  MessageCircle, 
  Flame, 
  Bot,
  Save,
  Loader,
  Check
} from 'lucide-react';
import { useNotifications } from '../contexts/NotificationContext';
import { NotificationType } from '../services/notificationService';

const NOTIFICATION_TYPES: { id: NotificationType; label: string; description: string; icon: React.ReactNode }[] = [
  {
    id: 'ACHIEVEMENT',
    label: 'Achievements',
    description: 'Get notified when you earn badges, complete milestones, or reach new levels',
    icon: <Trophy size={20} />,
  },
  {
    id: 'COURSE_MILESTONE',
    label: 'Course Progress',
    description: 'Updates on your course completion, new lessons, and learning streaks',
    icon: <GraduationCap size={20} />,
  },
  {
    id: 'CONTENT_UPDATE',
    label: 'New Content',
    description: 'Notifications about new courses, lessons, and learning materials',
    icon: <BookOpen size={20} />,
  },
  {
    id: 'COMMUNITY_REPLY',
    label: 'Community',
    description: 'Replies to your comments, mentions, and community interactions',
    icon: <MessageCircle size={20} />,
  },
  {
    id: 'STREAK_REMINDER',
    label: 'Streak Reminders',
    description: 'Reminders to maintain your learning streak and stay consistent',
    icon: <Flame size={20} />,
  },
  {
    id: 'AI_RESPONSE',
    label: 'AI Assistant',
    description: 'Responses from your AI learning assistant and recommendations',
    icon: <Bot size={20} />,
  },
  {
    id: 'SYSTEM_ANNOUNCEMENT',
    label: 'System Announcements',
    description: 'Important updates about the platform, new features, and policies',
    icon: <Bell size={20} />,
  },
];

export const NotificationSettings: React.FC = () => {
  const { preferences, fetchPreferences, updatePreferences } = useNotifications();
  
  const [localPreferences, setLocalPreferences] = useState({
    email_enabled: true,
    push_enabled: true,
    types_config: {} as Record<NotificationType, boolean>,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');

  // Load preferences on mount
  useEffect(() => {
    fetchPreferences();
  }, [fetchPreferences]);

  // Update local state when preferences change
  useEffect(() => {
    if (preferences) {
      setLocalPreferences({
        email_enabled: preferences.email_enabled,
        push_enabled: preferences.push_enabled,
        types_config: preferences.types_config,
      });
    }
  }, [preferences]);

  // Handle type toggle
  const handleTypeToggle = (typeId: NotificationType) => {
    setLocalPreferences(prev => ({
      ...prev,
      types_config: {
        ...prev.types_config,
        [typeId]: !prev.types_config[typeId],
      },
    }));
  };

  // Handle save
  const handleSave = async () => {
    setIsSaving(true);
    setSaveStatus('idle');
    
    try {
      await updatePreferences(localPreferences);
      setSaveStatus('success');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      setSaveStatus('error');
      console.error('Error saving preferences:', error);
    } finally {
      setIsSaving(false);
    }
  };

  // Handle reset to defaults
  const handleReset = () => {
    if (preferences) {
      setLocalPreferences({
        email_enabled: true,
        push_enabled: true,
        types_config: {
          ACHIEVEMENT: true,
          COURSE_MILESTONE: true,
          CONTENT_UPDATE: true,
          COMMUNITY_REPLY: true,
          STREAK_REMINDER: true,
          AI_RESPONSE: true,
          SYSTEM_ANNOUNCEMENT: true,
        },
      });
    }
  };

  // Check if all types are enabled
  const allTypesEnabled = Object.values(localPreferences.types_config).every(v => v);
  const allTypesDisabled = Object.values(localPreferences.types_config).every(v => !v);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Bell className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Notification Settings
                </h1>
                <p className="text-sm text-gray-500">
                  Customize how and when you receive notifications
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Delivery Preferences */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Delivery Preferences</h2>
            <p className="text-sm text-gray-500 mt-1">
              Choose how you want to receive notifications
            </p>
          </div>
          
          <div className="p-6 space-y-4">
            {/* In-app notifications */}
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Bell size={20} className="text-blue-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">In-App Notifications</p>
                  <p className="text-sm text-gray-500">
                    Receive notifications while using the platform
                  </p>
                </div>
              </div>
              <button
                onClick={() => setLocalPreferences(prev => ({ ...prev, push_enabled: !prev.push_enabled }))}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                          ${localPreferences.push_enabled ? 'bg-blue-600' : 'bg-gray-200'}`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                             ${localPreferences.push_enabled ? 'translate-x-6' : 'translate-x-1'}`}
                />
              </button>
            </div>

            {/* Email notifications */}
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Mail size={20} className="text-purple-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">Email Notifications</p>
                  <p className="text-sm text-gray-500">
                    Receive important updates in your inbox
                  </p>
                </div>
              </div>
              <button
                onClick={() => setLocalPreferences(prev => ({ ...prev, email_enabled: !prev.email_enabled }))}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                          ${localPreferences.email_enabled ? 'bg-blue-600' : 'bg-gray-200'}`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                             ${localPreferences.email_enabled ? 'translate-x-6' : 'translate-x-1'}`}
                />
              </button>
            </div>
          </div>
        </div>

        {/* Notification Types */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Notification Types</h2>
                <p className="text-sm text-gray-500 mt-1">
                  Choose which types of notifications you want to receive
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    const newConfig = NOTIFICATION_TYPES.reduce((acc, type) => {
                      acc[type.id] = !allTypesEnabled;
                      return acc;
                    }, {} as Record<NotificationType, boolean>);
                    setLocalPreferences(prev => ({ ...prev, types_config: newConfig }));
                  }}
                  className="text-sm text-blue-600 hover:text-blue-800 font-medium px-3 py-1.5 
                           hover:bg-blue-50 rounded-lg transition-colors"
                >
                  {allTypesEnabled ? 'Disable All' : 'Enable All'}
                </button>
              </div>
            </div>
          </div>
          
          <div className="divide-y divide-gray-100">
            {NOTIFICATION_TYPES.map(type => (
              <div key={type.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center
                                   ${localPreferences.types_config[type.id] 
                                     ? 'bg-blue-100 text-blue-600' 
                                     : 'bg-gray-100 text-gray-400'}`}>
                      {type.icon}
                    </div>
                    <div>
                      <p className={`font-medium ${localPreferences.types_config[type.id] ? 'text-gray-900' : 'text-gray-500'}`}>
                        {type.label}
                      </p>
                      <p className="text-sm text-gray-500">
                        {type.description}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleTypeToggle(type.id)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                              ${localPreferences.types_config[type.id] ? 'bg-blue-600' : 'bg-gray-200'}`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                                 ${localPreferences.types_config[type.id] ? 'translate-x-6' : 'translate-x-1'}`}
                    />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Save Actions */}
        <div className="flex items-center justify-between">
          <button
            onClick={handleReset}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 
                     rounded-lg transition-colors font-medium"
          >
            Reset to Defaults
          </button>
          
          <div className="flex items-center gap-3">
            {saveStatus === 'success' && (
              <span className="flex items-center gap-1 text-green-600 text-sm">
                <Check size={16} />
                Saved successfully
              </span>
            )}
            {saveStatus === 'error' && (
              <span className="text-red-600 text-sm">
                Failed to save. Please try again.
              </span>
            )}
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg 
                       hover:bg-blue-700 transition-colors font-medium disabled:opacity-50"
            >
              {isSaving ? (
                <>
                  <Loader size={18} className="animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save size={18} />
                  Save Changes
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationSettings;
