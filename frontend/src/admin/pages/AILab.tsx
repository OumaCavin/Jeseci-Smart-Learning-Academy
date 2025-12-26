/**
 * AI Lab Page - Admin interface for AI content generation
 */

import React, { useState, useEffect } from 'react';
import adminApi from '../../services/adminApi';
import { Domain, AIUsageStats } from '../../services/adminApi';
import './Admin.css';

interface AILabProps {
  activeSection: string;
}

const AILab: React.FC<AILabProps> = ({ activeSection }) => {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [stats, setStats] = useState<AIUsageStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedContent, setGeneratedContent] = useState<any>(null);

  // Generation form
  const [formData, setFormData] = useState({
    concept_name: '',
    domain: 'Jac Programming',
    difficulty: 'beginner',
    related_concepts: '',
  });

  useEffect(() => {
    if (activeSection === 'ai') {
      loadData();
    }
  }, [activeSection]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [domainsResponse, statsResponse] = await Promise.all([
        adminApi.getDomains(),
        adminApi.getAIUsageStats().catch(() => ({ success: true, stats: null })),
      ]);

      if (domainsResponse.success) {
        setDomains(domainsResponse.domains || []);
      }

      if (statsResponse.success) {
        setStats(statsResponse.stats);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load AI data');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    setError(null);
    setGeneratedContent(null);

    try {
      const response = await adminApi.generateAIContent({
        concept_name: formData.concept_name,
        domain: formData.domain,
        difficulty: formData.difficulty,
        related_concepts: formData.related_concepts
          ? formData.related_concepts.split(',').map(s => s.trim())
          : [],
      });

      if (response.success) {
        setGeneratedContent(response.content);
      } else {
        setError(response.message || 'Failed to generate content');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to generate content');
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="spinner"></div>
        <span>Loading AI Lab...</span>
      </div>
    );
  }

  return (
    <div className="ai-lab">
      {/* AI Stats */}
      <div className="stats-grid" style={{ marginBottom: '24px' }}>
        <div className="stat-card">
          <div className="stat-icon">🤖</div>
          <div className="stat-value">{stats?.total_generations || 0}</div>
          <div className="stat-label">Total Generations</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📝</div>
          <div className="stat-value">{stats?.total_tokens_used?.toLocaleString() || 0}</div>
          <div className="stat-label">Tokens Used</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-value">{Object.keys(stats?.domains_used || {}).length}</div>
          <div className="stat-label">Domains Used</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⚡</div>
          <div className="stat-value">Active</div>
          <div className="stat-label">AI Status</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Content Generator */}
        <div className="admin-card">
          <div className="admin-card-header">
            <h2>Content Generator</h2>
          </div>
          <div className="admin-card-body">
            {error && (
              <div style={{ padding: '12px', background: '#fee2e2', color: '#dc2626', borderRadius: '8px', marginBottom: '16px' }}>
                {error}
              </div>
            )}

            <form onSubmit={handleGenerate}>
              <div className="form-group">
                <label className="form-label">Concept to Generate *</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g., Object-Spatial Programming, Walker Functions, Node Relationships"
                  value={formData.concept_name}
                  onChange={(e) => setFormData(f => ({ ...f, concept_name: e.target.value }))}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Domain *</label>
                <select
                  className="form-select"
                  value={formData.domain}
                  onChange={(e) => setFormData(f => ({ ...f, domain: e.target.value }))}
                >
                  {domains.length > 0 ? (
                    domains.map((domain) => (
                      <option key={domain.id} value={domain.name}>
                        {domain.name}
                      </option>
                    ))
                  ) : (
                    <>
                      <option value="Jac Programming">Jac Programming</option>
                      <option value="Object-Spatial Programming">Object-Spatial Programming</option>
                      <option value="Graph Theory">Graph Theory</option>
                    </>
                  )}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Difficulty *</label>
                <select
                  className="form-select"
                  value={formData.difficulty}
                  onChange={(e) => setFormData(f => ({ ...f, difficulty: e.target.value }))}
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Related Concepts (comma-separated)</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g., Nodes, Edges, Walkers, Graph Traversal"
                  value={formData.related_concepts}
                  onChange={(e) => setFormData(f => ({ ...f, related_concepts: e.target.value }))}
                />
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                style={{ width: '100%' }}
                disabled={generating || !formData.concept_name}
              >
                {generating ? '🤖 Generating...' : '🚀 Generate AI Content'}
              </button>
            </form>
          </div>
        </div>

        {/* Generated Content Preview */}
        <div className="admin-card">
          <div className="admin-card-header">
            <h2>Generated Content</h2>
          </div>
          <div className="admin-card-body">
            {generatedContent ? (
              <div className="generated-content">
                <div style={{ marginBottom: '16px' }}>
                  <span className="badge badge-info" style={{ marginRight: '8px' }}>
                    {generatedContent.concept_name}
                  </span>
                  <span className={`badge ${
                    generatedContent.difficulty === 'beginner' ? 'badge-success' :
                    generatedContent.difficulty === 'intermediate' ? 'badge-warning' : 'badge-danger'
                  }`}>
                    {generatedContent.difficulty}
                  </span>
                </div>

                <div style={{ 
                  background: '#f9fafb', 
                  padding: '16px', 
                  borderRadius: '8px',
                  maxHeight: '400px',
                  overflowY: 'auto',
                  marginBottom: '16px',
                  whiteSpace: 'pre-wrap',
                  fontSize: '14px',
                  lineHeight: '1.6',
                }}>
                  {generatedContent.content}
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <strong>Related Concepts:</strong>{' '}
                  {generatedContent.related_concepts?.join(', ') || 'None'}
                </div>

                <div style={{ fontSize: '13px', color: '#6b7280' }}>
                  Generated: {new Date(generatedContent.generated_at).toLocaleString()}
                </div>

                <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
                  <button className="btn btn-primary btn-sm">Save to Library</button>
                  <button className="btn btn-secondary btn-sm">Copy Content</button>
                </div>
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">🤖</div>
                <h3>No Content Generated Yet</h3>
                <p>Fill in the form and click generate to create AI-powered learning content</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Generations */}
      {stats?.recent_generations && stats.recent_generations.length > 0 && (
        <div className="admin-card" style={{ marginTop: '24px' }}>
          <div className="admin-card-header">
            <h2>Recent Generations</h2>
          </div>
          <div className="admin-card-body" style={{ padding: 0 }}>
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Concept</th>
                  <th>Domain</th>
                  <th>Difficulty</th>
                  <th>Generated</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_generations.slice(0, 5).map((content, index) => (
                  <tr key={index}>
                    <td>{content.concept_name}</td>
                    <td><span className="badge badge-info">{content.domain}</span></td>
                    <td>
                      <span className={`badge ${
                        content.difficulty === 'beginner' ? 'badge-success' :
                        content.difficulty === 'intermediate' ? 'badge-warning' : 'badge-danger'
                      }`}>
                        {content.difficulty}
                      </span>
                    </td>
                    <td>{new Date(content.generated_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default AILab;
