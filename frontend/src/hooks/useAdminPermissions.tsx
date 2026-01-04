/**
 * Admin Permissions Hook - Custom hook for permission-based access control
 */

import { useAdmin } from '../contexts/AdminContext';
import type { AdminPermissions } from '../contexts/AdminContext';

interface UseAdminPermissionsReturn {
  permissions: AdminPermissions | null;
  hasPermission: (permission: keyof AdminPermissions) => boolean;
  isSuperAdmin: boolean;
  canManageUsers: boolean;
  canManageContent: boolean;
  canManageQuizzes: boolean;
  canAccessAI: boolean;
  canViewAnalytics: boolean;
  canViewUserActivity: boolean;
  canViewDatabaseActivity: boolean;
  canManageCache: boolean;
  canViewAuditLogs: boolean;
  canViewAuditHistory: boolean;
  canManageSystem: boolean;
}

export const useAdminPermissions = (): UseAdminPermissionsReturn => {
  const { permissions, hasPermission } = useAdmin();

  return {
    permissions,
    hasPermission,
    isSuperAdmin: permissions?.canManageSystem ?? false,
    canManageUsers: hasPermission('canManageUsers'),
    canManageContent: hasPermission('canManageContent'),
    canManageQuizzes: hasPermission('canManageQuizzes'),
    canAccessAI: hasPermission('canAccessAI'),
    canViewAnalytics: hasPermission('canViewAnalytics'),
    canViewUserActivity: hasPermission('canViewUserActivity'),
    canViewDatabaseActivity: hasPermission('canViewDatabaseActivity'),
    canManageCache: hasPermission('canManageCache'),
    canViewAuditLogs: hasPermission('canViewAuditLogs'),
    canViewAuditHistory: hasPermission('canViewAuditHistory'),
    canManageSystem: hasPermission('canManageSystem')
  };
};

export default useAdminPermissions;
