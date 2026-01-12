/**
 * Admin Table Activity Component
 * 
 * Monitors database table activity and performance for administrators
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Database,
  Table,
  Activity,
  Server,
  HardDrive,
  Search,
  RefreshCw,
  TrendingUp,
  Clock,
  AlertCircle,
  CheckCircle,
  MoreVertical,
  ArrowUp,
  ArrowDown,
  Filter,
  Download
} from 'lucide-react';
import advancedCollaborationService from '../../services/advancedCollaborationService';
import adminApi from '../../services/adminApi';

interface TableInfo {
  tableName: string;
  rows: number;
  size: string;
  indexes: number;
  lastModified: string;
}

interface TableActivity {
  tableName: string;
  reads: number;
  writes: number;
  updates: number;
  deletes: number;
  avgQueryTime: number;
  peakConnections: number;
}

interface DatabaseStats {
  totalSize: string;
  totalTables: number;
  totalRows: number;
  activeConnections: number;
  avgQueryTime: number;
  uptime: string;
}

export const AdminTableActivity: React.FC = () => {
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [activities, setActivities] = useState<TableActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'name' | 'rows' | 'size'>('rows');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const loadTableActivity = useCallback(async () => {
    try {
      setLoading(true);
      const [statsData, tablesData, activitiesData] = await Promise.all([
        advancedCollaborationService.getDatabaseStats(),
        advancedCollaborationService.getTableInfo(),
        advancedCollaborationService.getTableActivity()
      ]);
      setStats(statsData.data);
      setTables(tablesData.data || []);
      setActivities(activitiesData.data || []);
    } catch (error) {
      console.error('Error loading table activity:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleExport = async (format: 'csv' | 'json') => {
    try {
      let response;
      if (format === 'csv') {
        response = await adminApi.exportTableActivityCsv();
      } else {
        response = await adminApi.exportTableActivityJson();
      }

      if (response.success) {
        const blob = new Blob([response.data], {
          type: format === 'csv' ? 'text/csv' : 'application/json'
        });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `table_activity_export_${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        alert('Export downloaded successfully!');
      } else {
        alert('Failed to export: ' + response.error);
      }
    } catch (err: any) {
      alert('Error: ' + err.message);
    }
  };

  useEffect(() => {
    loadTableActivity();
  }, [loadTableActivity]);

  const sortedTables = [...tables].sort((a, b) => {
    let comparison = 0;
    switch (sortBy) {
      case 'name':
        comparison = a.tableName.localeCompare(b.tableName);
        break;
      case 'rows':
        comparison = a.rows - b.rows;
        break;
      case 'size':
        comparison = parseFloat(a.size) - parseFloat(b.size);
        break;
    }
    return sortOrder === 'asc' ? comparison : -comparison;
  });

  const getActivityColor = (value: number, thresholds: { low: number; medium: number; high: number }) => {
    if (value >= thresholds.high) return 'text-red-600 bg-red-100';
    if (value >= thresholds.medium) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  if (loading && !stats) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
        <div className="animate-pulse flex items-center justify-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
          <span className="ml-3 text-gray-600">Loading database activity...</span>
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
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Database className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Table Activity</h2>
              <p className="text-sm text-gray-500">Monitor database performance and table metrics</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 flex items-center gap-2"
              onClick={() => handleExport('csv')}
              title="Export to CSV"
            >
              <Download className="w-4 h-4" />
              CSV
            </button>
            <button
              className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 flex items-center gap-2"
              onClick={() => handleExport('json')}
              title="Export to JSON"
            >
              <Download className="w-4 h-4" />
              JSON
            </button>
            <button
              onClick={loadTableActivity}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Size</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalSize}</p>
              </div>
              <HardDrive className="w-8 h-8 text-blue-300" />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Tables</p>
                <p className="text-2xl font-bold text-purple-600">{stats.totalTables}</p>
              </div>
              <Table className="w-8 h-8 text-purple-300" />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Active Connections</p>
                <p className="text-2xl font-bold text-green-600">{stats.activeConnections}</p>
              </div>
              <Server className="w-8 h-8 text-green-300" />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Avg Query Time</p>
                <p className="text-2xl font-bold text-gray-900">{stats.avgQueryTime}ms</p>
              </div>
              <Clock className="w-8 h-8 text-gray-300" />
            </div>
          </div>
        </div>
      )}

      {/* Table List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
              <Table className="w-5 h-5 text-blue-500" />
              Database Tables
            </h3>
            <div className="flex items-center gap-2">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="px-3 py-1 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="rows">Sort by Rows</option>
                <option value="size">Sort by Size</option>
                <option value="name">Sort by Name</option>
              </select>
              <button
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                {sortOrder === 'asc' ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </div>
        
        {sortedTables.length === 0 ? (
          <div className="p-8 text-center">
            <Table className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No tables found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Table Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rows
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Size
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Indexes
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Modified
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {sortedTables.map((table) => (
                  <tr key={table.tableName} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Database className="w-5 h-5 text-gray-400 mr-3" />
                        <span className="font-medium text-gray-900">{table.tableName}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {table.rows.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {table.size}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {table.indexes}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(table.lastModified).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => setSelectedTable(table.tableName)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        View Activity
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Activity by Table */}
      {activities.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-green-500" />
            Table Activity Metrics
          </h3>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {activities.map((activity) => (
              <div key={activity.tableName} className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900">{activity.tableName}</h4>
                  <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getActivityColor(activity.avgQueryTime, { low: 50, medium: 200, high: 500 })}`}>
                    {activity.avgQueryTime}ms avg
                  </span>
                </div>
                <div className="grid grid-cols-4 gap-2 text-center text-sm">
                  <div className="bg-green-100 rounded p-2">
                    <p className="font-semibold text-green-700">{activity.reads}</p>
                    <p className="text-xs text-green-600">Reads</p>
                  </div>
                  <div className="bg-blue-100 rounded p-2">
                    <p className="font-semibold text-blue-700">{activity.writes}</p>
                    <p className="text-xs text-blue-600">Writes</p>
                  </div>
                  <div className="bg-yellow-100 rounded p-2">
                    <p className="font-semibold text-yellow-700">{activity.updates}</p>
                    <p className="text-xs text-yellow-600">Updates</p>
                  </div>
                  <div className="bg-red-100 rounded p-2">
                    <p className="font-semibold text-red-700">{activity.deletes}</p>
                    <p className="text-xs text-red-600">Deletes</p>
                  </div>
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  Peak connections: {activity.peakConnections}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminTableActivity;
