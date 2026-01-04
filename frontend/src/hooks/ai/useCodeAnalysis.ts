import { useState, useCallback, useEffect, useRef } from 'react';

// Type definitions for code analysis
export interface AIAnalysisSuggestion {
  id: string;
  type: 'security' | 'style' | 'logic' | 'performance' | 'bug' | 'best_practice';
  severity: 'info' | 'warning' | 'error';
  line: number;
  column?: number;
  message: string;
  explanation: string;
  suggestion?: string;
  codeDiff?: {
    before: string;
    after: string;
  };
  confidence: number;
  relatedResources?: string[];
}

export interface CodeAnalysisResult {
  id: string;
  timestamp: string;
  duration: number;
  suggestions: AIAnalysisSuggestion[];
  metrics: {
    complexity: number;
    linesOfCode: number;
    maintainability: number;
    issuesCount: number;
  };
}

export interface UseCodeAnalysisOptions {
  language: string;
  onSuggestionClick?: (suggestion: AIAnalysisSuggestion) => void;
  debounceMs?: number;
  enableAutoAnalysis?: boolean;
  maxSuggestions?: number;
}

export interface UseCodeAnalysisReturn {
  isAnalyzing: boolean;
  results: CodeAnalysisResult | null;
  suggestions: AIAnalysisSuggestion[];
  metrics: CodeAnalysisResult['metrics'] | null;
  analyze: (code: string, context?: Record<string, unknown>) => Promise<CodeAnalysisResult | null>;
  applyFix: (suggestionId: string) => Promise<void>;
  dismissSuggestion: (suggestionId: string) => void;
  clearResults: () => void;
  getSuggestionsAtLine: (line: number) => AIAnalysisSuggestion[];
}

export function useCodeAnalysis(options: UseCodeAnalysisOptions): UseCodeAnalysisReturn {
  const {
    language,
    onSuggestionClick,
    debounceMs = 1000,
    enableAutoAnalysis = true,
    maxSuggestions = 10,
  } = options;

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<CodeAnalysisResult | null>(null);
  const [suggestions, setSuggestions] = useState<AIAnalysisSuggestion[]>([]);
  const [metrics, setMetrics] = useState<CodeAnalysisResult['metrics'] | null>(null);
  
  const debounceRef = useRef<NodeJS.Timeout | null>(null);
  const currentCodeRef = useRef<string>('');

  // Analyze code
  const analyze = useCallback(async (
    code: string,
    context?: Record<string, unknown>
  ): Promise<CodeAnalysisResult | null> => {
    if (!code.trim()) return null;
    
    setIsAnalyzing(true);
    currentCodeRef.current = code;
    
    const startTime = Date.now();
    
    try {
      // Simulate AI code analysis - replace with actual API call
      const response = await new Promise<CodeAnalysisResult>((resolve) => {
        setTimeout(() => {
          // Generate mock analysis results
          const mockSuggestions: AIAnalysisSuggestion[] = [];
          
          // Add some example suggestions based on code content
          if (code.includes('var ')) {
            mockSuggestions.push({
              id: `suggestion-${Date.now()}-1`,
              type: 'style',
              severity: 'info',
              line: code.split('\n').findIndex(line => line.includes('var ')) + 1,
              message: 'Use "const" or "let" instead of "var"',
              explanation: 'ES6 const and let provide block scoping and help prevent hoisting-related bugs.',
              suggestion: 'Replace "var" with "const" or "let"',
              confidence: 0.95,
            });
          }
          
          if (code.includes('console.log') && code.includes('function')) {
            mockSuggestions.push({
              id: `suggestion-${Date.now()}-2`,
              type: 'best_practice',
              severity: 'info',
              line: code.split('\n').findIndex(line => line.includes('console.log')) + 1,
              message: 'Consider removing debug console.log statements',
              explanation: 'Console.log statements should be removed or replaced with proper logging in production code.',
              suggestion: 'Remove console.log or use a logging framework',
              confidence: 0.9,
            });
          }
          
          // Check for potential security issues
          if (code.includes('innerHTML') || code.includes('dangerouslySetInnerHTML')) {
            mockSuggestions.push({
              id: `suggestion-${Date.now()}-3`,
              type: 'security',
              severity: 'warning',
              line: code.split('\n').findIndex(line => line.includes('innerHTML') || line.includes('dangerouslySetInnerHTML')) + 1,
              message: 'Potential XSS vulnerability detected',
              explanation: 'Directly setting innerHTML can lead to Cross-Site Scripting (XSS) attacks if the content is not properly sanitized.',
              suggestion: 'Use textContent instead, or sanitize the input using a library like DOMPurify',
              confidence: 0.88,
            });
          }

          const result: CodeAnalysisResult = {
            id: `analysis-${Date.now()}`,
            timestamp: new Date().toISOString(),
            duration: Date.now() - startTime,
            suggestions: mockSuggestions.slice(0, maxSuggestions),
            metrics: {
              complexity: Math.floor(Math.random() * 20) + 1,
              linesOfCode: code.split('\n').length,
              maintainability: Math.floor(Math.random() * 50) + 50,
              issuesCount: mockSuggestions.length,
            },
          };
          
          resolve(result);
        }, 800);
      });
      
      setResults(response);
      setSuggestions(response.suggestions);
      setMetrics(response.metrics);
      
      return response;
    } catch (error) {
      console.error('Code analysis failed:', error);
      return null;
    } finally {
      setIsAnalyzing(false);
    }
  }, [maxSuggestions]);

  // Apply fix for a suggestion
  const applyFix = useCallback(async (suggestionId: string) => {
    const suggestion = suggestions.find(s => s.id === suggestionId);
    if (!suggestion) return;
    
    onSuggestionClick?.(suggestion);
    
    // Remove applied suggestion from list
    setSuggestions(prev => prev.filter(s => s.id !== suggestionId));
  }, [suggestions, onSuggestionClick]);

  // Dismiss a suggestion
  const dismissSuggestion = useCallback((suggestionId: string) => {
    setSuggestions(prev => prev.filter(s => s.id !== suggestionId));
  }, []);

  // Clear all results
  const clearResults = useCallback(() => {
    setResults(null);
    setSuggestions([]);
    setMetrics(null);
  }, []);

  // Get suggestions at specific line
  const getSuggestionsAtLine = useCallback((line: number): AIAnalysisSuggestion[] => {
    return suggestions.filter(s => s.line === line);
  }, [suggestions]);

  // Debounced auto-analysis
  useEffect(() => {
    if (!enableAutoAnalysis || !currentCodeRef.current) return;
    
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }
    
    debounceRef.current = setTimeout(() => {
      analyze(currentCodeRef.current);
    }, debounceMs);
    
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [enableAutoAnalysis, debounceMs, analyze]);

  return {
    isAnalyzing,
    results,
    suggestions,
    metrics,
    analyze,
    applyFix,
    dismissSuggestion,
    clearResults,
    getSuggestionsAtLine,
  };
}

export default useCodeAnalysis;
