import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useCodeAnalysis, AIAnalysisSuggestion } from '../../hooks/ai/useCodeAnalysis';
import './AICodeAssistant.css';

interface AICodeAssistantProps {
  code: string;
  language: string;
  onApplyFix?: (suggestion: AIAnalysisSuggestion, fixedCode: string) => void;
  position?: 'sidebar' | 'floating' | 'bottom';
  isOpen?: boolean;
  onClose?: () => void;
}

export function AICodeAssistant({
  code,
  language,
  onApplyFix,
  position = 'sidebar',
  isOpen = true,
  onClose,
}: AICodeAssistantProps) {
  const [selectedSuggestion, setSelectedSuggestion] = useState<AIAnalysisSuggestion | null>(null);
  const [activeTab, setActiveTab] = useState<'suggestions' | 'chat'>('suggestions');
  const [chatMessages, setChatMessages] = useState<{ role: 'user' | 'assistant'; content: string }[]>([]);
  const [chatInput, setChatInput] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);
  
  const {
    isAnalyzing,
    suggestions,
    metrics,
    analyze,
    applyFix,
    dismissSuggestion,
    clearResults,
  } = useCodeAnalysis({
    language,
    onSuggestionClick: (suggestion) => setSelectedSuggestion(suggestion),
  });

  // Auto-analyze when code changes
  useEffect(() => {
    if (code && isOpen) {
      const debounceTimer = setTimeout(() => {
        analyze(code);
      }, 1500);
      return () => clearTimeout(debounceTimer);
    }
  }, [code, isOpen, analyze]);

  // Scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const handleApplyFix = useCallback(async (suggestion: AIAnalysisSuggestion) => {
    await applyFix(suggestion.id);
    onApplyFix?.(suggestion, suggestion.codeDiff?.after || '');
    setSelectedSuggestion(null);
  }, [applyFix, onApplyFix]);

  const handleSendMessage = useCallback(() => {
    if (!chatInput.trim()) return;
    
    setChatMessages(prev => [
      ...prev,
      { role: 'user', content: chatInput },
    ]);
    
    // Simulate AI response
    setTimeout(() => {
      setChatMessages(prev => [
        ...prev,
        { role: 'assistant', content: `I understand you're asking about "${chatInput}". Here's what I can help with...` },
      ]);
    }, 1000);
    
    setChatInput('');
  }, [chatInput]);

  const getSeverityColor = (severity: AIAnalysisSuggestion['severity']) => {
    switch (severity) {
      case 'error': return '#ef4444';
      case 'warning': return '#f59e0b';
      case 'info': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  const getTypeIcon = (type: AIAnalysisSuggestion['type']) => {
    switch (type) {
      case 'security': return '🔒';
      case 'performance': return '⚡';
      case 'bug': return '🐛';
      case 'best_practice': return '✨';
      default: return '💡';
    }
  };

  if (!isOpen) return null;

  return (
    <div className={`ai-code-assistant ${position}`}>
      <div className="ai-assistant-header">
        <div className="ai-header-title">
          <span className="ai-icon">🤖</span>
          <span>AI Code Assistant</span>
        </div>
        <div className="ai-header-actions">
          {onClose && (
            <button className="ai-close-btn" onClick={onClose}>✕</button>
          )}
        </div>
      </div>

      <div className="ai-assistant-tabs">
        <button
          className={`ai-tab ${activeTab === 'suggestions' ? 'active' : ''}`}
          onClick={() => setActiveTab('suggestions')}
        >
          Suggestions ({suggestions.length})
        </button>
        <button
          className={`ai-tab ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          Chat
        </button>
      </div>

      <div className="ai-assistant-content">
        {activeTab === 'suggestions' ? (
          <div className="ai-suggestions-panel">
            {isAnalyzing ? (
              <div className="ai-loading">
                <div className="ai-spinner"></div>
                <span>Analyzing code...</span>
              </div>
            ) : suggestions.length === 0 ? (
              <div className="ai-empty-state">
                <span className="ai-empty-icon">✨</span>
                <p>Your code looks clean!</p>
                <span className="ai-empty-hint">No issues found</span>
              </div>
            ) : (
              <>
                {metrics && (
                  <div className="ai-metrics-bar">
                    <div className="ai-metric">
                      <span className="metric-label">Complexity</span>
                      <span className="metric-value">{metrics.complexity}</span>
                    </div>
                    <div className="ai-metric">
                      <span className="metric-label">Lines</span>
                      <span className="metric-value">{metrics.linesOfCode}</span>
                    </div>
                    <div className="ai-metric">
                      <span className="metric-label">Issues</span>
                      <span className="metric-value issues">{metrics.issuesCount}</span>
                    </div>
                  </div>
                )}
                
                <div className="ai-suggestions-list">
                  {suggestions.map((suggestion) => (
                    <div
                      key={suggestion.id}
                      className={`ai-suggestion-card ${selectedSuggestion?.id === suggestion.id ? 'selected' : ''}`}
                      onClick={() => setSelectedSuggestion(suggestion)}
                    >
                      <div className="suggestion-header">
                        <span className="suggestion-icon">{getTypeIcon(suggestion.type)}</span>
                        <span
                          className="suggestion-severity"
                          style={{ backgroundColor: getSeverityColor(suggestion.severity) }}
                        >
                          {suggestion.severity}
                        </span>
                        <span className="suggestion-line">Line {suggestion.line}</span>
                      </div>
                      <p className="suggestion-message">{suggestion.message}</p>
                      {selectedSuggestion?.id === suggestion.id && (
                        <div className="suggestion-details">
                          <p className="suggestion-explanation">{suggestion.explanation}</p>
                          {suggestion.suggestion && (
                            <p className="suggestion-fix">{suggestion.suggestion}</p>
                          )}
                          <div className="suggestion-actions">
                            <button
                              className="ai-btn-primary"
                              onClick={() => handleApplyFix(suggestion)}
                            >
                              Apply Fix
                            </button>
                            <button
                              className="ai-btn-secondary"
                              onClick={() => dismissSuggestion(suggestion.id)}
                            >
                              Dismiss
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        ) : (
          <div className="ai-chat-panel">
            <div className="ai-chat-messages">
              {chatMessages.length === 0 ? (
                <div className="ai-chat-empty">
                  <span className="ai-chat-icon">💬</span>
                  <p>Ask me anything about your code</p>
                </div>
              ) : (
                chatMessages.map((message, index) => (
                  <div key={index} className={`ai-chat-message ${message.role}`}>
                    <span className="chat-role">
                      {message.role === 'user' ? 'You' : 'AI'}
                    </span>
                    <p className="chat-content">{message.content}</p>
                  </div>
                ))
              )}
              <div ref={chatEndRef} />
            </div>
            <div className="ai-chat-input">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Ask about your code..."
              />
              <button onClick={handleSendMessage} disabled={!chatInput.trim()}>
                Send
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AICodeAssistant;
