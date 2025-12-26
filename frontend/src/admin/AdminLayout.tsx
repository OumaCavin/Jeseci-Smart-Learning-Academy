/**
 * Admin Layout Component - Main admin dashboard layout with sidebar
 */

import React, { useState } from 'react';
import { useAdmin } from '../../contexts/AdminContext';
import './Admin.css';

interface AdminLayoutProps {
  children: React.ReactNode;
}

const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const { adminUser, logout } = useAdmin();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activeSection, setActiveSection] = useState('dashboard');

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'users', label: 'Users', icon: '👥' },
    { id: 'content', label: 'Content', icon: '📚' },
    { id: 'quizzes', label: 'Quizzes', icon: '📝' },
    { id: 'ai', label: 'AI Lab', icon: '🤖' },
    { id: 'analytics', label: 'Analytics', icon: '📈' },
  ];

  const handleLogout = () => {
    logout();
    window.location.href = '/';
  };

  return (
    <div className="admin-layout">
      {/* Sidebar */}
      <aside className={`admin-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <div className="logo">
            <span className="logo-icon">🎓</span>
            {!sidebarCollapsed && <span className="logo-text">Jeseci Admin</span>}
          </div>
          <button 
            className="collapse-btn"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          >
            {sidebarCollapsed ? '→' : '←'}
          </button>
        </div>

        <nav className="sidebar-nav">
          {menuItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${activeSection === item.id ? 'active' : ''}`}
              onClick={() => setActiveSection(item.id)}
              title={item.label}
            >
              <span className="nav-icon">{item.icon}</span>
              {!sidebarCollapsed && <span className="nav-label">{item.label}</span>}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="admin-info">
            <span className="admin-avatar">👤</span>
            {!sidebarCollapsed && (
              <div className="admin-details">
                <span className="admin-name">{adminUser?.first_name || adminUser?.username}</span>
                <span className="admin-role">{adminUser?.admin_role || 'Admin'}</span>
              </div>
            )}
          </div>
          <button className="logout-btn" onClick={handleLogout} title="Logout">
            <span>🚪</span>
            {!sidebarCollapsed && <span>Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="admin-main">
        <header className="admin-header">
          <div className="header-left">
            <h1>{menuItems.find(m => m.id === activeSection)?.label || 'Admin Panel'}</h1>
            <span className="breadcrumb">Jeseci Smart Learning Academy</span>
          </div>
          <div className="header-right">
            <span className="admin-badge">{adminUser?.admin_role || 'Administrator'}</span>
          </div>
        </header>

        <div className="admin-content">
          {React.Children.map(children, (child) => {
            if (React.isValidElement(child)) {
              return React.cloneElement(child as React.ReactElement<any>, { activeSection });
            }
            return child;
          })}
        </div>
      </main>
    </div>
  );
};

export default AdminLayout;
