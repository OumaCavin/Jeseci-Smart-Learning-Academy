/**
 * Community Dashboard Component
 * 
 * Main entry point for community and collaboration features
 * displaying forums, connections, and advanced collaboration tools.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Users,
  MessageCircle,
  MessageSquare,
  Search,
  Plus,
  Loader,
  RefreshCw,
  UserPlus,
  Settings,
  Star,
  BookOpen,
  Award,
  Shield,
  Users as GroupIcon,
  TrendingUp,
  Target,
  Activity
} from 'lucide-react';
import { getForums, getConnectionRequests, getConnections, Forum as ForumType, Connection, ConnectionRequest } from '../../services/collaborationService';
import UserConnections from './UserConnections';
import ForumList from './Forum/ForumList';
import CreateThreadModal from './Forum/CreateThreadModal';
import ConnectionRequestModal from './ConnectionRequestModal';
import Reputation from './Reputation';
import StudyGroups from './StudyGroups';
import Mentorship from './Mentorship';
import Moderation from './Moderation';
import PeerReview from './PeerReview';

interface CommunityDashboardProps {
  onNavigateToThread?: (threadId: string) => void;
}

type TabType = 'forums' | 'connections' | 'requests' | 'reputation' | 'study-groups' | 'mentorship' | 'moderation' | 'peer-review';

const CommunityDashboard: React.FC<CommunityDashboardProps> = ({ onNavigateToThread }) => {
  const [activeTab, setActiveTab] = useState<TabType>('forums');
  const [forums, setForums] = useState<ForumType[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [connectionRequests, setConnectionRequests] = useState<ConnectionRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateThread, setShowCreateThread] = useState(false);
  const [showAddConnection, setShowAddConnection] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [forumsResult, requestsResult, connectionsResult] = await Promise.all([
        getForums(),
        getConnectionRequests(),
        getConnections('accepted')
      ]);

      if (forumsResult.success) {
        setForums(forumsResult.forums);
      } else {
        setError('Failed to load forums');
      }

      if (requestsResult.success) {
        setConnectionRequests(requestsResult.requests);
      }

      if (connectionsResult.success) {
        setConnections(connectionsResult.connections);
      }
    } catch (err) {
      setError('Failed to load community data');
      console.error('Error loading community data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleThreadClick = (threadId: string) => {
    if (onNavigateToThread) {
      onNavigateToThread(threadId);
    }
    // Navigate to thread detail - would typically use React Router
    console.log('Navigate to thread:', threadId);
  };

  const handleThreadCreated = (newThread: { thread_id: string; forum_id: string }) => {
    setShowCreateThread(false);
    // Could navigate to the new thread or refresh the list
    loadData();
  };

  const handleConnectionAccepted = () => {
    // Refresh connections when a request is accepted
    loadData();
  };

  const isAdvancedTab = (tab: TabType) => {
    return ['reputation', 'study-groups', 'mentorship', 'moderation', 'peer-review'].includes(tab);
  };

  const renderTabContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center py-12">
          <Loader className="w-8 h-8 animate-spin text-blue-600" />
          <span className="ml-3 text-gray-600">Loading community data...</span>
        </div>
      );
    }

    if (error) {
      return (
        <div className="text-center py-12">
          <div className="text-red-500 mb-4">{error}</div>
          <button
            onClick={loadData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      );
    }

    // Advanced collaboration components handle their own loading states
    if (isAdvancedTab(activeTab)) {
      switch (activeTab) {
        case 'reputation':
          return <Reputation />;
        case 'study-groups':
          return <StudyGroups />;
        case 'mentorship':
          return <Mentorship />;
        case 'moderation':
          return <Moderation />;
        case 'peer-review':
          return <PeerReview />;
        default:
          return null;
      }
    }

    // Basic community features
    switch (activeTab) {
      case 'forums':
        return (
          <ForumList
            forums={forums}
            onThreadClick={handleThreadClick}
            onCreateThread={() => setShowCreateThread(true)}
          />
        );

      case 'connections':
        return (
          <UserConnections
            connections={connections}
            onRemove={loadData}
          />
        );

      case 'requests':
        return (
          <UserConnections
            requests={connectionRequests}
            onAccept={handleConnectionAccepted}
            onReject={handleConnectionAccepted}
            showActions={true}
          />
        );

      default:
        return null;
    }
  };

  // Header content based on active tab
  const renderHeaderContent = () => {
    const headers: Record<TabType, { title: string; subtitle: string; icon: React.ReactNode }> = {
      forums: {
        title: 'Discussion MessageSquares',
        subtitle: 'Engage in meaningful discussions with the community',
        icon: <MessageSquare className="w-6 h-6 text-white" />
      },
      connections: {
        title: 'My Connections',
        subtitle: 'Manage your professional network',
        icon: <Users className="w-6 h-6 text-white" />
      },
      requests: {
        title: 'Connection Requests',
        subtitle: 'Review pending connection requests',
        icon: <UserPlus className="w-6 h-6 text-white" />
      },
      reputation: {
        title: 'Reputation System',
        subtitle: 'Track your contributions and earn recognition',
        icon: <Star className="w-6 h-6 text-white" />
      },
      'study-groups': {
        title: 'Study Groups',
        subtitle: 'Join or create study groups for collaborative learning',
        icon: <GroupIcon className="w-6 h-6 text-white" />
      },
      mentorship: {
        title: 'Mentorship',
        subtitle: 'Connect with mentors or become one',
        icon: <Award className="w-6 h-6 text-white" />
      },
      moderation: {
        title: 'Content Moderation',
        subtitle: 'Help maintain a safe and helpful community',
        icon: <Shield className="w-6 h-6 text-white" />
      },
      'peer-review': {
        title: 'Peer Review',
        subtitle: 'Submit and review content for quality assurance',
        icon: <Target className="w-6 h-6 text-white" />
      }
    };

    const header = headers[activeTab];
    return (
      <div className="flex items-center justify-between py-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
            {header.icon}
          </div>
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              {header.title}
            </h1>
            <p className="text-sm text-gray-500">
              {header.subtitle}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="Refresh"
          >
            <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
          </button>
          {!isAdvancedTab(activeTab) && (
            <button
              onClick={() => setShowAddConnection(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <UserPlus className="w-4 h-4" />
              <span>Find Friends</span>
            </button>
          )}
        </div>
      </div>
    );
  };

  // Stats content based on active tab
  const renderStatsContent = () => {
    // Basic community stats
    const basicStats = (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{forums.length}</p>
              <p className="text-sm text-gray-500">Active MessageSquares</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Users className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{connections.length}</p>
              <p className="text-sm text-gray-500">Connections</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <MessageCircle className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{connectionRequests.length}</p>
              <p className="text-sm text-gray-500">Pending Requests</p>
            </div>
          </div>
        </div>
      </div>
    );

    // For advanced tabs, we'll show the component directly without additional stats
    if (isAdvancedTab(activeTab)) {
      return null;
    }

    return basicStats;
  };

  // Tabs configuration
  const tabs: { id: TabType; label: string; icon: React.ReactNode; badge?: number }[] = [
    { id: 'forums', label: 'MessageSquares', icon: <MessageSquare className="w-4 h-4 inline-block mr-2" /> },
    { id: 'connections', label: 'Connections', icon: <Users className="w-4 h-4 inline-block mr-2" /> },
    { 
      id: 'requests', 
      label: 'Requests', 
      icon: <UserPlus className="w-4 h-4 inline-block mr-2" />,
      badge: connectionRequests.length > 0 ? connectionRequests.length : undefined
    },
    { id: 'reputation', label: 'Reputation', icon: <Star className="w-4 h-4 inline-block mr-2" /> },
    { id: 'study-groups', label: 'Study Groups', icon: <GroupIcon className="w-4 h-4 inline-block mr-2" /> },
    { id: 'mentorship', label: 'Mentorship', icon: <Award className="w-4 h-4 inline-block mr-2" /> },
    { id: 'moderation', label: 'Moderation', icon: <Shield className="w-4 h-4 inline-block mr-2" /> },
    { id: 'peer-review', label: 'Peer Review', icon: <Target className="w-4 h-4 inline-block mr-2" /> },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          {renderHeaderContent()}
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview - only for basic tabs */}
        {renderStatsContent()}

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="border-b border-gray-200">
            <nav className="flex flex-wrap -mb-px">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center py-4 px-6 text-center font-medium text-sm transition-colors relative ${
                    activeTab === tab.id
                      ? 'border-b-2 border-blue-600 text-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab.icon}
                  {tab.label}
                  {tab.badge && (
                    <span className="absolute top-2 right-1/4 w-5 h-5 bg-yellow-500 text-white text-xs rounded-full flex items-center justify-center">
                      {tab.badge}
                    </span>
                  )}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {renderTabContent()}
          </div>
        </div>
      </div>

      {/* Modals - only for basic community features */}
      {showCreateThread && (
        <CreateThreadModal
          forums={forums}
          onClose={() => setShowCreateThread(false)}
          onThreadCreated={handleThreadCreated}
        />
      )}

      {showAddConnection && (
        <ConnectionRequestModal
          onClose={() => setShowAddConnection(false)}
          onRequestSent={() => {
            setShowAddConnection(false);
            loadData();
          }}
        />
      )}
    </div>
  );
};

export default CommunityDashboard;
