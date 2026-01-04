import React, { useState, useCallback } from 'react';
import { useLMSIntegration } from '../../hooks/useLMSIntegration';
import { LMSStudent, RosterMapping, LMSCourse } from '../../contexts/LMSIntegrationContext';

// Icons
const SearchIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
  </svg>
);

const RefreshIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
  </svg>
);

const CheckIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
);

const UserIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
  </svg>
);

const ExclamationIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
  </svg>
);

const LinkIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
  </svg>
);

const UploadIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
  </svg>
);

interface RosterSyncDashboardProps {
  courseId?: string;
  onStudentSelect?: (student: LMSStudent) => void;
  onMappingSave?: (mappings: RosterMapping[]) => void;
}

export function RosterSyncDashboard({
  courseId,
  onStudentSelect,
  onMappingSave
}: RosterSyncDashboardProps) {
  const {
    students,
    rosterMappings,
    isLoadingStudents,
    fetchStudents,
    syncRoster,
    updateRosterMappings,
    importStudents,
    isSyncing,
    syncProgress
  } = useLMSIntegration();

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'matched' | 'unmatched' | 'conflict'>('all');
  const [selectedStudents, setSelectedStudents] = useState<Set<string>>(new Set());
  const [showImportConfirm, setShowImportConfirm] = useState(false);

  // Filter students
  const filteredStudents = students.filter(student => {
    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const matchesSearch = 
        student.firstName.toLowerCase().includes(query) ||
        student.lastName.toLowerCase().includes(query) ||
        student.email.toLowerCase().includes(query);
      if (!matchesSearch) return false;
    }

    // Status filter
    const mapping = rosterMappings.find(m => m.lmsStudentId === student.id);
    if (statusFilter !== 'all') {
      if (statusFilter === 'matched' && mapping?.status !== 'matched') return false;
      if (statusFilter === 'unmatched' && mapping?.status !== 'unmatched') return false;
      if (statusFilter === 'conflict' && mapping?.status !== 'conflict') return false;
    }

    return true;
  });

  // Get status counts
  const statusCounts = {
    matched: rosterMappings.filter(m => m.status === 'matched').length,
    unmatched: rosterMappings.filter(m => m.status === 'unmatched').length,
    conflict: rosterMappings.filter(m => m.status === 'conflict').length
  };

  // Handle student selection
  const toggleStudentSelection = useCallback((studentId: string) => {
    setSelectedStudents(prev => {
      const newSet = new Set(prev);
      if (newSet.has(studentId)) {
        newSet.delete(studentId);
      } else {
        newSet.add(studentId);
      }
      return newSet;
    });
  }, []);

  // Handle bulk import
  const handleBulkImport = useCallback(async () => {
    const studentIds = Array.from(selectedStudents);
    if (studentIds.length === 0) return;

    const result = await importStudents(studentIds);
    if (result.success > 0) {
      setSelectedStudents(new Set());
      setShowImportConfirm(false);
    }
  }, [selectedStudents, importStudents]);

  // Get status badge class
  const getStatusBadge = (status: RosterMapping['status']) => {
    const classes = {
      matched: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
      unmatched: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-400',
      conflict: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
      pending: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
    };

    const labels = {
      matched: 'Matched',
      unmatched: 'Unmatched',
      conflict: 'Conflict',
      pending: 'Pending'
    };

    return (
      <span className={`px-2 py-0.5 text-xs rounded-full ${classes[status]}`}>
        {labels[status]}
      </span>
    );
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 
                   dark:border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700 
                    bg-gray-50 dark:bg-gray-750">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">
              Roster Management
            </h3>
            <p className="text-sm text-gray-500 mt-0.5">
              Sync and manage student enrollments
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            {/* Sync roster button */}
            <button
              onClick={() => syncRoster(courseId || 'all')}
              disabled={isSyncing}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium
                       text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/30
                       rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors
                       disabled:opacity-50"
            >
              {isSyncing ? (
                <div className="w-4 h-4 border-2 border-blue-600/30 border-t-blue-600 rounded-full animate-spin" />
              ) : (
                <RefreshIcon />
              )}
              {isSyncing ? 'Syncing...' : 'Sync Roster'}
            </button>

            {/* Bulk import button */}
            {selectedStudents.size > 0 && (
              <button
                onClick={() => setShowImportConfirm(true)}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium
                         text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors"
              >
                <UploadIcon />
                Import Selected ({selectedStudents.size})
              </button>
            )}
          </div>
        </div>

        {/* Status summary */}
        <div className="flex items-center gap-4 mt-3">
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-green-500" />
            <span className="text-xs text-gray-600 dark:text-gray-400">
              {statusCounts.matched} Matched
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-gray-400" />
            <span className="text-xs text-gray-600 dark:text-gray-400">
              {statusCounts.unmatched} Unmatched
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-yellow-500" />
            <span className="text-xs text-gray-600 dark:text-gray-400">
              {statusCounts.conflict} Conflicts
            </span>
          </div>
        </div>

        {/* Search and filters */}
        <div className="flex items-center gap-3 mt-3">
          <div className="relative flex-1">
            <SearchIcon />
            <input
              type="text"
              placeholder="Search students..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 text-sm border border-gray-300 dark:border-gray-600 
                       rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as typeof statusFilter)}
            className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Status</option>
            <option value="matched">Matched</option>
            <option value="unmatched">Unmatched</option>
            <option value="conflict">Conflicts</option>
          </select>
        </div>
      </div>

      {/* Sync progress */}
      {isSyncing && syncProgress && (
        <div className="px-4 py-3 bg-blue-50 dark:bg-blue-900/20 border-b border-blue-100 
                      dark:border-blue-800">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-blue-700 dark:text-blue-300">{syncProgress.status}</span>
            <span className="text-blue-600 dark:text-blue-400">
              {syncProgress.current}/{syncProgress.total}
            </span>
          </div>
          <div className="w-full bg-blue-200 dark:bg-blue-800 rounded-full h-2">
            <div 
              className="bg-blue-600 dark:bg-blue-500 h-2 rounded-full transition-all"
              style={{ width: `${(syncProgress.current / syncProgress.total) * 100}%` }}
            />
          </div>
          {syncProgress.errors.length > 0 && (
            <div className="mt-2 text-xs text-red-600 dark:text-red-400">
              {syncProgress.errors.length} errors occurred
            </div>
          )}
        </div>
      )}

      {/* Student list */}
      <div className="overflow-auto" style={{ maxHeight: '500px' }}>
        {isLoadingStudents ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        ) : filteredStudents.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-gray-500">
            <UserIcon />
            <p className="mt-2">No students found</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100 dark:divide-gray-700">
            {filteredStudents.map((student) => {
              const mapping = rosterMappings.find(m => m.lmsStudentId === student.id);
              const isSelected = selectedStudents.has(student.id);
              const isUnmatched = !mapping || mapping.status === 'unmatched';

              return (
                <div 
                  key={student.id}
                  className={`flex items-center gap-4 px-4 py-3 hover:bg-gray-50 
                           dark:hover:bg-gray-700/50 transition-colors ${
                    isSelected ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                  }`}
                >
                  {/* Selection checkbox */}
                  {isUnmatched && (
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggleStudentSelection(student.id)}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                    />
                  )}

                  {/* Avatar */}
                  <div className="w-10 h-10 bg-gray-200 dark:bg-gray-600 rounded-full 
                                flex items-center justify-center text-gray-600 
                                dark:text-gray-400 font-medium">
                    {student.firstName[0]}{student.lastName[0]}
                  </div>

                  {/* Student info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900 dark:text-gray-100">
                        {student.firstName} {student.lastName}
                      </span>
                      {mapping && getStatusBadge(mapping.status)}
                    </div>
                    <div className="text-sm text-gray-500 truncate">
                      {student.email}
                    </div>
                    {mapping?.localUserId && (
                      <div className="text-xs text-gray-400 flex items-center gap-1 mt-0.5">
                        <LinkIcon />
                        Linked to user {mapping.localUserId.slice(-6)}
                      </div>
                    )}
                  </div>

                  {/* Enrollment status */}
                  <div className={`px-2 py-1 text-xs rounded-full ${
                    student.enrollmentStatus === 'enrolled'
                      ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                  }`}>
                    {student.enrollmentStatus}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-1">
                    {isUnmatched && (
                      <button
                        onClick={() => onStudentSelect?.(student)}
                        className="p-1.5 text-blue-600 hover:bg-blue-100 
                                 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
                        title="Match to user"
                      >
                        <LinkIcon />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-gray-100 dark:border-gray-700 
                    bg-gray-50 dark:bg-gray-750 text-sm text-gray-500">
        Showing {filteredStudents.length} of {students.length} students
      </div>

      {/* Import confirmation modal */}
      {showImportConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-md w-full mx-4">
            <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
              Confirm Import
            </h4>
            <p className="text-gray-500 mb-6">
              You are about to import {selectedStudents.size} students. 
              New user accounts will be created for unmatched students.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowImportConfirm(false)}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 
                         dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleBulkImport}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white 
                         rounded-lg transition-colors"
              >
                Import Students
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

import React, { useState, useCallback } from 'react';
