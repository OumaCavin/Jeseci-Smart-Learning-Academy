/**
 * Connection Request Modal
 * 
 * Modal for searching and sending connection requests to other users
 */

import React, { useState, useEffect } from 'react';
import { Search, UserPlus, X, Loader, Check } from 'lucide-react';
import { searchUsers, sendConnectionRequest, User } from '../../services/collaborationService';

interface ConnectionRequestModalProps {
  onClose: () => void;
  onRequestSent: () => void;
}

const ConnectionRequestModal: React.FC<ConnectionRequestModalProps> = ({ onClose, onRequestSent }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  const [sendingRequests, setSendingRequests] = useState<Record<string, boolean>>({});
  const [sentRequests, setSentRequests] = useState<Record<string, boolean>>({});
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (searchQuery.trim().length < 2) return;

    setSearching(true);
    setError(null);

    try {
      const result = await searchUsers(searchQuery.trim());
      if (result.success) {
        setSearchResults(result.users);
      } else {
        setError('Failed to search users');
      }
    } catch (err) {
      setError('An error occurred while searching');
      console.error('Search error:', err);
    } finally {
      setSearching(false);
    }
  };

  const handleSendRequest = async (userId: number) => {
    setSendingRequests(prev => ({ ...prev, [userId]: true }));
    setError(null);

    try {
      const result = await sendConnectionRequest(userId);
      if (result.success) {
        setSentRequests(prev => ({ ...prev, [userId]: true }));
      } else {
        setError(result.error || 'Failed to send request');
      }
    } catch (err) {
      setError('An error occurred while sending request');
      console.error('Send request error:', err);
    } finally {
      setSendingRequests(prev => ({ ...prev, [userId]: false }));
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Initial search with empty query to show recommended users
  useEffect(() => {
    const loadInitial = async () => {
      setLoading(true);
      const result = await searchUsers('');
      if (result.success) {
        setSearchResults(result.users);
      }
      setLoading(false);
    };
    loadInitial();
  }, []);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-lg w-full max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Find Friends</h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search Input */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Search by username or name..."
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              autoFocus
            />
            <button
              onClick={handleSearch}
              disabled={searching}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 px-4 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {searching ? 'Searching...' : 'Search'}
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mx-6 mt-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Results */}
        <div className="px-6 py-4 overflow-y-auto" style={{ maxHeight: '400px' }}>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader className="w-8 h-8 animate-spin text-blue-600" />
              <span className="ml-3 text-gray-600">Loading users...</span>
            </div>
          ) : searchResults.length === 0 ? (
            <div className="text-center py-12">
              <UserPlus className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No users found</p>
            </div>
          ) : (
            <div className="space-y-3">
              {searchResults.map((user) => (
                <div
                  key={user.user_id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-medium">
                      {user.first_name
                        ? user.first_name.charAt(0).toUpperCase()
                        : user.username.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">
                        {user.first_name && user.last_name
                          ? `${user.first_name} ${user.last_name}`
                          : user.username}
                      </h4>
                      <p className="text-sm text-gray-500">@{user.username}</p>
                    </div>
                  </div>

                  <button
                    onClick={() => handleSendRequest(user.user_id)}
                    disabled={sendingRequests[user.user_id] || sentRequests[user.user_id]}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                      sentRequests[user.user_id]
                        ? 'bg-green-100 text-green-700'
                        : 'bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50'
                    }`}
                  >
                    {sentRequests[user.user_id] ? (
                      <>
                        <Check className="w-4 h-4" />
                        <span>Sent</span>
                      </>
                    ) : sendingRequests[user.user_id] ? (
                      <Loader className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        <UserPlus className="w-4 h-4" />
                        <span>Connect</span>
                      </>
                    )}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <p className="text-sm text-gray-500 text-center">
            Send connection requests to connect with other learners
          </p>
        </div>
      </div>
    </div>
  );
};

export default ConnectionRequestModal;
