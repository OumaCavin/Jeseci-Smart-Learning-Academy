/**
 * Community Dashboard Component
 * 
 * Main entry point for community and collaboration features
 * displaying forums, connections, and activity.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Users,
  MessageCircle,
  Forum,
  Search,
  Plus,
  Loader,
  RefreshCw,
  UserPlus,
  Settings
} from 'lucide-react';
import { getForums, getConnectionRequests, getConnections, Forum as ForumType, Connection } from '../../services/collaborationService';
import UserConnections from './UserConnections';
import ForumList from './Forum/ForumList';
import CreateThreadModal from './Forum/CreateThreadModal';
import ConnectionRequestModal from './ConnectionRequestModal';

interface CommunityDashboardProps {
  onNavigateToThread?: (threadId: string) => void;
}

type TabType = 'forums' | 'connections' | 'requests';

const CommunityDashboard: React.FC<CommunityDashboardProps> = ({ onNavigateToThread }) => {
  const [activeTab, setActiveTab] = useState<TabType>('forums');
  const [forums, setForums] = useState<ForumType[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [connectionRequests, setConnectionRequests] = useState<Connection[]>([]);
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
            onRemoveConnection={loadData}
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

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Community
                </h1>
                <p className="text-sm text-gray-500">
                  Connect, share, and learn together
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
              <button
                onClick={() => setShowAddConnection(true)}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <UserPlus className="w-4 h-4" />
                <span>Find Friends</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Forum className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{forums.length}</p>
                <p className="text-sm text-gray-500">Active Forums</p>
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

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('forums')}
                className={`flex-1 py-4 px-6 text-center font-medium text-sm transition-colors ${
                  activeTab === 'forums'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <Forum className="w-4 h-4 inline-block mr-2" />
                Discussion Forums
              </button>
              <button
                onClick={() => setActiveTab('connections')}
                className={`flex-1 py-4 px-6 text-center font-medium text-sm transition-colors ${
                  activeTab === 'connections'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <Users className="w-4 h-4 inline-block mr-2" />
                My Connections
              </button>
              <button
                onClick={() => setActiveTab('requests')}
                className={`flex-1 py-4 px-6 text-center font-medium text-sm transition-colors relative ${
                  activeTab === 'requests'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <UserPlus className="w-4 h-4 inline-block mr-2" />
                Requests
                {connectionRequests.length > 0 && (
                  <span className="absolute top-2 right-1/4 w-5 h-5 bg-yellow-500 text-white text-xs rounded-full flex items-center justify-center">
                    {connectionRequests.length}
                  </span>
                )}
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {renderTabContent()}
          </div>
        </div>
      </div>

      {/* Modals */}
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
