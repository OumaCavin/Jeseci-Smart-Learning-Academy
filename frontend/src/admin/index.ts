/**
 * Admin Module Index - Export all admin components
 */

export { default as AdminLayout } from './AdminLayout';
export { default as AdminContext, AdminProvider, useAdmin } from '../contexts/AdminContext';
export { default as DashboardOverview } from './pages/DashboardOverview';
export { default as UserManagement } from './pages/UserManagement';
export { default as ContentManager } from './pages/ContentManager';
export { default as QuizManager } from './pages/QuizManager';
export { default as AILab } from './pages/AILab';
export { default as AnalyticsReports } from './pages/AnalyticsReports';
