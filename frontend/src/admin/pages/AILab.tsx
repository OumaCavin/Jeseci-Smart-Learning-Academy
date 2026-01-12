/**
 * AI Lab Page - Admin interface for AI content generation and management
 */

import React, { useState, useEffect } from 'react';
import adminApi from '../../services/adminApi';
import { Domain, AIUsageStats, AIGeneratedContentAdmin } from '../../services/adminApi';
import '../Admin.css';

interface AILabProps {
  activeSection: string;
}

type ViewMode = 'active' | 'deleted';

const AILab: React.FC<AILabProps> = ({ activeSection }) => {
  const [viewMode, setViewMode] = useState<ViewMode>('active');
  const [domains, setDomains] = useState<Domain[]>([]);
  const [stats, setStats] = useState<AIUsageStats | null>(null);
  const [aiContent, setAiContent] = useState<AIGeneratedContentAdmin[]>([]);
  const [deletedContent, setDeletedContent] = useState<AIGeneratedContentAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedContent, setGeneratedContent] = useState<any>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{ id: string; name: string } | null>(null);

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
  }, [activeSection, viewMode]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [domainsResponse, statsResponse, contentResponse] = await Promise.all([
        adminApi.getDomains(),
        adminApi.getAIUsageStats().catch(() => ({ success: true, stats: null })),
        adminApi.generateAIContent({ concept_name: 'all' }).catch(() => ({ success: true, content: [] })),
      ]);

      if (domainsResponse.success) {
        setDomains(domainsResponse.domains || []);
      }

      if (statsResponse.success) {
        setStats(statsResponse.stats);
      }

      if (contentResponse.success) {
        setAiContent(contentResponse.content || []);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load AI data');
    } finally {
      setLoading(false);
    }
  };

  const loadDeletedContent = async () => {
    try {
      const response = await adminApi.getDeletedAIContent();
      if (response.success) {
        setDeletedContent(response.content || []);
      }
    } catch (err: any) {
      console.error('Error loading deleted content:', err);
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
        // Refresh content list
        loadData();
      } else {
        setError(response.message || 'Failed to generate content');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to generate content');
    } finally {
      setGenerating(false);
    }
  };

  const handleDelete = (contentId: string, conceptName: string) => {
    setDeleteTarget({ id: contentId, name: conceptName });
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;

    try {
      const response = await adminApi.deleteAIContent(deleteTarget.id, 'admin', '127.0.0.1');
      if (response.success) {
        alert(`${deleteTarget.name} deleted successfully`);
        loadData();
        loadDeletedContent();
      } else {
        alert('Failed to delete: ' + response.message);
      }
    } catch (err: any) {
      alert('Error: ' + err.message);
    } finally {
      setShowDeleteConfirm(false);
      setDeleteTarget(null);
    }
  };

  const handleRestore = async (contentId: string, conceptName: string) => {
    try {
      const response = await adminApi.restoreAIContent(contentId, 'admin', '127.0.0.1');
      if (response.success) {
        alert(`${conceptName} restored successfully`);
        loadData();
        loadDeletedContent();
      } else {
        alert('Failed to restore: ' + response.message);
      }
    } catch (err: any) {
      alert('Error: ' + err.message);
    }
  };

  const handleExport = async (format: 'csv' | 'json') => {
    try {
      let response;
      if (format === 'csv') {
        response = await adminApi.exportAIContentCsv();
      } else {
        response = await adminApi.exportAIContentJson();
      }

      if (response.success) {
        const blob = new Blob([response.data], {
          type: format === 'csv' ? 'text/csv' : 'application/json'
        });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ai_content_export_${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        alert('Export downloaded successfully!');
      } else {
        alert('Failed to export: ' + response.error);
      }
    } catch (err: any) {
      alert('Error: ' + err.message);
    }
  };

  const getDifficultyBadge = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'badge-success';
      case 'intermediate':
        return 'badge-warning';
      case 'advanced':
        return 'badge-danger';
      default:
        return 'badge-info';
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

  const renderActiveContent = () => (
    <div className="admin-card">
      <div className="admin-card-header">
        <h2>AI Generated Content ({aiContent.length})</h2>
      </div>
      <div className="admin-card-body" style={{ padding: 0 }}>
        {aiContent.length > 0 ? (
          <table className="admin-table">
            <thead>
              <tr>
                <th>Concept Name</th>
                <th>Domain</th>
                <th>Difficulty</th>
                <th>Generated By</th>
                <th>Generated At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {aiContent.map((content) => (
                <tr key={content.content_id}>
                  <td>
                    <div>
                      <div style={{ fontWeight: '500' }}>{content.concept_name}</div>
                      <div style={{ fontSize: '13px', color: '#6b7280' }}>
                        {content.content?.substring(0, 50)}...
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className="badge badge-info">{content.domain}</span>
                  </td>
                  <td>
                    <span className={`badge ${getDifficultyBadge(content.difficulty)}`}>
                      {content.difficulty}
                    </span>
                  </td>
                  <td>{content.generated_by || 'system'}</td>
                  <td>{content.generated_at ? new Date(content.generated_at).toLocaleDateString() : 'N/A'}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button className="btn btn-sm btn-secondary">View</button>
                      <button
                        className="btn btn-sm btn-danger"
                        onClick={() => handleDelete(content.content_id, content.concept_name)}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">🤖</div>
            <h3>No AI Content Generated Yet</h3>
            <p>Use the content generator to create AI-powered learning content</p>
          </div>
        )}
      </div>
    </div>
  );

  const renderDeletedContent = () => (
    <div className="admin-card">
      <div className="admin-card-header">
        <h2>Deleted Content ({deletedContent.length})</h2>
      </div>
      <div className="admin-card-body" style={{ padding: 0 }}>
        {deletedContent.length > 0 ? (
          <table className="admin-table">
            <thead>
              <tr>
                <th>Concept Name</th>
                <th>Domain</th>
                <th>Difficulty</th>
                <th>Deleted By</th>
                <th>Deleted At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {deletedContent.map((content) => (
                <tr key={content.content_id}>
                  <td>
                    <div>
                      <div style={{ fontWeight: '500' }}>{content.concept_name}</div>
                      <div style={{ fontSize: '13px', color: '#6b7280' }}>
                        {content.domain}
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className="badge badge-info">{content.domain}</span>
                  </td>
                  <td>
                    <span className={`badge ${getDifficultyBadge(content.difficulty)}`}>
                      {content.difficulty}
                    </span>
                  </td>
                  <td>{content.deleted_by || 'Unknown'}</td>
                  <td>{content.deleted_at ? new Date(content.deleted_at).toLocaleDateString() : 'N/A'}</td>
                  <td>
                    <button
                      className="btn btn-sm btn-success"
                      onClick={() => handleRestore(content.content_id, content.concept_name)}
                    >
                      ♻️ Restore
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">🗑️</div>
            <h3>No Deleted Content</h3>
            <p>Deleted content will appear here</p>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="ai-lab">
      {/* View Mode Toggle */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            className={`btn ${viewMode === 'active' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setViewMode('active')}
          >
            ✅ Active Content
          </button>
          <button
            className={`btn ${viewMode === 'deleted' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => {
              setViewMode('deleted');
              loadDeletedContent();
            }}
          >
            🗑️ Deleted Content ({deletedContent.length})
          </button>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            className="btn btn-secondary"
            onClick={() => handleExport('csv')}
            title="Export to CSV"
          >
            📥 CSV
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => handleExport('json')}
            title="Export to JSON"
          >
            📥 JSON
          </button>
        </div>
      </div>

      {/* AI Stats */}
      <div className="stats-grid" style={{ marginBottom: '24px' }}>
        <div className="stat-card">
          <div className="stat-icon">🤖</div>
          <div className="stat-value">{stats?.total_generations || aiContent.length}</div>
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

      {/* Content List or Generator */}
      {viewMode === 'active' ? (
        <>
          {/* Content Generator */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
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
                      maxHeight: '300px',
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

          {/* Active Content List */}
          {renderActiveContent()}
        </>
      ) : (
        renderDeletedContent()
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && deleteTarget && (
        <div className="modal-overlay" style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}>
          <div className="modal-content" style={{
            background: 'white',
            borderRadius: '12px',
            padding: '24px',
            width: '100%',
            maxWidth: '400px',
          }}>
            <h2 style={{ marginTop: 0 }}>Confirm Delete</h2>
            <p>Are you sure you want to delete <strong>{deleteTarget.name}</strong>?</p>
            <p style={{ color: '#6b7280', fontSize: '14px' }}>
              This content will be moved to the Deleted section and can be restored later.
            </p>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '24px' }}>
              <button className="btn btn-secondary" onClick={() => {
                setShowDeleteConfirm(false);
                setDeleteTarget(null);
              }}>
                Cancel
              </button>
              <button className="btn btn-danger" onClick={confirmDelete}>
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AILab;
