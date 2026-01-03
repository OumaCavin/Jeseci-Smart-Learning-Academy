import React, { useState, useEffect, useRef } from 'react';
import { apiService } from '../services/api';

interface User {
  user_id: string;
  username: string;
  first_name?: string;
  last_name?: string;
  avatar_url?: string;
}

interface Message {
  id: string;
  sender_id: string;
  receiver_id: string;
  content: string;
  created_at: string;
  is_read: boolean;
}

interface Conversation {
  user: User;
  last_message: Message;
  unread_count: number;
}

const CommunityMessages: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    if (selectedUser) {
      loadMessages(selectedUser.user_id);
    }
  }, [selectedUser]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadConversations = async () => {
    try {
      setLoading(true);
      const response = await apiService.getCommunityUsers(50, 0);
      // For now, we'll use community users as potential contacts
      // In a real implementation, this would fetch actual conversations
      if (Array.isArray(response)) {
        setConversations(response.slice(0, 10).map((user: any) => ({
          user,
          last_message: {
            id: '1',
            sender_id: user.user_id,
            receiver_id: 'me',
            content: 'Start a conversation',
            created_at: new Date().toISOString(),
            is_read: true
          },
          unread_count: 0
        })));
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async (userId: string) => {
    try {
      const response = await apiService.getCommunityMessages(userId);
      setMessages(Array.isArray(response) ? response : []);
    } catch (error) {
      console.error('Error loading messages:', error);
      setMessages([]);
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedUser) return;

    try {
      setSending(true);
      await apiService.sendCommunityMessage(selectedUser.user_id, newMessage);
      setNewMessage('');

      // Add message to local state
      const newMsg: Message = {
        id: Date.now().toString(),
        sender_id: 'me',
        receiver_id: selectedUser.user_id,
        content: newMessage,
        created_at: new Date().toISOString(),
        is_read: true
      };
      setMessages(prev => [...prev, newMsg]);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setSending(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const filteredUsers = conversations.filter(c =>
    c.user.username?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.user.first_name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="community-messages">
      <div className="messages-layout">
        <aside className="conversations-list">
          <div className="conversations-header">
            <h3>Messages</h3>
            <input
              type="text"
              placeholder="Search people..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="conversations">
            {loading ? (
              <div className="loading-state">Loading conversations...</div>
            ) : filteredUsers.length === 0 ? (
              <div className="empty-state">No conversations yet</div>
            ) : (
              filteredUsers.map(conv => (
                <div
                  key={conv.user.user_id}
                  className={`conversation-item ${selectedUser?.user_id === conv.user.user_id ? 'selected' : ''}`}
                  onClick={() => setSelectedUser(conv.user)}
                >
                  <div className="avatar">
                    {conv.user.avatar_url ? (
                      <img src={conv.user.avatar_url} alt={conv.user.username} />
                    ) : (
                      <span className="avatar-placeholder">
                        {conv.user.username?.charAt(0).toUpperCase()}
                      </span>
                    )}
                  </div>
                  <div className="conversation-info">
                    <div className="conversation-name">
                      {conv.user.first_name ? `${conv.user.first_name} ${conv.user.last_name || ''}` : conv.user.username}
                    </div>
                    <div className="conversation-preview">
                      {conv.last_message.content.substring(0, 40)}...
                    </div>
                  </div>
                  {conv.unread_count > 0 && (
                    <span className="unread-badge">{conv.unread_count}</span>
                  )}
                </div>
              ))
            )}
          </div>
        </aside>

        <main className="chat-area">
          {selectedUser ? (
            <>
              <div className="chat-header">
                <div className="chat-user-info">
                  <div className="avatar small">
                    {selectedUser.avatar_url ? (
                      <img src={selectedUser.avatar_url} alt={selectedUser.username} />
                    ) : (
                      <span className="avatar-placeholder">
                        {selectedUser.username?.charAt(0).toUpperCase()}
                      </span>
                    )}
                  </div>
                  <span className="chat-username">
                    {selectedUser.first_name ? `${selectedUser.first_name} ${selectedUser.last_name || ''}` : selectedUser.username}
                  </span>
                </div>
              </div>

              <div className="messages-container">
                {messages.length === 0 ? (
                  <div className="no-messages">
                    <p>No messages yet. Start the conversation!</p>
                  </div>
                ) : (
                  messages.map(msg => (
                    <div
                      key={msg.id}
                      className={`message ${msg.sender_id === 'me' ? 'sent' : 'received'}`}
                    >
                      <div className="message-content">
                        {msg.content}
                      </div>
                      <div className="message-time">
                        {formatTime(msg.created_at)}
                      </div>
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>

              <div className="message-input">
                <input
                  type="text"
                  placeholder="Type a message..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  disabled={sending}
                />
                <button onClick={handleSendMessage} disabled={!newMessage.trim() || sending}>
                  {sending ? 'Sending...' : 'Send'}
                </button>
              </div>
            </>
          ) : (
            <div className="no-conversation-selected">
              <span className="icon">💬</span>
              <h3>Select a conversation</h3>
              <p>Choose a person from the list to start messaging</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default CommunityMessages;
