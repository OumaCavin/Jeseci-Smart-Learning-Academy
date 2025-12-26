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

const QuizManager: React.FC<QuizManagerProps> = ({ activeSection }) => {
  const [quizzes, setQuizzes] = useState<AdminQuiz[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);

  useEffect(() => {
    if (activeSection === 'quizzes') {
      loadQuizzes();
      loadAnalytics();
    }
  }, [activeSection]);

  const loadQuizzes = async () => {
    setLoading(true);
    try {
      const response = await adminApi.getQuizzes();
      if (response.success) {
        setQuizzes(response.quizzes || []);
      } else {
        setError('Failed to load quizzes');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load quizzes');
    } finally {
      setLoading(false);
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

  const handleDelete = async (quizId: string) => {
    if (!confirm('Are you sure you want to delete this quiz?')) return;

    try {
      const response = await adminApi.deleteQuiz(quizId);
      if (response.success) {
        loadQuizzes();
      } else {
        alert('Failed to delete: ' + response.message);
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

  return (
    <div className="quiz-manager">
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

      {/* Quizzes Table */}
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
                          onClick={() => handleDelete(quiz.quiz_id)}
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
      if (response.success) {
        alert('Quiz created successfully!');
        onCreated();
      } else {
        setError(response.message || 'Failed to create quiz');
      }
    } catch (err: any) {
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
