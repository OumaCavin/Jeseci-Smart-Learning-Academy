import React, { useState, useCallback, useMemo } from 'react';
import { useAdmin, SystemUser, BulkUserAction } from '../../contexts/AdminContext';
import './UserManagementTable.css';

interface UserManagementTableProps {
  onViewUser?: (user: SystemUser) => void;
  onEditUser?: (user: SystemUser) => void;
}

export function UserManagementTable({
  onViewUser,
  onEditUser,
}: UserManagementTableProps) {
  const {
    users,
    totalUsers,
    currentPage,
    pageSize,
    userFilter,
    selectedUsers,
    isLoading,
    fetchUsers,
    updateUser,
    suspendUser,
    activateUser,
    banUser,
    changeUserRole,
    deleteUser,
    bulkUserAction,
    toggleUserSelection,
    selectAllUsers,
    deselectAllUsers,
    setPage,
    setPageSize,
    setUserFilter,
  } = useAdmin();

  const [sortField, setSortField] = useState<keyof SystemUser>('metadata.createdAt');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [showBulkActions, setShowBulkActions] = useState(false);
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [selectedUserForRole, setSelectedUserForRole] = useState<SystemUser | null>(null);
  const [newRole, setNewRole] = useState<SystemUser['role']>('student');

  const totalPages = Math.ceil(totalUsers / pageSize);

  const handleSort = useCallback((field: keyof SystemUser) => {
    if (sortField === field) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  }, [sortField]);

  const sortedUsers = useMemo(() => {
    return [...users].sort((a, b) => {
      let aVal: unknown, bVal: unknown;
      const sortFieldStr = String(sortField);
      
      if (sortFieldStr.includes('.')) {
        const [parent, child] = sortFieldStr.split('.') as [keyof SystemUser, string];
        aVal = (a[parent] as Record<string, unknown>)?.[child];
        bVal = (b[parent] as Record<string, unknown>)?.[child];
      } else {
        aVal = a[sortField];
        bVal = b[sortField];
      }
      
      if (aVal === undefined || bVal === undefined) return 0;
      
      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [users, sortField, sortDirection]);

  const handleBulkAction = useCallback(async (action: BulkUserAction['action']) => {
    if (selectedUsers.length === 0) return;
    
    const reason = action === 'suspend' || action === 'ban' ? window.prompt('Please provide a reason:') : undefined;
    if (action !== 'activate' && action !== 'delete' && !reason) return;
    
    await bulkUserAction({ action, userIds: selectedUsers, reason: reason || undefined });
    setShowBulkActions(false);
  }, [selectedUsers, bulkUserAction]);

  const handleRoleChange = useCallback(async () => {
    if (!selectedUserForRole) return;
    
    await changeUserRole(selectedUserForRole.id, newRole);
    setShowRoleModal(false);
    setSelectedUserForRole(null);
  }, [selectedUserForRole, newRole, changeUserRole]);

  const getStatusBadge = (status: SystemUser['status']) => {
    switch (status) {
      case 'active': return <span className="status-badge active">Active</span>;
      case 'suspended': return <span className="status-badge suspended">Suspended</span>;
      case 'banned': return <span className="status-badge banned">Banned</span>;
      case 'pending': return <span className="status-badge pending">Pending</span>;
      default: return null;
    }
  };

  const getRoleBadge = (role: SystemUser['role']) => {
    const colors: Record<SystemUser['role'], string> = {
      student: '#3b82f6',
      instructor: '#10b981',
      moderator: '#f59e0b',
      admin: '#8b5cf6',
      super_admin: '#ef4444',
    };
    return (
      <span className="role-badge" style={{ backgroundColor: colors[role] }}>
        {role.replace('_', ' ')}
      </span>
    );
  };

  return (
    <div className="user-management-table">
      <div className="table-header">
        <div className="header-left">
          <h2>User Management</h2>
          <span className="user-count">{totalUsers} users</span>
        </div>
        <div className="header-actions">
          <div className="filter-group">
            <select
              value={userFilter.role || ''}
              onChange={(e) => setUserFilter({ ...userFilter, role: e.target.value as SystemUser['role'] || undefined })}
            >
              <option value="">All Roles</option>
              <option value="student">Student</option>
              <option value="instructor">Instructor</option>
              <option value="moderator">Moderator</option>
              <option value="admin">Admin</option>
            </select>
            <select
              value={userFilter.status || ''}
              onChange={(e) => setUserFilter({ ...userFilter, status: e.target.value as SystemUser['status'] || undefined })}
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="suspended">Suspended</option>
              <option value="banned">Banned</option>
              <option value="pending">Pending</option>
            </select>
            <input
              type="text"
              placeholder="Search users..."
              value={userFilter.searchText || ''}
              onChange={(e) => setUserFilter({ ...userFilter, searchText: e.target.value })}
            />
          </div>
        </div>
      </div>

      <div className="table-toolbar">
        <div className="selection-info">
          {selectedUsers.length > 0 ? (
            <>
              <span>{selectedUsers.length} selected</span>
              <button onClick={deselectAllUsers}>Clear selection</button>
            </>
          ) : (
            <span>Select users to perform bulk actions</span>
          )}
        </div>
        {selectedUsers.length > 0 && (
          <div className="bulk-actions">
            <button className="btn-bulk" onClick={() => handleBulkAction('activate')}>
              Activate
            </button>
            <button className="btn-bulk" onClick={() => handleBulkAction('suspend')}>
              Suspend
            </button>
            <button className="btn-bulk" onClick={() => handleBulkAction('ban')}>
              Ban
            </button>
            <button className="btn-bulk danger" onClick={() => {
              if (window.confirm(`Delete ${selectedUsers.length} users?`)) {
                handleBulkAction('delete');
              }
            }}>
              Delete
            </button>
          </div>
        )}
      </div>

      <div className="table-container">
        <table className="users-table">
          <thead>
            <tr>
              <th className="checkbox-col">
                <input
                  type="checkbox"
                  checked={users.length > 0 && selectedUsers.length === users.length}
                  onChange={(e) => {
                    if (e.target.checked) {
                      selectAllUsers();
                    } else {
                      deselectAllUsers();
                    }
                  }}
                />
              </th>
              <th onClick={() => handleSort('displayName')} className="sortable">
                User {sortField === 'displayName' && <span>{sortDirection === 'asc' ? '↑' : '↓'}</span>}
              </th>
              <th onClick={() => handleSort('email')} className="sortable">
                Email {sortField === 'email' && <span>{sortDirection === 'asc' ? '↑' : '↓'}</span>}
              </th>
              <th onClick={() => handleSort('role')} className="sortable">
                Role {sortField === 'role' && <span>{sortDirection === 'asc' ? '↑' : '↓'}</span>}
              </th>
              <th onClick={() => handleSort('status')} className="sortable">
                Status {sortField === 'status' && <span>{sortDirection === 'asc' ? '↑' : '↓'}</span>}
              </th>
              <th onClick={() => handleSort('metadata.createdAt')} className="sortable">
                Joined {sortField === 'metadata.createdAt' && <span>{sortDirection === 'asc' ? '↑' : '↓'}</span>}
              </th>
              <th onClick={() => handleSort('metadata.loginCount')} className="sortable">
                Logins {sortField === 'metadata.loginCount' && <span>{sortDirection === 'asc' ? '↑' : '↓'}</span>}
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={8} className="loading-row">
                  <div className="loading-spinner"></div>
                  Loading users...
                </td>
              </tr>
            ) : sortedUsers.length === 0 ? (
              <tr>
                <td colSpan={8} className="empty-row">
                  No users found
                </td>
              </tr>
            ) : (
              sortedUsers.map((user) => (
                <tr key={user.id} className={selectedUsers.includes(user.id) ? 'selected' : ''}>
                  <td className="checkbox-col">
                    <input
                      type="checkbox"
                      checked={selectedUsers.includes(user.id)}
                      onChange={() => toggleUserSelection(user.id)}
                    />
                  </td>
                  <td className="user-cell">
                    <div className="user-avatar">
                      {user.avatar ? (
                        <img src={user.avatar} alt={user.displayName} />
                      ) : (
                        <span>{user.displayName.charAt(0).toUpperCase()}</span>
                      )}
                    </div>
                    <span className="user-name">{user.displayName}</span>
                  </td>
                  <td className="email-cell">{user.email}</td>
                  <td className="role-cell">{getRoleBadge(user.role)}</td>
                  <td className="status-cell">{getStatusBadge(user.status)}</td>
                  <td className="date-cell">
                    {new Date(user.metadata.createdAt).toLocaleDateString()}
                  </td>
                  <td className="logins-cell">{user.metadata.loginCount}</td>
                  <td className="actions-cell">
                    <button
                      className="btn-action"
                      onClick={() => onViewUser?.(user)}
                      title="View"
                    >
                      👁️
                    </button>
                    <button
                      className="btn-action"
                      onClick={() => {
                        setSelectedUserForRole(user);
                        setNewRole(user.role);
                        setShowRoleModal(true);
                      }}
                      title="Change Role"
                    >
                      👤
                    </button>
                    {user.status === 'active' ? (
                      <button
                        className="btn-action"
                        onClick={() => suspendUser(user.id, 'Manual suspension')}
                        title="Suspend"
                      >
                        ⏸️
                      </button>
                    ) : (
                      <button
                        className="btn-action"
                        onClick={() => activateUser(user.id)}
                        title="Activate"
                      >
                        ▶️
                      </button>
                    )}
                    <button
                      className="btn-action danger"
                      onClick={() => {
                        if (window.confirm(`Delete user ${user.displayName}?`)) {
                          deleteUser(user.id);
                        }
                      }}
                      title="Delete"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="table-pagination">
        <div className="pagination-info">
          Showing {(currentPage - 1) * pageSize + 1} to {Math.min(currentPage * pageSize, totalUsers)} of {totalUsers}
        </div>
        <div className="pagination-controls">
          <button
            onClick={() => setPage(1)}
            disabled={currentPage === 1}
          >
            ««
          </button>
          <button
            onClick={() => setPage(currentPage - 1)}
            disabled={currentPage === 1}
          >
            «
          </button>
          
          {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
            let pageNum: number;
            if (totalPages <= 5) {
              pageNum = i + 1;
            } else if (currentPage <= 3) {
              pageNum = i + 1;
            } else if (currentPage >= totalPages - 2) {
              pageNum = totalPages - 4 + i;
            } else {
              pageNum = currentPage - 2 + i;
            }
            
            return (
              <button
                key={pageNum}
                className={currentPage === pageNum ? 'active' : ''}
                onClick={() => setPage(pageNum)}
              >
                {pageNum}
              </button>
            );
          })}
          
          <button
            onClick={() => setPage(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            »
          </button>
          <button
            onClick={() => setPage(totalPages)}
            disabled={currentPage === totalPages}
          >
            »»
          </button>
        </div>
        <div className="pagination-size">
          <select
            value={pageSize}
            onChange={(e) => setPageSize(parseInt(e.target.value))}
          >
            <option value={10}>10 per page</option>
            <option value={25}>25 per page</option>
            <option value={50}>50 per page</option>
            <option value={100}>100 per page</option>
          </select>
        </div>
      </div>

      {showRoleModal && selectedUserForRole && (
        <div className="modal-overlay" onClick={() => setShowRoleModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Change User Role</h3>
            <p>Change role for: <strong>{selectedUserForRole.displayName}</strong></p>
            <div className="role-options">
              {(['student', 'instructor', 'moderator', 'admin'] as const).map((role) => (
                <label key={role} className={`role-option ${newRole === role ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    name="role"
                    value={role}
                    checked={newRole === role}
                    onChange={() => setNewRole(role)}
                  />
                  <span className="role-name">{role.replace('_', ' ')}</span>
                  <span className="role-description">
                    {role === 'student' && 'Can access courses and learning content'}
                    {role === 'instructor' && 'Can create and manage courses'}
                    {role === 'moderator' && 'Can moderate content and users'}
                    {role === 'admin' && 'Full system access'}
                  </span>
                </label>
              ))}
            </div>
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setShowRoleModal(false)}>
                Cancel
              </button>
              <button className="btn-primary" onClick={handleRoleChange}>
                Change Role
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UserManagementTable;
