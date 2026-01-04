import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useCodeExecution } from '../../hooks/useCodeExecution';
import { ExecutionRequest, ExecutionResponse, TestResult } from '../../contexts/CodeExecutionContext';

// Icons
const PlayIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const StopIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
  </svg>
);

const RefreshIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
  </svg>
);

const CheckCircleIcon = () => (
  <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const XCircleIcon = () => (
  <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

interface DebugConsoleProps {
  code: string;
  language: string;
  height?: string;
  showTestPanel?: boolean;
  stdin?: string;
  onExecutionComplete?: (result: ExecutionResponse) => void;
}

export function DebugConsole({
  code,
  language,
  height = '400px',
  showTestPanel = false,
  stdin = '',
  onExecutionComplete
}: DebugConsoleProps) {
  const [activeTab, setActiveTab] = useState<'output' | 'tests' | 'stdin'>('output');
  const [stdinValue, setStdinValue] = useState(stdin);
  const [selectedLanguage, setSelectedLanguage] = useState(language);
  
  const {
    isExecuting,
    currentSession,
    executionHistory,
    currentResult,
    resultStream,
    execute,
    executeStream,
    cancelExecution,
    clearHistory,
    clearCurrentResult
  } = useCodeExecution({
    onSuccess: (result) => onExecutionComplete?.(result),
    onError: (error) => console.error('Execution error:', error),
    onStream: (chunk) => {
      // Handle streaming output
    }
  });

  // Available languages
  const languages = [
    { id: 'python', name: 'Python' },
    { id: 'javascript', name: 'JavaScript' },
    { id: 'typescript', name: 'TypeScript' },
    { id: 'java', name: 'Java' },
    { id: 'cpp', name: 'C++' },
    { id: 'c', name: 'C' },
    { id: 'rust', name: 'Rust' },
    { id: 'go', name: 'Go' },
    { id: 'ruby', name: 'Ruby' }
  ];

  // Run code
  const handleRun = useCallback(async () => {
    clearCurrentResult();
    setActiveTab('output');
    
    const request: ExecutionRequest = {
      code,
      language: selectedLanguage,
      stdin: stdinValue,
      timeout: 30000
    };

    // Use streaming if available
    if (resultStream.length === 0) {
      await execute(request);
    } else {
      executeStream(request);
    }
  }, [code, selectedLanguage, stdinValue, execute, executeStream, clearCurrentResult, resultStream]);

  // Handle keyboard shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === 'Enter') {
          e.preventDefault();
          if (!isExecuting) {
            handleRun();
          }
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleRun, isExecuting]);

  // Render test results
  const renderTestResults = () => {
    if (!currentResult?.testResults) {
      return (
        <div className="flex items-center justify-center h-full text-gray-500">
          No test results available
        </div>
      );
    }

    return (
      <div className="space-y-2">
        {currentResult.testResults.map((test, index) => (
          <div
            key={index}
            className={`flex items-center gap-3 p-3 rounded-lg ${
              test.passed ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-red-900/20'
            }`}
          >
            {test.passed ? <CheckCircleIcon /> : <XCircleIcon />}
            <div className="flex-1">
              <div className="font-medium">{test.name}</div>
              {!test.passed && test.message && (
                <div className="text-sm text-red-600 dark:text-red-400 mt-1">
                  {test.message}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Render output
  const renderOutput = () => {
    if (resultStream.length > 0) {
      return (
        <div className="font-mono text-sm whitespace-pre-wrap break-words">
          {resultStream.join('')}
        </div>
      );
    }

    if (!currentResult && !isExecuting) {
      return (
        <div className="flex items-center justify-center h-full text-gray-500">
          <div className="text-center">
            <div className="mb-2">Click "Run" to execute your code</div>
            <div className="text-sm opacity-75">Press Ctrl+Enter to run</div>
          </div>
        </div>
      );
    }

    if (currentResult) {
      return (
        <div className="font-mono text-sm">
          {currentResult.output && (
            <div className="mb-4 whitespace-pre-wrap break-words">{currentResult.output}</div>
          )}
          
          {currentResult.executionTime !== undefined && (
            <div className="text-xs text-gray-500 mb-2">
              Execution time: {currentResult.executionTime}ms
            </div>
          )}
          
          {currentResult.memoryUsed !== undefined && (
            <div className="text-xs text-gray-500 mb-2">
              Memory used: {currentResult.memoryUsed}KB
            </div>
          )}
          
          {currentResult.error && (
            <div className="text-red-600 dark:text-red-400 whitespace-pre-wrap break-words">
              Error: {currentResult.error}
            </div>
          )}
        </div>
      );
    }

    if (isExecuting) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-500">Executing...</span>
        </div>
      );
    }

    return null;
  };

  return (
    <div 
      className="flex flex-col bg-white dark:bg-gray-800 rounded-lg shadow-lg"
      style={{ height }}
    >
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-4">
          {/* Language selector */}
          <select
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={isExecuting}
          >
            {languages.map((lang) => (
              <option key={lang.id} value={lang.id}>
                {lang.name}
              </option>
            ))}
          </select>

          {/* Run button */}
          <button
            onClick={handleRun}
            disabled={isExecuting || !code.trim()}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-md text-sm font-medium
                      transition-colors ${
              isExecuting
                ? 'bg-gray-300 dark:bg-gray-600 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 text-white'
            }`}
          >
            {isExecuting ? (
              <>
                <StopIcon />
                Running...
              </>
            ) : (
              <>
                <PlayIcon />
                Run
              </>
            )}
          </button>

          {/* Cancel button */}
          {isExecuting && (
            <button
              onClick={cancelExecution}
              className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium
                       bg-red-100 hover:bg-red-200 dark:bg-red-900/30 dark:hover:bg-red-900/50
                       text-red-700 dark:text-red-400 rounded-md transition-colors"
            >
              Cancel
            </button>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Clear output */}
          <button
            onClick={clearCurrentResult}
            className="p-1.5 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300
                     rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            title="Clear output"
          >
            <RefreshIcon />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-700">
        {['output', 'tests', 'stdin'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as 'output' | 'tests' | 'stdin')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
            {tab === 'output' && resultStream.length > 0 && (
              <span className="ml-2 px-1.5 py-0.5 text-xs bg-blue-100 dark:bg-blue-900/30 
                             text-blue-600 dark:text-blue-400 rounded-full">
                Live
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4 bg-gray-50 dark:bg-gray-900">
        {activeTab === 'output' && renderOutput()}
        {activeTab === 'tests' && showTestPanel && renderTestResults()}
        {activeTab === 'stdin' && (
          <div className="h-full">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Standard Input
            </label>
            <textarea
              value={stdinValue}
              onChange={(e) => setStdinValue(e.target.value)}
              placeholder="Enter input for stdin..."
              className="w-full h-32 px-3 py-2 font-mono text-sm border border-gray-300 
                       dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800
                       text-gray-900 dark:text-gray-100
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
            />
          </div>
        )}
      </div>

      {/* Status bar */}
      <div className="flex items-center justify-between px-4 py-2 border-t border-gray-200 dark:border-gray-700
                    bg-gray-100 dark:bg-gray-800 text-xs text-gray-500">
        <div className="flex items-center gap-4">
          {currentSession && (
            <span>Session: {currentSession.id.slice(-8)}</span>
          )}
          {currentResult?.executionTime !== undefined && (
            <span>Time: {currentResult.executionTime}ms</span>
          )}
          {currentResult?.memoryUsed !== undefined && (
            <span>Memory: {(currentResult.memoryUsed / 1024).toFixed(2)}MB</span>
          )}
        </div>
        
        <div className="flex items-center gap-4">
          {executionHistory.length > 0 && (
            <span>History: {executionHistory.length} executions</span>
          )}
          <span>
            {currentResult?.success === false ? (
              <span className="text-red-500">Failed</span>
            ) : currentResult?.success ? (
              <span className="text-green-500">Success</span>
            ) : (
              <span className="text-gray-400">Ready</span>
            )}
          </span>
        </div>
      </div>
    </div>
  );
}

import React, { useState, useCallback, useRef, useEffect } from 'react';
