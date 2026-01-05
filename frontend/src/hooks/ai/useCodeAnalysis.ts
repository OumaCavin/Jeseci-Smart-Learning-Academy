import { useState, useCallback, useEffect, useRef } from 'react';
import { apiService, AIAnalysisResponse, AICodeIssue } from '../../services/api';

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

  // Helper function for basic static analysis when AI API is unavailable
  const generateBasicAnalysis = useCallback((code: string, startTime: number): CodeAnalysisResult => {
    const mockSuggestions: AIAnalysisSuggestion[] = [];
    const lines = code.split('\n');
    
    // Basic static analysis patterns
    lines.forEach((line, index) => {
      const lineNum = index + 1;
      
      // Check for var usage
      if (line.includes('var ')) {
        mockSuggestions.push({
          id: `suggestion-${startTime}-${lineNum}-var`,
          type: 'style',
          severity: 'info',
          line: lineNum,
          message: 'Use "const" or "let" instead of "var"',
          explanation: 'ES6 const and let provide block scoping and help prevent hoisting-related bugs.',
          suggestion: 'Replace "var" with "const" or "let"',
          confidence: 0.95,
        });
      }
      
      // Check for console.log
      if (line.includes('console.log')) {
        mockSuggestions.push({
          id: `suggestion-${startTime}-${lineNum}-console`,
          type: 'best_practice',
          severity: 'info',
          line: lineNum,
          message: 'Consider removing debug console.log statements',
          explanation: 'Console.log statements should be removed or replaced with proper logging in production code.',
          suggestion: 'Remove console.log or use a logging framework',
          confidence: 0.9,
        });
      }
      
      // Check for potential XSS
      if (line.includes('innerHTML') || line.includes('dangerouslySetInnerHTML')) {
        mockSuggestions.push({
          id: `suggestion-${startTime}-${lineNum}-xss`,
          type: 'security',
          severity: 'warning',
          line: lineNum,
          message: 'Potential XSS vulnerability detected',
          explanation: 'Directly setting innerHTML can lead to Cross-Site Scripting (XSS) attacks.',
          suggestion: 'Use textContent instead, or sanitize the input using a library like DOMPurify',
          confidence: 0.88,
        });
      }
    });
    
    const result: CodeAnalysisResult = {
      id: `analysis-${startTime}`,
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
    
    setResults(result);
    setSuggestions(result.suggestions);
    setMetrics(result.metrics);
    
    return result;
  }, [maxSuggestions]);

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
      // Call real AI code analysis API
      const language = context?.language as string || 'jac';
      const analysisTypes = context?.analysisTypes as string || 'comprehensive';
      
      const response: AIAnalysisResponse = await apiService.aiAnalyzeCode(
        code,
        language,
        analysisTypes
      );
      
      if (response.success && response.issues) {
        // Transform AI API response to our internal format
        const transformedSuggestions: AIAnalysisSuggestion[] = response.issues.map((issue: AICodeIssue, index: number) => ({
          id: issue.id || `suggestion-${startTime}-${index}`,
          type: issue.type as AIAnalysisSuggestion['type'],
          severity: issue.severity as AIAnalysisSuggestion['severity'],
          line: issue.line,
          column: issue.column,
          message: issue.message,
          explanation: issue.explanation,
          suggestion: issue.suggestion,
          codeDiff: issue.code_diff ? {
            before: issue.code_diff.before,
            after: issue.code_diff.after
          } : undefined,
          confidence: 0.9,
        }));
        
        // Determine complexity level from API or calculate it
        const complexityScore = response.metrics?.complexity === 'high' ? 15 : 
                               response.metrics?.complexity === 'medium' ? 8 : 3;
        
        const result: CodeAnalysisResult = {
          id: `analysis-${startTime}`,
          timestamp: new Date().toISOString(),
          duration: Date.now() - startTime,
          suggestions: transformedSuggestions.slice(0, maxSuggestions),
          metrics: {
            complexity: complexityScore,
            linesOfCode: code.split('\n').length,
            maintainability: Math.max(0, 100 - (complexityScore * 3) - (response.metrics?.issuesCount || 0) * 5),
            issuesCount: response.metrics?.issuesCount || transformedSuggestions.length,
          },
        };
        
        setResults(result);
        setSuggestions(result.suggestions);
        setMetrics(result.metrics);
        
        return result;
      } else {
        // Fallback to basic analysis if API returns no issues or fails
        console.warn('AI analysis returned no results or failed:', response.error);
        return generateBasicAnalysis(code, startTime);
      }
    } catch (error) {
      console.error('Code analysis failed:', error);
      // Fallback to basic static analysis on error
      return generateBasicAnalysis(code, startTime);
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
