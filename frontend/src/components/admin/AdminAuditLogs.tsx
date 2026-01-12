/**
 * Admin Audit Logs Component
 * 
 * Displays comprehensive audit logs for system monitoring and security
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  FileText,
  Search,
  Filter,
  Download,
  Calendar,
  User,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  RefreshCw,
  ChevronRight,
  Eye,
  MoreVertical,
  Activity
} from 'lucide-react';
import advancedCollaborationService from '../../services/advancedCollaborationService';

interface AuditLogEntry {
  id: string;
  timestamp: string;
  userId: string;
  username: string;
  action: string;
  resource: string;
  resourceType: string;
  ipAddress: string;
  userAgent: string;
  status: 'success' | 'failure' | 'warning';
  details: string;
  metadata?: Record<string, any>;
}

interface AuditLogStats {
  totalEntries: number;
  entriesToday: number;
  entriesThisWeek: number;
  failuresToday: number;
  topActions: Array<{ action: string; count: number }>;
  topUsers: Array<{ username: string; count: number }>;
}

export const AdminAuditLogs: React.FC = () => {
  const [stats, setStats] = useState<AuditLogStats | null>(null);
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterAction, setFilterAction] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');
  const [selectedLog, setSelectedLog] = useState<AuditLogEntry | null>(null);
  const [exporting, setExporting] = useState<'csv' | 'json' | null>(null);
  const [exportMessage, setExportMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const loadAuditLogs = useCallback(async () => {
    try {
      setLoading(true);
      const [statsData, logsData] = await Promise.all([
        advancedCollaborationService.getAuditLogStats(),
        advancedCollaborationService.getAuditLogs({
          startDate: dateFrom || undefined,
          endDate: dateTo || undefined,
          limit: 200
        })
      ]);
      
      // Get the actual data from the response
      const stats = statsData.data || statsData;
      const logsResult = logsData.data || logsData;
      const logsArray = logsResult.logs || logsResult || [];
      
      // Calculate date-based stats
      const now = new Date();
      const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const weekStart = new Date(now);
      weekStart.setDate(weekStart.getDate() - 7);
      
      let entriesToday = 0;
      let entriesThisWeek = 0;
      let failuresToday = 0;
      
      logsArray.forEach((log: any) => {
        const logDate = new Date(log.timestamp);
        if (logDate >= todayStart) {
          entriesToday++;
          if (log.action === 'DELETE' || log.action === 'SOFT_DELETE') {
            failuresToday++;
          }
        }
        if (logDate >= weekStart) {
          entriesThisWeek++;
        }
      });
      
      // Transform API response to match component interface
      const transformedStats = {
        totalEntries: stats.totalLogs || 0,
        entriesToday,
        entriesThisWeek,
        failuresToday,
        topActions: Object.entries(stats.logsByAction || stats.logsByLevel || {}).map(([action, count]) => ({ 
          action, 
          count: count as number 
        })),
        topUsers: Object.entries(stats.logsByUser || stats.logsBySource || {}).map(([username, count]) => ({ 
          username, 
          count: count as number 
        }))
      };
      
      const transformedLogs = (logsArray || []).map((item: any) => {
        const status: AuditLogEntry['status'] = 
          item.action === 'DELETE' || item.action === 'SOFT_DELETE' ? 'failure' : 
          item.action === 'UPDATE' || item.action === 'RESTORE' ? 'warning' : 'success';
        return {
          id: item.id || item.audit_id,
          timestamp: item.timestamp,
          userId: item.performed_by_id?.toString() || 'system',
          username: item.performed_by || 'System',
          action: item.action || 'UNKNOWN',
          resource: item.record_id || item.table || 'unknown',
          resourceType: item.table || 'log',
          ipAddress: item.ip_address || '',
          userAgent: item.user_agent || '',
          status,
          details: item.action ? `${item.action} on ${item.table || 'unknown'}` : 'No details',
          metadata: {
            old_values: item.old_values,
            new_values: item.new_values,
            changed_fields: item.changed_fields,
            geolocation: item.geolocation,
            application_source: item.application_source
          }
        };
      });
      
      setStats(transformedStats);
      setLogs(transformedLogs);
    } catch (error) {
      console.error('Error loading audit logs:', error);
    } finally {
      setLoading(false);
    }
  }, [dateFrom, dateTo]);

  useEffect(() => {
    loadAuditLogs();
  }, [loadAuditLogs]);

  const handleExportLogs = async (format: 'csv' | 'json') => {
    try {
      setExporting(format);
      setExportMessage(null);

      let result;
      if (format === 'csv') {
        result = await advancedCollaborationService.getAuditLogs({
          startDate: dateFrom || undefined,
          endDate: dateTo || undefined,
          limit: 1000
        });
        
        // Create CSV content from logs
        const headers = ['ID', 'Timestamp', 'Action', 'Table', 'Record ID', 'Performed By', 'IP Address', 'Source'];
        const rows = (result.data?.logs || []).map((log: any) => [
          log.id,
          log.timestamp,
          log.action,
          log.table,
          log.record_id,
          log.performed_by,
          log.ip_address,
          log.application_source
        ]);
        
        const csvContent = [headers.join(','), ...rows.map((row: any) => row.join(','))].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `audit_logs_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      } else {
        result = await advancedCollaborationService.getAuditLogs({
          startDate: dateFrom || undefined,
          endDate: dateTo || undefined,
          limit: 1000
        });
        
        const jsonContent = JSON.stringify({
          exported_at: new Date().toISOString(),
          filters: { dateFrom, dateTo },
          total_records: result.data?.logs?.length || 0,
          logs: result.data?.logs || []
        }, null, 2);
        
        const blob = new Blob([jsonContent], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `audit_logs_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }

      setExportMessage({ 
        type: 'success', 
        text: `Audit logs exported to ${format.toUpperCase()} successfully` 
      });
    } catch (error) {
      setExportMessage({ 
        type: 'error', 
        text: `Failed to export audit logs as ${format.toUpperCase()}` 
      });
    } finally {
      setExporting(null);
      setTimeout(() => setExportMessage(null), 5000);
    }
  };

  const filteredLogs = logs.filter(log => {
    if (filterAction !== 'all' && log.action !== filterAction) return false;
    if (filterStatus !== 'all' && log.status !== filterStatus) return false;
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return log.username.toLowerCase().includes(query) ||
             log.action.toLowerCase().includes(query) ||
             log.resource.toLowerCase().includes(query) ||
             log.details.toLowerCase().includes(query);
    }
    return true;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failure': return <XCircle className="w-4 h-4 text-red-500" />;
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      default: return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };

  const getActionColor = (action: string) => {
    if (action.includes('create') || action.includes('add')) return 'bg-green-100 text-green-700';
    if (action.includes('delete') || action.includes('remove')) return 'bg-red-100 text-red-700';
    if (action.includes('update') || action.includes('edit')) return 'bg-blue-100 text-blue-700';
    if (action.includes('login') || action.includes('auth')) return 'bg-purple-100 text-purple-700';
    return 'bg-gray-100 text-gray-700';
  };

  if (loading && !stats) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
        <div className="animate-pulse flex items-center justify-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
          <span className="ml-3 text-gray-600">Loading audit logs...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-indigo-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Audit Logs</h2>
              <p className="text-sm text-gray-500">Track all system activities and changes</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={loadAuditLogs}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              title="Refresh"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
            <div className="relative group">
              <button className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                <Download className="w-4 h-4" />
                {exporting ? 'Exporting...' : 'Export Logs'}
              </button>
              {/* Dropdown menu */}
              <div className="absolute right-0 mt-1 w-32 bg-white rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10">
                <div className="py-1">
                  <button
                    onClick={() => handleExportLogs('csv')}
                    disabled={exporting !== null}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 disabled:opacity-50"
                  >
                    Export as CSV
                  </button>
                  <button
                    onClick={() => handleExportLogs('json')}
                    disabled={exporting !== null}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 disabled:opacity-50"
                  >
                    Export as JSON
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Export Message */}
      {exportMessage && (
        <div className={`p-4 rounded-lg flex items-center gap-2 ${
          exportMessage.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }`}>
          {exportMessage.type === 'success' ? <CheckCircle className="w-5 h-5" /> : <AlertTriangle className="w-5 h-5" />}
          {exportMessage.text}
        </div>
      )}

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Entries</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalEntries.toLocaleString()}</p>
              </div>
              <FileText className="w-8 h-8 text-blue-300" />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Today</p>
                <p className="text-2xl font-bold text-green-600">{stats.entriesToday.toLocaleString()}</p>
              </div>
              <Calendar className="w-8 h-8 text-green-300" />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">This Week</p>
                <p className="text-2xl font-bold text-purple-600">{stats.entriesThisWeek.toLocaleString()}</p>
              </div>
              <Clock className="w-8 h-8 text-purple-300" />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Failures Today</p>
                <p className="text-2xl font-bold text-red-600">{stats.failuresToday.toLocaleString()}</p>
              </div>
              <XCircle className="w-8 h-8 text-red-300" />
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search logs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <select
            value={filterAction}
            onChange={(e) => setFilterAction(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Actions</option>
            <option value="create">Create</option>
            <option value="update">Update</option>
            <option value="delete">Delete</option>
            <option value="login">Login</option>
            <option value="logout">Logout</option>
            <option value="view">View</option>
          </select>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Status</option>
            <option value="success">Success</option>
            <option value="failure">Failure</option>
            <option value="warning">Warning</option>
          </select>
          <input
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <span className="text-gray-400">to</span>
          <input
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Audit Logs List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b border-gray-100">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-500" />
            Audit Log Entries ({filteredLogs.length})
          </h3>
        </div>

        {filteredLogs.length === 0 ? (
          <div className="p-8 text-center">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No audit logs found</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {filteredLogs.slice(0, 100).map((log) => (
              <div
                key={log.id}
                className="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => setSelectedLog(log)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-1">
                      {getStatusIcon(log.status)}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-gray-900">{log.username}</span>
                        <span className="text-gray-500">performed</span>
                        <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getActionColor(log.action)}`}>
                          {log.action}
                        </span>
                        <span className="text-gray-500">on</span>
                        <span className="font-medium text-blue-600">{log.resourceType}:{log.resource}</span>
                      </div>
                      <p className="text-sm text-gray-600 line-clamp-1">{log.details}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {new Date(log.timestamp).toLocaleString()}
                        </span>
                        <span className="flex items-center gap-1">
                          <Activity className="w-3 h-3" />
                          {log.ipAddress}
                        </span>
                      </div>
                    </div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Log Detail Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Audit Log Details</h3>
                <button
                  onClick={() => setSelectedLog(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-4">
                <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
                  {getStatusIcon(selectedLog.status)}
                  <div>
                    <p className="font-medium text-gray-900">{selectedLog.username}</p>
                    <p className="text-sm text-gray-500">{selectedLog.userId}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Action</label>
                    <p className="mt-1">
                      <span className={`px-2 py-0.5 text-sm font-medium rounded-full ${getActionColor(selectedLog.action)}`}>
                        {selectedLog.action}
                      </span>
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Status</label>
                    <p className="mt-1 capitalize text-gray-900">{selectedLog.status}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Resource Type</label>
                    <p className="mt-1 text-gray-900">{selectedLog.resourceType}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Resource</label>
                    <p className="mt-1 text-gray-900 font-mono text-sm">{selectedLog.resource}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">IP Address</label>
                    <p className="mt-1 text-gray-900">{selectedLog.ipAddress}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Timestamp</label>
                    <p className="mt-1 text-gray-900">{new Date(selectedLog.timestamp).toLocaleString()}</p>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-500">Details</label>
                  <p className="mt-1 text-gray-900">{selectedLog.details}</p>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-500">User Agent</label>
                  <p className="mt-1 text-gray-600 text-sm font-mono bg-gray-50 p-2 rounded">{selectedLog.userAgent}</p>
                </div>

                {selectedLog.metadata && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Metadata</label>
                    <pre className="mt-1 text-xs bg-gray-50 p-3 rounded overflow-x-auto">
                      {JSON.stringify(selectedLog.metadata, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminAuditLogs;
