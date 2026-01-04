import React, { useState, useCallback, useEffect, useRef } from 'react';

// Icons
const PlusIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
  </svg>
);

const TrashIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
);

const PlayIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const CheckIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
);

const XIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

// Test types
export type TestType = 'assertion' | 'input_output' | 'custom';

export interface TestCase {
  id: string;
  name: string;
  type: TestType;
  input?: string;
  expectedOutput: string;
  description?: string;
  points?: number;
  hidden?: boolean;
}

export interface TestSuite {
  id: string;
  name: string;
  description?: string;
  testCases: TestCase[];
  setupCode?: string;
  teardownCode?: string;
  timeout?: number;
  totalPoints?: number;
}

// Props
interface TestRunnerPanelProps {
  testSuite: TestSuite;
  onRunTests: (testSuite: TestSuite) => Promise<TestResult[]>;
  onAddTestCase?: () => void;
  onEditTestCase?: (testCase: TestCase) => void;
  onDeleteTestCase?: (testId: string) => void;
  onUpdateSuite?: (suite: TestSuite) => void;
  className?: string;
}

export interface TestResult {
  testId: string;
  passed: boolean;
  actualOutput?: string;
  expectedOutput: string;
  input?: string;
  executionTime?: number;
  error?: string;
  points?: number;
  message?: string;
}

export function TestRunnerPanel({
  testSuite,
  onRunTests,
  onAddTestCase,
  onEditTestCase,
  onDeleteTestCase,
  onUpdateSuite,
  className = ''
}: TestRunnerPanelProps) {
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<TestResult[]>([]);
  const [expandedTest, setExpandedTest] = useState<string | null>(null);
  const [showHidden, setShowHidden] = useState(false);
  const resultsRef = useRef<HTMLDivElement>(null);

  // Run all tests
  const handleRunTests = useCallback(async () => {
    setIsRunning(true);
    setResults([]);
    
    try {
      const testResults = await onRunTests(testSuite);
      setResults(testResults);
      
      // Scroll to results
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (error) {
      console.error('Failed to run tests:', error);
    } finally {
      setIsRunning(false);
    }
  }, [testSuite, onRunTests]);

  // Calculate summary
  const passedCount = results.filter(r => r.passed).length;
  const failedCount = results.filter(r => !r.passed).length;
  const totalPoints = results.reduce((sum, r) => sum + (r.points || 0), 0);
  const earnedPoints = results.filter(r => r.passed).reduce((sum, r) => sum + (r.points || 0), 0);

  // Filter visible tests
  const visibleTests = testSuite.testCases.filter(t => !t.hidden || showHidden);

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 
                   dark:border-gray-700 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700 
                    bg-gray-50 dark:bg-gray-750">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">
              {testSuite.name}
            </h3>
            {testSuite.description && (
              <span className="text-sm text-gray-500">{testSuite.description}</span>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            {/* Toggle hidden tests */}
            {testSuite.testCases.some(t => t.hidden) && (
              <button
                onClick={() => setShowHidden(!showHidden)}
                className="px-3 py-1 text-xs font-medium text-gray-500 
                         bg-gray-200 dark:bg-gray-700 rounded-lg
                         hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                {showHidden ? 'Hide Hidden' : 'Show Hidden'}
              </button>
            )}

            {/* Add test button */}
            {onAddTestCase && (
              <button
                onClick={onAddTestCase}
                className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium
                         text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/30
                         rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
              >
                <PlusIcon />
                Add Test
              </button>
            )}

            {/* Run tests button */}
            <button
              onClick={handleRunTests}
              disabled={isRunning || visibleTests.length === 0}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium
                       bg-green-600 hover:bg-green-700 text-white rounded-lg
                       disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isRunning ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <PlayIcon />
                  Run Tests
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Results summary */}
      {results.length > 0 && (
        <div ref={resultsRef} className="px-4 py-3 bg-gray-50 dark:bg-gray-750 
                                       border-b border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-green-100 dark:bg-green-900/30 rounded-full 
                              flex items-center justify-center text-green-600 dark:text-green-400">
                  <CheckIcon />
                </div>
                <span className="font-medium text-gray-900 dark:text-gray-100">
                  {passedCount} Passed
                </span>
              </div>
              
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-red-100 dark:bg-red-900/30 rounded-full 
                              flex items-center justify-center text-red-600 dark:text-red-400">
                  <XIcon />
                </div>
                <span className="font-medium text-gray-900 dark:text-gray-100">
                  {failedCount} Failed
                </span>
              </div>

              {totalPoints > 0 && (
                <div className="text-sm text-gray-500">
                  Score: <span className="font-medium text-gray-900 dark:text-gray-100">
                    {earnedPoints}/{totalPoints}
                  </span>
                </div>
              )}
            </div>
            
            <button
              onClick={() => setResults([])}
              className="text-sm text-gray-500 hover:text-gray-700 
                       dark:hover:text-gray-300 transition-colors"
            >
              Clear Results
            </button>
          </div>
        </div>
      )}

      {/* Test cases list */}
      <div className="divide-y divide-gray-100 dark:divide-gray-700">
        {visibleTests.map((testCase) => {
          const result = results.find(r => r.testId === testCase.id);
          const isExpanded = expandedTest === testCase.id;

          return (
            <div key={testCase.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 
                                            transition-colors">
              {/* Test case header */}
              <div 
                onClick={() => setExpandedTest(isExpanded ? null : testCase.id)}
                className="flex items-center gap-4 px-4 py-3 cursor-pointer"
              >
                {/* Status indicator */}
                <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0
                              ${result?.passed 
                                ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400'
                                : result?.passed === false
                                  ? 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400'
                                  : 'bg-gray-100 text-gray-400 dark:bg-gray-700 dark:text-gray-500'}`}>
                  {result?.passed ? <CheckIcon /> : result?.passed === false ? <XIcon /> : (
                    <div className="w-2 h-2 bg-current rounded-full" />
                  )}
                </div>

                {/* Test name */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900 dark:text-gray-100 truncate">
                      {testCase.name}
                    </span>
                    {testCase.hidden && (
                      <span className="px-1.5 py-0.5 text-xs bg-gray-200 dark:bg-gray-600 
                                    text-gray-600 dark:text-gray-400 rounded">
                        Hidden
                      </span>
                    )}
                    {testCase.points !== undefined && (
                      <span className="text-xs text-gray-500">
                        ({testCase.points} pts)
                      </span>
                    )}
                  </div>
                  {testCase.description && (
                    <p className="text-sm text-gray-500 truncate mt-0.5">
                      {testCase.description}
                    </p>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                  {result && (
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      result.passed 
                        ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                        : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                    }`}>
                      {result.executionTime ? `${result.executionTime}ms` : 
                       result.error ? 'Error' : 'Failed'}
                    </span>
                  )}
                  
                  <svg className={`w-5 h-5 text-gray-400 transition-transform ${
                    isExpanded ? 'rotate-180' : ''
                  }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>

              {/* Expanded details */}
              {isExpanded && (
                <div className="px-4 pb-4 ml-10 space-y-3">
                  {/* Input/Output details */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {testCase.input && (
                      <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3">
                        <div className="text-xs font-medium text-gray-500 mb-1">Input</div>
                        <pre className="text-sm font-mono text-gray-700 dark:text-gray-300 
                                      whitespace-pre-wrap break-words">
                          {testCase.input}
                        </pre>
                      </div>
                    )}
                    
                    <div className={`rounded-lg p-3 ${
                      result?.passed 
                        ? 'bg-green-50 dark:bg-green-900/20' 
                        : 'bg-gray-50 dark:bg-gray-900'
                    }`}>
                      <div className="text-xs font-medium text-gray-500 mb-1">
                        Expected Output
                      </div>
                      <pre className="text-sm font-mono text-gray-700 dark:text-gray-300 
                                    whitespace-pre-wrap break-words">
                        {testCase.expectedOutput}
                      </pre>
                    </div>
                  </div>

                  {/* Actual output (if test ran) */}
                  {result && result.actualOutput && (
                    <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
                      <div className="text-xs font-medium text-blue-600 dark:text-blue-400 mb-1">
                        Your Output
                      </div>
                      <pre className="text-sm font-mono text-gray-700 dark:text-gray-300 
                                    whitespace-pre-wrap break-words">
                        {result.actualOutput}
                      </pre>
                    </div>
                  )}

                  {/* Error message */}
                  {result?.error && (
                    <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-3">
                      <div className="text-xs font-medium text-red-600 dark:text-red-400 mb-1">
                        Error
                      </div>
                      <pre className="text-sm font-mono text-red-700 dark:text-red-300 
                                    whitespace-pre-wrap break-words">
                        {result.error}
                      </pre>
                    </div>
                  )}

                  {/* Test actions */}
                  <div className="flex items-center gap-2 pt-2">
                    {onEditTestCase && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onEditTestCase(testCase);
                        }}
                        className="px-3 py-1.5 text-xs font-medium text-gray-600 dark:text-gray-400
                                 bg-gray-100 dark:bg-gray-700 rounded-lg
                                 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                      >
                        Edit
                      </button>
                    )}
                    
                    {onDeleteTestCase && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteTestCase(testCase.id);
                        }}
                        className="px-3 py-1.5 text-xs font-medium text-red-600 dark:text-red-400
                                 bg-red-100 dark:bg-red-900/30 rounded-lg
                                 hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors"
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}

        {visibleTests.length === 0 && (
          <div className="px-4 py-8 text-center text-gray-500">
            <p>No test cases to display</p>
            {onAddTestCase && (
              <button
                onClick={onAddTestCase}
                className="mt-2 text-blue-600 hover:text-blue-700"
              >
                Add your first test case
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

import React, { useState, useCallback, useEffect, useRef } from 'react';
