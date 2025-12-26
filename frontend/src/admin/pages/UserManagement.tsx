/**
 * User Management Page - Admin user management interface
 */

import React, { useState, useEffect } from 'react';
import adminApi from '../../services/adminApi';
import { AdminUser } from '../../services/adminApi';
import '../Admin.css';

interface UserManagementProps {
  activeSection: string;
}

const UserManagement: React.FC<UserManagementProps> = ({ activeSection }) => {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedUsers, setSelectedUsers] = useState<string[]>([]);
  const [filters, setFilters] = useState({
    include_inactive: false,
    admin_only: false,
  });

  useEffect(() => {
    if (activeSection === 'users') {
      loadUsers();
    }
  }, [activeSection]);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const response = await adminApi.getUsers({
        limit: 100,
        ...filters,
        search: searchTerm || undefined,
      });
      if (response.success) {
        setUsers(response.users);
      } else {
        setError('Failed to load users');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleAdmin = async (userId: string, currentStatus: boolean) => {
    try {
      const response = await adminApi.updateUser(userId, {
        is_admin: !currentStatus,
      });
      if (response.success) {
        loadUsers();
      } else {
        alert('Failed to update user: ' + response.message);
      }
    } catch (err: any) {
      alert('Error: ' + err.message);
    }
  };

  const handleToggleActive = async (userId: string, currentStatus: boolean) => {
    try {
      const response = await adminApi.updateUser(userId, {
        is_active: !currentStatus,
      });
      if (response.success) {
        loadUsers();
      } else {
        alert('Failed to update user: ' + response.message);
      }
    } catch (err: any) {
      alert('Error: ' + err.message);
    }
  };

  const handleBulkAction = async (action: 'suspend' | 'activate') => {
    if (selectedUsers.length === 0) {
      alert('Please select users first');
      return;
    }

    if (!confirm(`Are you sure you want to ${action} ${selectedUsers.length} users?`)) {
      return;
    }

    try {
      const response = await adminApi.bulkUserAction(selectedUsers, action);
      if (response.success) {
        alert(response.message);
        setSelectedUsers([]);
        loadUsers();
      } else {
        alert('Failed: ' + response.message);
      }
    } catch (err: any) {
      alert('Error: ' + err.message);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadUsers();
  };

  const toggleUserSelection = (userId: string) => {
    setSelectedUsers(prev => 
      prev.includes(userId) 
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="spinner"></div>
        <span>Loading users...</span>
      </div>
    );
  }

  return (
    <div className="user-management">
      {/* Filters and Actions */}
      <div className="admin-card" style={{ marginBottom: '24px' }}>
        <div className="admin-card-body">
          <div className="filter-bar">
            <form onSubmit={handleSearch} style={{ display: 'flex', gap: '12px', flex: 1 }}>
              <input
                type="text"
                className="form-input"
                placeholder="Search by username, email, or name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{ maxWidth: '400px' }}
              />
              <button type="submit" className="btn btn-primary">
                Search
              </button>
            </form>

            <div style={{ display: 'flex', gap: '12px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '14px' }}>
                <input
                  type="checkbox"
                  checked={filters.include_inactive}
                  onChange={(e) => setFilters(f => ({ ...f, include_inactive: e.target.checked }))}
                />
                Include Inactive
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '14px' }}>
                <input
                  type="checkbox"
                  checked={filters.admin_only}
                  onChange={(e) => setFilters(f => ({ ...f, admin_only: e.target.checked }))}
                />
                Admin Only
              </label>
              <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
                ➕ Create Admin
              </button>
            </div>
          </div>

          {selectedUsers.length > 0 && (
            <div style={{ marginTop: '16px', padding: '12px', background: '#f3f4f6', borderRadius: '8px' }}>
              <span style={{ marginRight: '16px' }}>
                {selectedUsers.length} user(s) selected
              </span>
              <button 
                className="btn btn-danger btn-sm" 
                onClick={() => handleBulkAction('suspend')}
              >
                Suspend Selected
              </button>
              <button 
                className="btn btn-success btn-sm" 
                style={{ marginLeft: '8px', background: '#dcfce7', color: '#16a34a' }}
                onClick={() => handleBulkAction('activate')}
              >
                Activate Selected
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Users Table */}
      <div className="admin-card">
        <div className="admin-card-header">
          <h2>Users ({users.length})</h2>
        </div>
        <div className="admin-card-body" style={{ padding: 0 }}>
          {users.length > 0 ? (
            <table className="admin-table">
              <thead>
                <tr>
                  <th style={{ width: '40px' }}>
                    <input
                      type="checkbox"
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedUsers(users.map(u => u.user_id));
                        } else {
                          setSelectedUsers([]);
                        }
                      }}
                      checked={selectedUsers.length === users.length && users.length > 0}
                    />
                  </th>
                  <th>User</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Joined</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.user_id}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedUsers.includes(user.user_id)}
                        onChange={() => toggleUserSelection(user.user_id)}
                      />
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span style={{ fontSize: '24px' }}>👤</span>
                        <div>
                          <div style={{ fontWeight: '500' }}>
                            {user.first_name} {user.last_name}
                          </div>
                          <div style={{ fontSize: '13px', color: '#6b7280' }}>
                            @{user.username}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td>{user.email}</td>
                    <td>
                      <span className={`badge ${user.is_admin ? 'badge-info' : 'badge-secondary'}`}>
                        {user.admin_role || 'student'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${user.is_active ? 'badge-success' : 'badge-danger'}`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>{formatDate(user.created_at)}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                          className="btn btn-sm btn-secondary"
                          onClick={() => handleToggleAdmin(user.user_id, user.is_admin)}
                          title={user.is_admin ? 'Remove Admin' : 'Make Admin'}
                        >
                          {user.is_admin ? '👑' : '👤'}
                        </button>
                        <button
                          className="btn btn-sm btn-secondary"
                          onClick={() => handleToggleActive(user.user_id, user.is_active)}
                          title={user.is_active ? 'Deactivate' : 'Activate'}
                        >
                          {user.is_active ? '⏸️' : '✅'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">👥</div>
              <h3>No Users Found</h3>
              <p>Try adjusting your search or filters</p>
            </div>
          )}
        </div>
      </div>

      {/* Create Admin Modal */}
      {showCreateModal && (
        <CreateAdminModal
          onClose={() => setShowCreateModal(false)}
          onCreated={() => {
            setShowCreateModal(false);
            loadUsers();
          }}
        />
      )}
    </div>
  );
};

// Create Admin Modal Component
const CreateAdminModal: React.FC<{ onClose: () => void; onCreated: () => void }> = ({ onClose, onCreated }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    admin_role: 'admin',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await adminApi.createAdminUser(formData);
      if (response.success) {
        alert('Admin created successfully!');
        onCreated();
      } else {
        setError(response.message || 'Failed to create admin');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create admin');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    }}>
      <div className="modal-content" style={{
        background: 'white',
        borderRadius: '12px',
        padding: '24px',
        width: '100%',
        maxWidth: '480px',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ margin: 0 }}>Create Admin User</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer' }}>×</button>
        </div>

        {error && (
          <div style={{ padding: '12px', background: '#fee2e2', color: '#dc2626', borderRadius: '8px', marginBottom: '16px' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Username *</label>
            <input
              type="text"
              className="form-input"
              value={formData.username}
              onChange={(e) => setFormData(f => ({ ...f, username: e.target.value }))}
              required
              minLength={3}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Email *</label>
            <input
              type="email"
              className="form-input"
              value={formData.email}
              onChange={(e) => setFormData(f => ({ ...f, email: e.target.value }))}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password *</label>
            <input
              type="password"
              className="form-input"
              value={formData.password}
              onChange={(e) => setFormData(f => ({ ...f, password: e.target.value }))}
              required
              minLength={8}
            />
          </div>

          <div style={{ display: 'flex', gap: '16px' }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">First Name</label>
              <input
                type="text"
                className="form-input"
                value={formData.first_name}
                onChange={(e) => setFormData(f => ({ ...f, first_name: e.target.value }))}
              />
            </div>

            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Last Name</label>
              <input
                type="text"
                className="form-input"
                value={formData.last_name}
                onChange={(e) => setFormData(f => ({ ...f, last_name: e.target.value }))}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Admin Role *</label>
            <select
              className="form-select"
              value={formData.admin_role}
              onChange={(e) => setFormData(f => ({ ...f, admin_role: e.target.value }))}
            >
              <option value="admin">Admin</option>
              <option value="content_admin">Content Admin</option>
              <option value="user_admin">User Admin</option>
              <option value="super_admin">Super Admin</option>
            </select>
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '24px' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Admin'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UserManagement;
