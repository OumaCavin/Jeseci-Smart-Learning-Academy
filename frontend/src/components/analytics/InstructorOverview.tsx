import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { useStudentAnalytics, StudentPerformance } from '../../hooks/useAnalytics';

// Icons
const AlertIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
  </svg>
);

const CheckIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
);

const TrendingUpIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
  </svg>
);

const TrendingDownIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
  </svg>
);

const UserIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
  </svg>
);

const FilterIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
  </svg>
);

interface InstructorOverviewProps {
  cohortId?: string;
  courseId?: string;
  onStudentClick?: (student: StudentPerformance) => void;
  onViewFullList?: () => void;
}

export function InstructorOverview({
  cohortId,
  courseId,
  onStudentClick,
  onViewFullList
}: InstructorOverviewProps) {
  const {
    atRiskStudents,
    topPerformers,
    avgScore,
    avgCompletion,
    atRiskCount,
    totalStudents,
    isLoading,
    refresh,
    sortBy
  } = useStudentAnalytics({
    cohortId,
    courseId,
    autoFetch: true
  });

  const [filterLevel, setFilterLevel] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [sortField, setSortField] = useState<keyof StudentPerformance>('riskLevel');

  // Risk level colors
  const riskColors = {
    high: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    medium: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    low: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
  };

  const riskLabels = {
    high: 'At Risk',
    medium: 'Needs Attention',
    low: 'On Track'
  };

  // Filter and sort students
  const displayedStudents = useMemo(() => {
    let students = [...atRiskStudents];
    
    if (filterLevel !== 'all') {
      students = students.filter(s => s.riskLevel === filterLevel);
    }
    
    return sortBy(sortField);
  }, [atRiskStudents, filterLevel, sortBy, sortField]);

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 
                   dark:border-gray-700">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3" />
          <div className="grid grid-cols-4 gap-4">
            <div className="h-20 bg-gray-200 dark:bg-gray-700 rounded" />
            <div className="h-20 bg-gray-200 dark:bg-gray-700 rounded" />
            <div className="h-20 bg-gray-200 dark:bg-gray-700 rounded" />
            <div className="h-20 bg-gray-200 dark:bg-gray-700 rounded" />
          </div>
          <div className="space-y-2">
            <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded" />
            <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 
                 dark:border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-100 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Instructor Overview
            </h2>
            <p className="text-sm text-gray-500 mt-0.5">
              Monitor student progress and identify those needing attention
            </p>
          </div>
          
          <button
            onClick={refresh}
            className="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 
                     rounded-lg transition-colors"
            title="Refresh data"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>

        {/* Summary cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          <div className="bg-gray-50 dark:bg-gray-750 rounded-lg p-3">
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {totalStudents}
            </div>
            <div className="text-xs text-gray-500">Total Students</div>
          </div>
          
          <div className="bg-gray-50 dark:bg-gray-750 rounded-lg p-3">
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {Math.round(avgScore)}%
            </div>
            <div className="text-xs text-gray-500">Average Score</div>
          </div>
          
          <div className="bg-gray-50 dark:bg-gray-750 rounded-lg p-3">
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {Math.round(avgCompletion)}%
            </div>
            <div className="text-xs text-gray-500">Completion Rate</div>
          </div>
          
          <div className={`rounded-lg p-3 ${atRiskCount > 0 ? 'bg-red-50 dark:bg-red-900/20' : 'bg-green-50 dark:bg-green-900/20'}`}>
            <div className={`text-2xl font-bold ${atRiskCount > 0 ? 'text-red-600' : 'text-green-600'}`}>
              {atRiskCount}
            </div>
            <div className="text-xs text-gray-500">At Risk</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="px-6 py-3 border-b border-gray-100 dark:border-gray-700 bg-gray-50 
                   dark:bg-gray-750 flex items-center gap-4">
        <div className="flex items-center gap-2">
          <FilterIcon />
          <span className="text-sm text-gray-600 dark:text-gray-400">Filter:</span>
          <select
            value={filterLevel}
            onChange={(e) => setFilterLevel(e.target.value as typeof filterLevel)}
            className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option value="all">All Students</option>
            <option value="high">At Risk Only</option>
            <option value="medium">Needs Attention</option>
            <option value="low">On Track</option>
          </select>
        </div>

        <div className="flex-1" />

        {onViewFullList && (
          <button
            onClick={onViewFullList}
            className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
          >
            View Full List →
          </button>
        )}
      </div>

      {/* At-risk students section */}
      {atRiskCount > 0 && (
        <div className="px-6 py-4 bg-red-50 dark:bg-red-900/10 border-b border-red-100 
                     dark:border-red-800/30">
          <div className="flex items-center gap-2 mb-3">
            <AlertIcon />
            <h3 className="font-medium text-red-700 dark:text-red-400">
              Students Needing Attention ({atRiskStudents.length})
            </h3>
          </div>

          <div className="grid gap-3">
            {atRiskStudents.slice(0, 5).map((student) => (
              <StudentCard 
                key={student.userId} 
                student={student} 
                onClick={() => onStudentClick?.(student)}
              />
            ))}
            
            {atRiskStudents.length > 5 && (
              <button
                onClick={onViewFullList}
                className="w-full py-2 text-sm text-red-600 hover:text-red-700 
                         dark:text-red-400 border border-dashed border-red-300 
                         dark:border-red-700 rounded-lg hover:bg-red-100 
                         dark:hover:bg-red-900/20 transition-colors"
              >
                +{atRiskStudents.length - 5} more students
              </button>
            )}
          </div>
        </div>
      )}

      {/* Top performers section */}
      <div className="px-6 py-4">
        <div className="flex items-center gap-2 mb-3">
          <TrendingUpIcon />
          <h3 className="font-medium text-gray-900 dark:text-gray-100">
            Top Performers
          </h3>
        </div>

        <div className="grid gap-3">
          {topPerformers.slice(0, 5).map((student, index) => (
            <StudentCard 
              key={student.userId} 
              student={student} 
              rank={index + 1}
              onClick={() => onStudentClick?.(student)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

// Student card component
interface StudentCardProps {
  student: StudentPerformance;
  rank?: number;
  onClick?: () => void;
}

function StudentCard({ student, rank, onClick }: StudentCardProps) {
  const riskColors = {
    high: 'border-l-red-500 bg-red-50/50 dark:bg-red-900/10',
    medium: 'border-l-yellow-500 bg-yellow-50/50 dark:bg-yellow-900/10',
    low: 'border-l-green-500 bg-green-50/50 dark:bg-green-900/10'
  };

  const riskBadges = {
    high: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    medium: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    low: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
  };

  return (
    <div 
      onClick={onClick}
      className={`flex items-center gap-4 p-3 rounded-lg border-l-4 cursor-pointer 
               hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors ${riskColors[student.riskLevel]}`}
    >
      {/* Rank or avatar */}
      <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center">
        {rank ? (
          <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
            rank === 1 
              ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' 
              : rank === 2
                ? 'bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-500'
          }`}>
            {rank}
          </span>
        ) : (
          <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
            <UserIcon />
          </div>
        )}
      </div>

      {/* Student info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-900 dark:text-gray-100 truncate">
            {student.userName}
          </span>
          <span className={`px-2 py-0.5 text-xs rounded-full ${riskBadges[student.riskLevel]}`}>
            {student.riskLevel === 'high' ? 'At Risk' : 
             student.riskLevel === 'medium' ? 'Needs Help' : 'On Track'}
          </span>
        </div>
        
        <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
          <span>Score: {Math.round(student.avgScore)}%</span>
          <span>Completion: {Math.round(student.completionRate * 100)}%</span>
          <span>Last active: {formatDate(student.lastActive)}</span>
        </div>

        {/* Risk factors */}
        {student.riskFactors.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {student.riskFactors.slice(0, 2).map((factor, i) => (
              <span 
                key={i}
                className="px-1.5 py-0.5 text-xs bg-red-100 dark:bg-red-900/30 
                         text-red-600 dark:text-red-400 rounded"
              >
                {factor}
              </span>
            ))}
            {student.riskFactors.length > 2 && (
              <span className="text-xs text-gray-400">
                +{student.riskFactors.length - 2} more
              </span>
            )}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex-shrink-0">
        <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </div>
  );
}

// Format relative date
function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  return date.toLocaleDateString();
}

import React, { useState, useCallback, useMemo, useEffect } from 'react';
