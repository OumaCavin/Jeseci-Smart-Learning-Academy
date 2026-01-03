/**
 * User Connections Component
 * 
 * Displays user's connections and handles connection management
 */

import React from 'react';
import { UserPlus, UserMinus, MessageCircle, Check, X } from 'lucide-react';
import { Connection } from '../../services/collaborationService';

interface UserConnectionsProps {
  connections?: Connection[];
  requests?: Connection[];
  onAccept?: (connectionId: string) => void;
  onReject?: (connectionId: string) => void;
  onRemove?: (connectionId: string) => void;
  showActions?: boolean;
}

const UserConnections: React.FC<UserConnectionsProps> = ({
  connections = [],
  requests = [],
  onAccept,
  onReject,
  onRemove,
  showActions = false
}) => {
  const displayConnections = requests.length > 0 ? requests : connections;

  if (displayConnections.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <UserPlus className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          {showActions ? 'No Pending Requests' : 'No Connections Yet'}
        </h3>
        <p className="text-gray-500">
          {showActions
            ? 'You have no connection requests at the moment.'
            : 'Start connecting with other learners to grow your network!'}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {displayConnections.map((connection) => (
        <div
          key={connection.connection_id}
          className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <div className="flex items-center space-x-4">
            {/* Avatar */}
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-medium">
              {connection.user.first_name
                ? connection.user.first_name.charAt(0).toUpperCase()
                : connection.user.username.charAt(0).toUpperCase()}
            </div>

            {/* User Info */}
            <div>
              <h4 className="font-medium text-gray-900">
                {connection.user.first_name && connection.user.last_name
                  ? `${connection.user.first_name} ${connection.user.last_name}`
                  : connection.user.username}
              </h4>
              <p className="text-sm text-gray-500">@{connection.user.username}</p>
              {connection.status === 'pending' && requests.length > 0 && (
                <p className="text-xs text-yellow-600 mt-1">Connection Request</p>
              )}
            </div>
          </div>

          {/* Actions */}
          {showActions && requests.length > 0 ? (
            <div className="flex items-center space-x-2">
              <button
                onClick={() => onAccept?.(connection.connection_id)}
                className="p-2 bg-green-100 text-green-600 rounded-lg hover:bg-green-200 transition-colors"
                title="Accept"
              >
                <Check className="w-4 h-4" />
              </button>
              <button
                onClick={() => onReject?.(connection.connection_id)}
                className="p-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors"
                title="Reject"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <button
                className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Send Message"
              >
                <MessageCircle className="w-4 h-4" />
              </button>
              <button
                onClick={() => onRemove?.(connection.connection_id)}
                className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Remove Connection"
              >
                <UserMinus className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default UserConnections;
