import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

// Type definitions for AI features
export interface AIAnalysisResult {
  id: string;
  suggestion: string;
  confidence: number;
  line: number;
  type: 'security' | 'style' | 'logic' | 'performance' | 'bug';
  explanation: string;
  diff?: {
    before: string;
    after: string;
  };
  relatedResources?: string[];
  timestamp: string;
}

export interface AICodeSnippet {
  code: string;
  language: string;
  startLine: number;
  endLine: number;
}

export interface AIConversation {
  id: string;
  messages: AIMessage[];
  context: {
    fileId?: string;
    functionName?: string;
    errorMessage?: string;
  };
  createdAt: string;
  updatedAt: string;
}

export interface AIMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  codeReferences?: AICodeSnippet[];
  timestamp: string;
}

export interface AITokenUsage {
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
  resetAt: string;
}

export interface AIFeatureConfig {
  enableSuggestions: boolean;
  enableAutoFix: boolean;
  enableExplanations: boolean;
  maxSuggestionsPerFile: number;
  suggestionDelay: number;
}

export interface AIContextType {
  // State
  isAnalyzing: boolean;
  currentAnalysis: AIAnalysisResult | null;
  analysisHistory: AIAnalysisResult[];
  conversations: AIConversation[];
  activeConversation: AIConversation | null;
  tokenUsage: AITokenUsage | null;
  config: AIFeatureConfig;
  recentSuggestions: AIAnalysisResult[];
  
  // Actions
  analyzeCode: (code: string, language: string, context?: Record<string, unknown>) => Promise<AIAnalysisResult[]>;
  getSuggestions: (lineNumber: number) => AIAnalysisResult[];
  applySuggestion: (analysisId: string) => Promise<void>;
  dismissSuggestion: (analysisId: string) => void;
  createConversation: (context?: Record<string, unknown>) => AIConversation;
  sendMessage: (conversationId: string, message: string) => Promise<AIMessage>;
  loadConversation: (conversationId: string) => void;
  updateConfig: (config: Partial<AIFeatureConfig>) => void;
  clearAnalysis: () => void;
  clearHistory: () => void;
}

const AIContext = createContext<AIContextType | undefined>(undefined);

export function AIProvider({ children }: { children: ReactNode }) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentAnalysis, setCurrentAnalysis] = useState<AIAnalysisResult | null>(null);
  const [analysisHistory, setAnalysisHistory] = useState<AIAnalysisResult[]>([]);
  const [conversations, setConversations] = useState<AIConversation[]>([]);
  const [activeConversation, setActiveConversation] = useState<AIConversation | null>(null);
  const [tokenUsage, setTokenUsage] = useState<AITokenUsage | null>(null);
  const [config, setConfig] = useState<AIFeatureConfig>({
    enableSuggestions: true,
    enableAutoFix: true,
    enableExplanations: true,
    maxSuggestionsPerFile: 5,
    suggestionDelay: 500,
  });
  const [recentSuggestions, setRecentSuggestions] = useState<AIAnalysisResult[]>([]);
  
  const { sendMessage, isConnected } = useWebSocket({
    url: `${process.env.REACT_APP_WS_URL || 'ws://localhost:3001'}/ai`,
    autoConnect: false,
  });

  // Analyze code with AI
  const analyzeCode = useCallback(async (
    code: string,
    language: string,
    context?: Record<string, unknown>
  ): Promise<AIAnalysisResult[]> => {
    setIsAnalyzing(true);
    
    try {
      // Simulate API call - replace with actual API integration
      const response = await new Promise<AIAnalysisResult[]>((resolve) => {
        setTimeout(() => {
          const mockResults: AIAnalysisResult[] = [
            {
              id: `analysis-${Date.now()}-1`,
              suggestion: 'Consider using const instead of let for variables that are not reassigned.',
              confidence: 0.95,
              line: 3,
              type: 'style',
              explanation: 'Using const helps prevent accidental reassignment and makes the code intent clearer.',
              timestamp: new Date().toISOString(),
            },
            {
              id: `analysis-${Date.now()}-2`,
              suggestion: 'This loop could be optimized using map() or reduce().',
              confidence: 0.88,
              line: 7,
              type: 'performance',
              explanation: 'Array methods are often more performant and easier to read than traditional for loops.',
              timestamp: new Date().toISOString(),
            },
          ];
          resolve(mockResults);
        }, 1000);
      });

      const results = response.filter(r => r.confidence >= 0.8);
      
      setCurrentAnalysis(results[0] || null);
      setAnalysisHistory(prev => [...results, ...prev].slice(0, 100));
      setRecentSuggestions(prev => [...results, ...prev].slice(0, config.maxSuggestionsPerFile));
      
      // Emit analysis completion event
      emit?.('ai:analysis:complete', { results, language });
      
      return results;
    } catch (error) {
      console.error('AI analysis failed:', error);
      throw error;
    } finally {
      setIsAnalyzing(false);
    }
  }, [config.maxSuggestionsPerFile, emit]);

  // Get suggestions for a specific line
  const getSuggestions = useCallback((lineNumber: number): AIAnalysisResult[] => {
    return analysisHistory.filter(
      result => result.line === lineNumber && !recentSuggestions.find(s => s.id === result.id)
    );
  }, [analysisHistory, recentSuggestions]);

  // Apply a suggestion to the code
  const applySuggestion = useCallback(async (analysisId: string): Promise<void> => {
    const suggestion = recentSuggestions.find(s => s.id === analysisId);
    if (!suggestion) {
      throw new Error('Suggestion not found');
    }

    // Emit event for editor to handle the fix
    emit?.('ai:suggestion:apply', { analysisId, suggestion });
    
    // Remove from recent suggestions
    setRecentSuggestions(prev => prev.filter(s => s.id !== analysisId));
  }, [recentSuggestions, emit]);

  // Dismiss a suggestion
  const dismissSuggestion = useCallback((analysisId: string) => {
    setRecentSuggestions(prev => prev.filter(s => s.id !== analysisId));
    setAnalysisHistory(prev => prev.filter(s => s.id !== analysisId));
  }, []);

  // Create a new conversation
  const createConversation = useCallback((context?: Record<string, unknown>): AIConversation => {
    const newConversation: AIConversation = {
      id: `conv-${Date.now()}`,
      messages: [],
      context: context || {},
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    
    setConversations(prev => [...prev, newConversation]);
    setActiveConversation(newConversation);
    
    return newConversation;
  }, []);

  // Send a message in a conversation
  const sendMessage = useCallback(async (
    conversationId: string,
    message: string
  ): Promise<AIMessage> => {
    const userMessage: AIMessage = {
      id: `msg-${Date.now()}-user`,
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };

    const conversation = conversations.find(c => c.id === conversationId);
    if (!conversation) {
      throw new Error('Conversation not found');
    }

    // Update conversation with user message
    const updatedConversation = {
      ...conversation,
      messages: [...conversation.messages, userMessage],
      updatedAt: new Date().toISOString(),
    };
    
    setConversations(prev => prev.map(c => 
      c.id === conversationId ? updatedConversation : c
    ));

    // Simulate AI response
    const aiResponse: AIMessage = {
      id: `msg-${Date.now()}-assistant`,
      role: 'assistant',
      content: `I understand you're asking about: "${message}". Let me help you with that.`,
      timestamp: new Date().toISOString(),
    };

    // Update conversation with AI response
    const finalConversation = {
      ...updatedConversation,
      messages: [...updatedConversation.messages, aiResponse],
    };
    
    setConversations(prev => prev.map(c => 
      c.id === conversationId ? finalConversation : c
    ));
    
    if (activeConversation?.id === conversationId) {
      setActiveConversation(finalConversation);
    }

    return aiResponse;
  }, [conversations, activeConversation]);

  // Load a specific conversation
  const loadConversation = useCallback((conversationId: string) => {
    const conversation = conversations.find(c => c.id === conversationId);
    if (conversation) {
      setActiveConversation(conversation);
    }
  }, [conversations]);

  // Update configuration
  const updateConfig = useCallback((newConfig: Partial<AIFeatureConfig>) => {
    setConfig(prev => ({ ...prev, ...newConfig }));
  }, []);

  // Clear current analysis
  const clearAnalysis = useCallback(() => {
    setCurrentAnalysis(null);
  }, []);

  // Clear analysis history
  const clearHistory = useCallback(() => {
    setAnalysisHistory([]);
    setRecentSuggestions([]);
    setCurrentAnalysis(null);
  }, []);

  // Listen for real-time AI events
  useEffect(() => {
    if (!isConnected) return;

    const handleTokenUpdate = (data: AITokenUsage) => {
      setTokenUsage(data);
    };

    const handleNewSuggestion = (data: AIAnalysisResult) => {
      setRecentSuggestions(prev => [data, ...prev].slice(0, config.maxSuggestionsPerFile));
    };

    on?.('ai:token:usage', handleTokenUpdate);
    on?.('ai:suggestion:new', handleNewSuggestion);

    return () => {
      off?.('ai:token:usage', handleTokenUpdate);
      off?.('ai:suggestion:new', handleNewSuggestion);
    };
  }, [isConnected, on, off, config.maxSuggestionsPerFile]);

  const value: AIContextType = {
    isAnalyzing,
    currentAnalysis,
    analysisHistory,
    conversations,
    activeConversation,
    tokenUsage,
    config,
    recentSuggestions,
    analyzeCode,
    getSuggestions,
    applySuggestion,
    dismissSuggestion,
    createConversation,
    sendMessage,
    loadConversation,
    updateConfig,
    clearAnalysis,
    clearHistory,
  };

  return (
    <AIContext.Provider value={value}>
      {children}
    </AIContext.Provider>
  );
}

export function useAI() {
  const context = useContext(AIContext);
  if (context === undefined) {
    throw new Error('useAI must be used within an AIProvider');
  }
  return context;
}

export default AIContext;
