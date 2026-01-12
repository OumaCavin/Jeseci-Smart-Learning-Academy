/**
 * Admin Cache Management Component
 * 
 * Provides interface for managing content cache and clearing cache entries
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  RefreshCw,
  Trash2,
  Database,
  HardDrive,
  CheckCircle,
  AlertCircle,
  Clock,
  Search,
  Filter,
  Settings,
  Zap,
  Server,
  Folder,
  FileText
} from 'lucide-react';
import advancedCollaborationService from '../../services/advancedCollaborationService';

interface CacheStats {
  totalSize: string;
  entryCount: number;
  hitRate: number;
  missRate: number;
  lastCleared: string;
  memoryUsage: string;
}

interface CacheEntry {
  key: string;
  type: string;
  size: string;
  createdAt: string;
  lastAccessed: string;
  hitCount: number;
}

interface CacheRegion {
  name: string;
  entryCount: number;
  size: string;
  hitRate: number;
}

export const AdminCacheManagement: React.FC = () => {
  const [stats, setStats] = useState<CacheStats | null>(null);
  const [entries, setEntries] = useState<CacheEntry[]>([]);
  const [regions, setRegions] = useState<CacheRegion[]>([]);
  const [loading, setLoading] = useState(true);
  const [clearing, setClearing] = useState(false);
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [clearMessage, setClearMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const loadCacheStats = useCallback(async () => {
    try {
      setLoading(true);
      const [statsData, entriesData, regionsData] = await Promise.all([
        advancedCollaborationService.getCacheStats(),
        advancedCollaborationService.getCacheEntries({ limit: 100 }),
        advancedCollaborationService.getCacheRegions()
      ]);
      setStats(statsData.data);
      setEntries(entriesData.data || []);
      setRegions(regionsData.data || []);
    } catch (error) {
      console.error('Error loading cache stats:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCacheStats();
  }, [loadCacheStats]);

  const handleClearCache = async (region?: string) => {
    try {
      setClearing(true);
      setShowClearConfirm(false);
      await advancedCollaborationService.clearContentCache(region);
      setClearMessage({ type: 'success', text: region ? `Cache cleared for region: ${region}` : 'All cache cleared successfully' });
      loadCacheStats();
    } catch (error) {
      setClearMessage({ type: 'error', text: 'Failed to clear cache' });
    } finally {
      setClearing(false);
      setTimeout(() => setClearMessage(null), 5000);
    }
  };

  const handleExportCacheStats = async (format: 'csv' | 'json') => {
    try {
      setExporting(format);
      setExportMessage(null);

      let result;
      if (format === 'csv') {
        result = await adminApiService.exportCacheStatsCsv();
      } else {
        result = await adminApiService.exportCacheStatsJson();
      }

      if (result.success) {
        // Create and download the file
        const blob = new Blob([result.data], { 
          type: format === 'csv' ? 'text/csv' : 'application/json' 
        });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cache_stats_${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        setExportMessage({ 
          type: 'success', 
          text: `Cache statistics exported to ${format.toUpperCase()} successfully` 
        });
      } else {
        setExportMessage({ 
          type: 'error', 
          text: result.error || `Failed to export cache statistics as ${format.toUpperCase()}` 
        });
      }
    } catch (error) {
      setExportMessage({ 
        type: 'error', 
        text: `Failed to export cache statistics as ${format.toUpperCase()}` 
      });
    } finally {
      setExporting(null);
      setTimeout(() => setExportMessage(null), 5000);
    }
  };

  const filteredEntries = entries.filter(entry => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return entry.key.toLowerCase().includes(query) || entry.type.toLowerCase().includes(query);
    }
    return true;
  });

  if (loading && !stats) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
        <div className="animate-pulse flex items-center justify-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
          <span className="ml-3 text-gray-600">Loading cache statistics...</span>
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
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <HardDrive className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Cache Management</h2>
              <p className="text-sm text-gray-500">Monitor and manage content cache</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={loadCacheStats}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              title="Refresh"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
            <button
              onClick={() => setShowClearConfirm(true)}
              disabled={clearing}
              className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors disabled:opacity-50"
            >
              <Trash2 className="w-4 h-4" />
              {clearing ? 'Clearing...' : 'Clear All Cache'}
            </button>
            <button
              onClick={() => handleExportCacheStats('csv')}
              disabled={exporting !== null}
              className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50"
              title="Export as CSV"
            >
              <Download className="w-4 h-4" />
              {exporting === 'csv' ? 'Exporting...' : 'Export CSV'}
            </button>
            <button
              onClick={() => handleExportCacheStats('json')}
              disabled={exporting !== null}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
              title="Export as JSON"
            >
              <Download className="w-4 h-4" />
              {exporting === 'json' ? 'Exporting...' : 'Export JSON'}
            </button>
          </div>
        </div>
      </div>

      {/* Clear Message */}
      {clearMessage && (
        <div className={`p-4 rounded-lg flex items-center gap-2 ${
          clearMessage.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }`}>
          {clearMessage.type === 'success' ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
          {clearMessage.text}
        </div>
      )}

      {/* Export Message */}
      {exportMessage && (
        <div className={`p-4 rounded-lg flex items-center gap-2 ${
          exportMessage.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }`}>
          {exportMessage.type === 'success' ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
          {exportMessage.text}
        </div>
      )}

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Size</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalSize}</p>
              </div>
              <Database className="w-8 h-8 text-blue-300" />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Entries</p>
                <p className="text-2xl font-bold text-purple-600">{stats.entryCount.toLocaleString()}</p>
              </div>
              <Folder className="w-8 h-8 text-purple-300" />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Hit Rate</p>
                <p className="text-2xl font-bold text-green-600">{stats.hitRate}%</p>
              </div>
              <Zap className="w-8 h-8 text-green-300" />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Last Cleared</p>
                <p className="text-2xl font-bold text-gray-900">{new Date(stats.lastCleared).toLocaleDateString()}</p>
              </div>
              <Clock className="w-8 h-8 text-gray-300" />
            </div>
          </div>
        </div>
      )}

      {/* Cache Regions */}
      {regions.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Server className="w-5 h-5 text-blue-500" />
            Cache Regions
          </h3>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {regions.map((region) => (
              <div key={region.name} className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900">{region.name}</h4>
                  <button
                    onClick={() => handleClearCache(region.name)}
                    disabled={clearing}
                    className="text-xs px-2 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
                  >
                    Clear
                  </button>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Entries</span>
                    <span className="font-medium">{region.entryCount.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Size</span>
                    <span className="font-medium">{region.size}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Hit Rate</span>
                    <span className={`font-medium ${region.hitRate > 80 ? 'text-green-600' : region.hitRate > 50 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {region.hitRate}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Cache Entries */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="p-4 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
              <FileText className="w-5 h-5 text-purple-500" />
              Recent Cache Entries
            </h3>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search entries..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {filteredEntries.length === 0 ? (
          <div className="p-8 text-center">
            <Database className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No cache entries found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Key
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Size
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Accessed
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Hit Count
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredEntries.map((entry) => (
                  <tr key={entry.key} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <Database className="w-4 h-4 text-gray-400 mr-2" />
                        <span className="text-sm font-mono text-gray-900 truncate max-w-xs" title={entry.key}>
                          {entry.key}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-700">
                        {entry.type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {entry.size}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(entry.createdAt).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(entry.lastAccessed).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        entry.hitCount > 100 ? 'bg-green-100 text-green-700' :
                        entry.hitCount > 10 ? 'bg-yellow-100 text-yellow-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {entry.hitCount}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Clear Cache Confirmation Modal */}
      {showClearConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                  <AlertCircle className="w-6 h-6 text-red-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Clear All Cache?</h3>
                  <p className="text-sm text-gray-500">This action cannot be undone.</p>
                </div>
              </div>
              <p className="text-gray-600 mb-6">
                This will clear all cached content across all regions. Users may experience slower load times as content is re-cached.
              </p>
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowClearConfirm(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleClearCache()}
                  disabled={clearing}
                  className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors disabled:opacity-50"
                >
                  {clearing ? 'Clearing...' : 'Clear Cache'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminCacheManagement;
