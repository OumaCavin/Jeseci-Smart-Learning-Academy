/**
 * Quiz Management Page - Admin interface for quizzes
 */

import React, { useState, useEffect } from 'react';
import adminApi from '../../services/adminApi';
import { AdminQuiz } from '../../services/adminApi';
import '../Admin.css';

interface QuizManagerProps {
  activeSection: string;
}

type ViewMode = 'active' | 'deleted';

const QuizManager: React.FC<QuizManagerProps> = ({ activeSection }) => {
  const [viewMode, setViewMode] = useState<ViewMode>('active');
  const [quizzes, setQuizzes] = useState<AdminQuiz[]>([]);
  const [deletedQuizzes, setDeletedQuizzes] = useState<AdminQuiz[]>([]);
  const [concepts, setConcepts] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [showAIGenerateModal, setShowAIGenerateModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{ id: string; name: string } | null>(null);

  useEffect(() => {
    if (activeSection === 'quizzes') {
      loadQuizzes();
      loadAnalytics();
      loadConcepts();
    }
  }, [activeSection, viewMode]);

  const loadConcepts = async () => {
    try {
      const response = await adminApi.getConcepts();
      if (response.success) {
        setConcepts(response.concepts || []);
      }
    } catch (err) {
      console.log('Could not load concepts');
    }
  };

  const loadQuizzes = async () => {
    setLoading(true);
    try {
      const response = await adminApi.getQuizzes();
      console.log('Get quizzes response:', response);
      if (response.success) {
        setQuizzes(response.quizzes || []);
      } else {
        setError('Failed to load quizzes');
      }
    } catch (err: any) {
      console.error('Load quizzes error:', err);
      setError(err.message || 'Failed to load quizzes');
    } finally {
      setLoading(false);
    }
  };

  const loadDeletedQuizzes = async () => {
    try {
      const response = await adminApi.getDeletedQuizzes();
      if (response.success) {
        setDeletedQuizzes(response.quizzes || []);
      }
    } catch (err: any) {
      console.error('Error loading deleted quizzes:', err);
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await adminApi.getQuizAnalytics();
      if (response.success) {
        setAnalytics(response.analytics);
      }
    } catch (err) {
      // Analytics might not be available
      console.log('Analytics not available');
    }
  };

  const handleDelete = (quizId: string, title: string) => {
    setDeleteTarget({ id: quizId, name: title });
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;

    try {
      const response = await adminApi.deleteQuiz(deleteTarget.id, 'admin', '127.0.0.1');
      if (response.success) {
        alert(`${deleteTarget.name} deleted successfully`);
        loadQuizzes();
        loadDeletedQuizzes();
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

  const handleRestore = async (quizId: string, title: string) => {
    try {
      const response = await adminApi.restoreQuiz(quizId, 'admin', '127.0.0.1');
      if (response.success) {
        alert(`${title} restored successfully`);
        loadQuizzes();
        loadDeletedQuizzes();
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
        response = await adminApi.exportQuizzesCsv();
      } else {
        response = await adminApi.exportQuizzesJson();
      }

      if (response.success) {
        // Create and download file
        const blob = new Blob([response.data], {
          type: format === 'csv' ? 'text/csv' : 'application/json'
        });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `quizzes_export_${new Date().toISOString().split('T')[0]}.${format}`;
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
        <span>Loading quizzes...</span>
      </div>
    );
  }

  const renderDeletedQuizzes = () => (
    <div className="admin-card">
      <div className="admin-card-header">
        <h2>Deleted Quizzes ({deletedQuizzes.length})</h2>
      </div>
      <div className="admin-card-body" style={{ padding: 0 }}>
        {deletedQuizzes.length > 0 ? (
          <table className="admin-table">
            <thead>
              <tr>
                <th>Quiz Title</th>
                <th>Difficulty</th>
                <th>Deleted By</th>
                <th>Deleted At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {deletedQuizzes.map((quiz) => (
                <tr key={quiz.quiz_id}>
                  <td>
                    <div>
                      <div style={{ fontWeight: '500' }}>{quiz.title}</div>
                      <div style={{ fontSize: '13px', color: '#6b7280' }}>
                        {quiz.description.substring(0, 60)}...
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className={`badge ${getDifficultyBadge(quiz.difficulty)}`}>
                      {quiz.difficulty}
                    </span>
                  </td>
                  <td>{quiz.deleted_by || 'Unknown'}</td>
                  <td>{quiz.deleted_at ? new Date(quiz.deleted_at).toLocaleDateString() : 'N/A'}</td>
                  <td>
                    <button
                      className="btn btn-sm btn-success"
                      onClick={() => handleRestore(quiz.quiz_id, quiz.title)}
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
            <h3>No Deleted Quizzes</h3>
            <p>Deleted quizzes will appear here</p>
          </div>
        )}
      </div>
    </div>
  );

  const renderActiveQuizzes = () => (
    <div className="admin-card">
      <div className="admin-card-header">
        <h2>All Quizzes ({quizzes.length})</h2>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button 
            className="btn btn-secondary" 
            onClick={() => setShowAnalytics(!showAnalytics)}
          >
            📊 Analytics
          </button>
          <button 
            className="btn btn-secondary" 
            onClick={() => setShowAIGenerateModal(true)}
            style={{ background: '#8b5cf6', color: 'white' }}
          >
            🤖 AI Generate
          </button>
          <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
            ➕ Create Quiz
          </button>
        </div>
      </div>
      <div className="admin-card-body" style={{ padding: 0 }}>
        {quizzes.length > 0 ? (
          <table className="admin-table">
            <thead>
              <tr>
                <th>Quiz Title</th>
                <th>Course ID</th>
                <th>Difficulty</th>
                <th>Questions</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {quizzes.map((quiz) => (
                <tr key={quiz.quiz_id}>
                  <td>
                    <div>
                      <div style={{ fontWeight: '500' }}>{quiz.title}</div>
                      <div style={{ fontSize: '13px', color: '#6b7280' }}>
                        {quiz.description.substring(0, 60)}...
                      </div>
                    </div>
                  </td>
                  <td>
                    <code style={{ fontSize: '12px', background: '#f3f4f6', padding: '2px 6px', borderRadius: '4px' }}>
                      {quiz.course_id || 'N/A'}
                    </code>
                  </td>
                  <td>
                    <span className={`badge ${getDifficultyBadge(quiz.difficulty)}`}>
                      {quiz.difficulty}
                    </span>
                  </td>
                  <td>{quiz.questions_count} questions</td>
                  <td>{new Date(quiz.created_at).toLocaleDateString()}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button className="btn btn-sm btn-secondary">Edit</button>
                      <button className="btn btn-sm btn-secondary">Preview</button>
                      <button 
                        className="btn btn-sm btn-danger"
                        onClick={() => handleDelete(quiz.quiz_id, quiz.title)}
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
            <div className="empty-icon">📝</div>
            <h3>No Quizzes Yet</h3>
            <p>Create your first quiz to test student knowledge</p>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="quiz-manager">
      {/* View Mode Toggle */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            className={`btn ${viewMode === 'active' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => {
              setViewMode('active');
            }}
          >
            ✅ Active Quizzes
          </button>
          <button
            className={`btn ${viewMode === 'deleted' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => {
              setViewMode('deleted');
              loadDeletedQuizzes();
            }}
          >
            🗑️ Deleted Quizzes ({deletedQuizzes.length})
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

      {/* Analytics Summary */}
      <div className="stats-grid" style={{ marginBottom: '24px' }}>
        <div className="stat-card">
          <div className="stat-icon">📝</div>
          <div className="stat-value">{analytics?.total_quizzes || quizzes.length}</div>
          <div className="stat-label">Total Quizzes</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-value">{analytics?.total_attempts || 0}</div>
          <div className="stat-label">Total Attempts</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-value">{analytics?.average_score?.toFixed(1) || 0}%</div>
          <div className="stat-label">Average Score</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🎯</div>
          <div className="stat-value">{analytics?.pass_rate?.toFixed(1) || 0}%</div>
          <div className="stat-label">Pass Rate</div>
        </div>
      </div>

      {/* Content Based on View Mode */}
      {viewMode === 'active' ? renderActiveQuizzes() : renderDeletedQuizzes()}

      {/* Create Quiz Modal */}
      {showCreateModal && (
        <CreateQuizModal
          onClose={() => setShowCreateModal(false)}
          onCreated={() => {
            setShowCreateModal(false);
            loadQuizzes();
          }}
        />
      )}

      {/* AI Generate Quiz Modal */}
      {showAIGenerateModal && (
        <AIGenerateQuizModal
          concepts={concepts}
          onClose={() => setShowAIGenerateModal(false)}
          onGenerated={() => {
            setShowAIGenerateModal(false);
            loadQuizzes();
          }}
        />
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
              This quiz will be moved to the Deleted section and can be restored later.
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

// AI Generate Quiz Modal
const AIGenerateQuizModal: React.FC<{
  concepts: any[];
  onClose: () => void;
  onGenerated: () => void;
}> = ({ concepts, onClose, onGenerated }) => {
  const [formData, setFormData] = useState({
    topic: '',
    difficulty: 'beginner',
    question_count: 5,
  });
  const [generatedQuiz, setGeneratedQuiz] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sample topics for JAC programming
  const sampleTopics = [
    { value: 'jac_programming_fundamentals', label: 'JAC Programming Fundamentals' },
    { value: 'jac_variables_data_types', label: 'JAC Variables and Data Types' },
    { value: 'jac_control_flow', label: 'JAC Control Flow' },
    { value: 'jac_functions', label: 'JAC Functions' },
    { value: 'jac_collections', label: 'JAC Collections' },
    { value: 'jac_oop', label: 'JAC Object-Oriented Programming' },
    { value: 'jac_object_spatial_programming', label: 'JAC Object-Spatial Programming' },
    { value: 'jac_nodes_edges', label: 'JAC Nodes and Edges' },
    { value: 'jac_walkers', label: 'JAC Walkers and Graph Traversal' },
    { value: 'jac_ai_integration', label: 'JAC AI Integration with byLLM' },
    { value: 'jac_scale_agnostic_programming', label: 'JAC Scale-Agnostic Programming' },
  ];

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    setError(null);

    try {
      const response = await adminApi.generateAIQuiz({
        topic: formData.topic,
        difficulty: formData.difficulty,
        question_count: formData.question_count,
      });
      console.log('AI Generate quiz response:', response);
      if (response.success) {
        setGeneratedQuiz(response.quiz);
      } else {
        setError(response.message || 'Failed to generate quiz');
      }
    } catch (err: any) {
      console.error('AI generate quiz error:', err);
      setError(err.message || 'Failed to generate quiz');
    } finally {
      setGenerating(false);
    }
  };

  const handleSave = async () => {
    if (!generatedQuiz) return;
    
    setLoading(true);
    setError(null);

    try {
      const response = await adminApi.saveAIQuiz(generatedQuiz, formData.topic, formData.difficulty);
      console.log('Save AI quiz response:', response);
      if (response.success) {
        alert('Quiz saved successfully!');
        onGenerated();
      } else {
        setError(response.message || 'Failed to save quiz');
      }
    } catch (err: any) {
      console.error('Save AI quiz error:', err);
      setError(err.message || 'Failed to save quiz');
    } finally {
      setLoading(false);
    }
  };

  return (
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
        maxWidth: generatedQuiz ? '700px' : '480px',
        maxHeight: '90vh',
        overflowY: 'auto',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ margin: 0 }}>🤖 AI Quiz Generator</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer' }}>×</button>
        </div>

        {error && (
          <div style={{ padding: '12px', background: '#fee2e2', color: '#dc2626', borderRadius: '8px', marginBottom: '16px' }}>
            {error}
          </div>
        )}

        {!generatedQuiz ? (
          <form onSubmit={handleGenerate}>
            <div className="form-group">
              <label className="form-label">Quiz Topic *</label>
              <select
                className="form-select"
                value={formData.topic}
                onChange={(e) => setFormData(f => ({ ...f, topic: e.target.value }))}
                required
              >
                <option value="">Select a topic...</option>
                {sampleTopics.map(topic => (
                  <option key={topic.value} value={topic.value}>{topic.label}</option>
                ))}
              </select>
              <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                Or enter a custom topic: <input
                  type="text"
                  className="form-input"
                  style={{ marginTop: '4px', padding: '8px' }}
                  placeholder="Custom topic..."
                  onChange={(e) => {
                    if (!sampleTopics.find(t => t.value === e.target.value)) {
                      setFormData(f => ({ ...f, topic: e.target.value }));
                    }
                  }}
                />
              </p>
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
                <option value="expert">Expert</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Number of Questions *</label>
              <input
                type="number"
                className="form-input"
                min={1}
                max={20}
                value={formData.question_count}
                onChange={(e) => setFormData(f => ({ ...f, question_count: parseInt(e.target.value) || 5 }))}
                required
              />
            </div>

            <div style={{ 
              padding: '16px', 
              background: '#f0f9ff', 
              borderRadius: '8px', 
              marginBottom: '16px',
              border: '1px solid #bae6fd'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span style={{ fontSize: '20px' }}>💡</span>
                <strong style={{ color: '#0369a1' }}>AI Quiz Generation</strong>
              </div>
              <p style={{ fontSize: '13px', color: '#0c4a6e', margin: 0 }}>
                The AI will generate multiple-choice questions based on your selected topic and difficulty level.
                Each question will include the correct answer and an explanation.
              </p>
            </div>

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '24px' }}>
              <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
              <button type="submit" className="btn btn-primary" disabled={generating} style={{ background: '#8b5cf6' }}>
                {generating ? 'Generating...' : '🤖 Generate Quiz'}
              </button>
            </div>
          </form>
        ) : (
          <div>
            <div style={{ 
              padding: '16px', 
              background: '#f0fdf4', 
              borderRadius: '8px', 
              marginBottom: '16px',
              border: '1px solid #86efac'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span style={{ fontSize: '20px' }}>✅</span>
                <strong style={{ color: '#166534' }}>Quiz Generated Successfully!</strong>
              </div>
              <p style={{ fontSize: '13px', color: '#166534', margin: 0 }}>
                {generatedQuiz.questions.length} questions generated for "{formData.topic}" at {formData.difficulty} level.
              </p>
            </div>

            <div style={{ maxHeight: '300px', overflowY: 'auto', marginBottom: '16px' }}>
              {generatedQuiz.questions.map((q: any, idx: number) => (
                <div key={idx} style={{ 
                  padding: '12px', 
                  background: '#f9fafb', 
                  borderRadius: '8px', 
                  marginBottom: '8px',
                  border: '1px solid #e5e7eb'
                }}>
                  <div style={{ fontWeight: '500', marginBottom: '8px' }}>
                    {idx + 1}. {q.question}
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '13px' }}>
                    {q.options.map((opt: string, optIdx: number) => (
                      <div key={optIdx} style={{ 
                        padding: '6px 10px',
                        background: optIdx === q.correct_answer ? '#dcfce7' : 'white',
                        border: optIdx === q.correct_answer ? '1px solid #86efac' : '1px solid #e5e7eb',
                        borderRadius: '4px',
                        color: optIdx === q.correct_answer ? '#166534' : '#374151'
                      }}>
                        {String.fromCharCode(65 + optIdx)}. {opt}
                      </div>
                    ))}
                  </div>
                  <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '8px', fontStyle: 'italic' }}>
                    💡 {q.explanation}
                  </div>
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '24px' }}>
              <button 
                type="button" 
                className="btn btn-secondary" 
                onClick={() => setGeneratedQuiz(null)}
              >
                ← Generate Again
              </button>
              <button 
                type="button" 
                className="btn btn-primary" 
                onClick={handleSave}
                disabled={loading}
                style={{ background: '#8b5cf6' }}
              >
                {loading ? 'Saving...' : '💾 Save Quiz'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Create Quiz Modal
const CreateQuizModal: React.FC<{ onClose: () => void; onCreated: () => void }> = ({ onClose, onCreated }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    course_id: '',
    difficulty: 'beginner',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await adminApi.createQuiz(formData);
      console.log('Create quiz response:', response);
      if (response.success) {
        alert('Quiz created successfully!');
        onCreated();
      } else {
        setError(response.message || 'Failed to create quiz');
      }
    } catch (err: any) {
      console.error('Create quiz error:', err);
      setError(err.message || 'Failed to create quiz');
    } finally {
      setLoading(false);
    }
  };

  return (
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
        maxWidth: '480px',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ margin: 0 }}>Create New Quiz</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer' }}>×</button>
        </div>

        {error && (
          <div style={{ padding: '12px', background: '#fee2e2', color: '#dc2626', borderRadius: '8px', marginBottom: '16px' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Quiz Title *</label>
            <input
              type="text"
              className="form-input"
              value={formData.title}
              onChange={(e) => setFormData(f => ({ ...f, title: e.target.value }))}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Description *</label>
            <textarea
              className="form-input"
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData(f => ({ ...f, description: e.target.value }))}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Associated Course ID (optional)</label>
            <input
              type="text"
              className="form-input"
              value={formData.course_id}
              onChange={(e) => setFormData(f => ({ ...f, course_id: e.target.value }))}
              placeholder="Leave empty for standalone quiz"
            />
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

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '24px' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Quiz'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default QuizManager;
