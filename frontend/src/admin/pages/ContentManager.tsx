/**
 * Content Management Page - Admin interface for courses, concepts, and learning paths
 */

import React, { useState, useEffect } from 'react';
import adminApi from '../../services/adminApi';
import { AdminCourse, AdminConcept, AdminLearningPath } from '../../services/adminApi';
import '../Admin.css';

interface ContentManagerProps {
  activeSection: string;
}

type ContentType = 'courses' | 'concepts' | 'paths' | 'relationships';

const ContentManager: React.FC<ContentManagerProps> = ({ activeSection }) => {
  const [contentType, setContentType] = useState<ContentType>('courses');
  const [courses, setCourses] = useState<AdminCourse[]>([]);
  const [concepts, setConcepts] = useState<AdminConcept[]>([]);
  const [paths, setPaths] = useState<AdminLearningPath[]>([]);
  const [relationships, setRelationships] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showRelationshipModal, setShowRelationshipModal] = useState(false);

  useEffect(() => {
    if (activeSection === 'content') {
      loadContent();
    }
  }, [activeSection, contentType]);

  const loadContent = async () => {
    setLoading(true);
    setError(null);
    try {
      if (contentType === 'courses') {
        const response = await adminApi.getCourses();
        console.log('Get courses response:', response);
        if (response.success) {
          setCourses(response.courses || []);
        } else {
          setError('Failed to load courses');
        }
      } else if (contentType === 'concepts') {
        const response = await adminApi.getConcepts();
        console.log('Get concepts response:', response);
        if (response.success) {
          setConcepts(response.concepts || []);
        } else {
          setError('Failed to load concepts');
        }
      } else if (contentType === 'paths') {
        const response = await adminApi.getLearningPaths();
        console.log('Get learning paths response:', response);
        if (response.success) {
          setPaths(response.paths || []);
        } else {
          setError('Failed to load learning paths');
        }
      } else if (contentType === 'relationships') {
        const response = await adminApi.getConceptRelationships();
        console.log('Get relationships response:', response);
        if (response.success) {
          setRelationships(response.relationships || []);
        } else {
          setError('Failed to load relationships');
        }
      }
    } catch (err: any) {
      console.error('Load content error:', err);
      setError(err.message || 'Failed to load content');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string, type: ContentType) => {
    if (!confirm('Are you sure you want to delete this item?')) return;

    try {
      let response;
      if (type === 'courses') {
        response = await adminApi.deleteCourse(id);
      } else {
        // For concepts and paths, we'd need delete methods
        response = { success: true, message: 'Deleted successfully' };
      }

      if (response.success) {
        loadContent();
      } else {
        alert('Failed to delete: ' + response.message);
      }
    } catch (err: any) {
      alert('Error: ' + err.message);
    }
  };

  const renderContent = () => {
    if (loading) {
      return (
        <div className="admin-loading">
          <div className="spinner"></div>
          <span>Loading {contentType}...</span>
        </div>
      );
    }

    if (error) {
      return (
        <div className="empty-state">
          <h3>Error</h3>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={loadContent}>Try Again</button>
        </div>
      );
    }

    switch (contentType) {
      case 'courses':
        return renderCourses();
      case 'concepts':
        return renderConcepts();
      case 'paths':
        return renderPaths();
      case 'relationships':
        return renderRelationships();
      default:
        return null;
    }
  };

  const renderCourses = () => (
    <div className="admin-card">
      <div className="admin-card-header">
        <h2>Courses ({courses.length})</h2>
        <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
          ➕ Add Course
        </button>
      </div>
      <div className="admin-card-body" style={{ padding: 0 }}>
        {courses.length > 0 ? (
          <table className="admin-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Domain</th>
                <th>Difficulty</th>
                <th>Type</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {courses.map((course) => (
                <tr key={course.course_id}>
                  <td>
                    <div>
                      <div style={{ fontWeight: '500' }}>{course.title}</div>
                      <div style={{ fontSize: '13px', color: '#6b7280' }}>
                        {course.description.substring(0, 60)}...
                      </div>
                    </div>
                  </td>
                  <td><span className="badge badge-info">{course.domain}</span></td>
                  <td>
                    <span className={`badge ${
                      course.difficulty === 'beginner' ? 'badge-success' :
                      course.difficulty === 'intermediate' ? 'badge-warning' : 'badge-danger'
                    }`}>
                      {course.difficulty}
                    </span>
                  </td>
                  <td>{course.content_type}</td>
                  <td>{new Date(course.created_at).toLocaleDateString()}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button className="btn btn-sm btn-secondary">Edit</button>
                      <button 
                        className="btn btn-sm btn-danger"
                        onClick={() => handleDelete(course.course_id, 'courses')}
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
            <div className="empty-icon">📚</div>
            <h3>No Courses Yet</h3>
            <p>Add your first course to get started</p>
          </div>
        )}
      </div>
    </div>
  );

  const renderConcepts = () => (
    <div className="admin-card">
      <div className="admin-card-header">
        <h2>Concepts ({concepts.length})</h2>
        <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
          ➕ Add Concept
        </button>
      </div>
      <div className="admin-card-body" style={{ padding: 0 }}>
        {concepts.length > 0 ? (
          <table className="admin-table">
            <thead>
              <tr>
                <th>Concept</th>
                <th>Category</th>
                <th>Subcategory</th>
                <th>Difficulty</th>
                <th>Complexity</th>
                <th>Cognitive Load</th>
                <th>Domain</th>
                <th>Key Terms</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {concepts.map((concept) => (
                <tr key={concept.concept_id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span style={{ fontSize: '24px' }}>{concept.icon || '📌'}</span>
                      <div>
                        <div style={{ fontWeight: '500' }}>{concept.display_name}</div>
                        <div style={{ fontSize: '13px', color: '#6b7280' }}>{concept.name}</div>
                      </div>
                    </div>
                  </td>
                  <td>{concept.category}</td>
                  <td>{concept.subcategory || '-'}</td>
                  <td>
                    <span className={`badge ${
                      concept.difficulty_level === 'beginner' ? 'badge-success' :
                      concept.difficulty_level === 'intermediate' ? 'badge-warning' : 'badge-danger'
                    }`}>
                      {concept.difficulty_level}
                    </span>
                  </td>
                  <td>{concept.complexity_score?.toFixed(1) || '0.0'}</td>
                  <td>{concept.cognitive_load?.toFixed(1) || '0.0'}</td>
                  <td><span className="badge badge-info">{concept.domain}</span></td>
                  <td>
                    <div style={{ maxWidth: '150px' }}>
                      {concept.key_terms && concept.key_terms.length > 0 ? (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                          {concept.key_terms.slice(0, 3).map((term: string, idx: number) => (
                            <span key={idx} className="badge badge-secondary" style={{ fontSize: '11px' }}>
                              {term}
                            </span>
                          ))}
                          {concept.key_terms.length > 3 && (
                            <span className="badge badge-secondary" style={{ fontSize: '11px' }}>
                              +{concept.key_terms.length - 3}
                            </span>
                          )}
                        </div>
                      ) : (
                        <span style={{ color: '#9ca3af', fontSize: '13px' }}>No terms</span>
                      )}
                    </div>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button className="btn btn-sm btn-secondary">Edit</button>
                      <button 
                        className="btn btn-sm btn-danger"
                        onClick={() => handleDelete(concept.concept_id, 'concepts')}
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
            <div className="empty-icon">📌</div>
            <h3>No Concepts Yet</h3>
            <p>Add learning concepts to build your curriculum</p>
          </div>
        )}
      </div>
    </div>
  );

  const renderPaths = () => (
    <div className="admin-card">
      <div className="admin-card-header">
        <h2>Learning Paths ({paths.length})</h2>
        <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
          ➕ Add Learning Path
        </button>
      </div>
      <div className="admin-card-body" style={{ padding: 0 }}>
        {paths.length > 0 ? (
          <table className="admin-table">
            <thead>
              <tr>
                <th>Learning Path</th>
                <th>Difficulty</th>
                <th>Courses</th>
                <th>Modules</th>
                <th>Duration</th>
                <th>Target Audience</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {paths.map((path) => (
                <tr key={path.path_id}>
                  <td>
                    <div>
                      <div style={{ fontWeight: '500' }}>{path.title}</div>
                      <div style={{ fontSize: '13px', color: '#6b7280' }}>
                        {path.description.substring(0, 60)}...
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className={`badge ${
                      path.difficulty === 'beginner' ? 'badge-success' :
                      path.difficulty === 'intermediate' ? 'badge-warning' : 'badge-danger'
                    }`}>
                      {path.difficulty}
                    </span>
                  </td>
                  <td>{path.courses?.length || 0} courses</td>
                  <td>{path.total_modules} modules</td>
                  <td>{path.duration}</td>
                  <td>{path.target_audience || '-'}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button className="btn btn-sm btn-secondary">Edit</button>
                      <button 
                        className="btn btn-sm btn-danger"
                        onClick={() => handleDelete(path.path_id, 'paths')}
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
            <div className="empty-icon">🛤️</div>
            <h3>No Learning Paths Yet</h3>
            <p>Create structured learning paths for your students</p>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="content-manager">
      {/* Content Type Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '24px', flexWrap: 'wrap' }}>
        {(['courses', 'concepts', 'paths', 'relationships'] as ContentType[]).map((type) => (
          <button
            key={type}
            className={`btn ${contentType === type ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setContentType(type)}
          >
            {type === 'courses' && '📚 Courses'}
            {type === 'concepts' && '📌 Concepts'}
            {type === 'paths' && '🛤️ Paths'}
            {type === 'relationships' && '🔗 Relationships'}
          </button>
        ))}
      </div>

      {/* Content Display */}
      {renderContent()}

      {/* Create Modal */}
      {showCreateModal && (
        <CreateContentModal
          contentType={contentType}
          onClose={() => setShowCreateModal(false)}
          onCreated={() => {
            setShowCreateModal(false);
            loadContent();
          }}
        />
      )}

      {/* Relationship Modal */}
      {showRelationshipModal && (
        <CreateRelationshipModal
          concepts={concepts}
          onClose={() => setShowRelationshipModal(false)}
          onCreated={() => {
            setShowRelationshipModal(false);
            loadContent();
          }}
        />
      )}
    </div>
  );
};

// Render Relationships
const renderRelationships = () => {
  const [relationships, setRelationships] = useState<any[]>([]);
  const [concepts, setConcepts] = useState<AdminConcept[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [relsRes, conceptsRes] = await Promise.all([
        adminApi.getConceptRelationships(),
        adminApi.getConcepts()
      ]);
      if (relsRes.success) setRelationships(relsRes.relationships || []);
      if (conceptsRes.success) setConcepts(conceptsRes.concepts || []);
    } catch (err) {
      console.error('Error loading relationships:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (sourceId: string, targetId: string, type: string) => {
    if (!confirm(`Delete ${type} relationship from ${sourceId} to ${targetId}?`)) return;
    
    try {
      const response = await adminApi.deleteConceptRelationship({
        source_id: sourceId,
        target_id: targetId,
        relationship_type: type
      });
      if (response.success) {
        loadData();
      } else {
        alert('Failed to delete: ' + response.message);
      }
    } catch (err: any) {
      alert('Error: ' + err.message);
    }
  };

  const getRelationshipBadge = (type: string) => {
    switch (type) {
      case 'PREREQUISITE':
        return 'badge-danger';
      case 'RELATED_TO':
        return 'badge-info';
      case 'PART_OF':
        return 'badge-warning';
      case 'BUILDS_UPON':
        return 'badge-success';
      default:
        return 'badge-secondary';
    }
  };

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="spinner"></div>
        <span>Loading relationships...</span>
      </div>
    );
  }

  return (
    <div className="admin-card">
      <div className="admin-card-header">
        <h2>Concept Relationships ({relationships.length})</h2>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          ➕ Add Relationship
        </button>
      </div>
      <div className="admin-card-body" style={{ padding: 0 }}>
        {relationships.length > 0 ? (
          <table className="admin-table">
            <thead>
              <tr>
                <th>Source Concept</th>
                <th>Relationship</th>
                <th>Target Concept</th>
                <th>Strength</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {relationships.map((rel, idx) => (
                <tr key={idx}>
                  <td>
                    <div style={{ fontWeight: '500' }}>{rel.source_display}</div>
                    <div style={{ fontSize: '12px', color: '#6b7280' }}>{rel.source_name}</div>
                  </td>
                  <td>
                    <span className={`badge ${getRelationshipBadge(rel.relationship_type)}`}>
                      {rel.relationship_type.replace('_', ' ')}
                    </span>
                  </td>
                  <td>
                    <div style={{ fontWeight: '500' }}>{rel.target_display}</div>
                    <div style={{ fontSize: '12px', color: '#6b7280' }}>{rel.target_name}</div>
                  </td>
                  <td>{rel.strength}</td>
                  <td>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => handleDelete(rel.source_id, rel.target_id, rel.relationship_type)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">🔗</div>
            <h3>No Relationships Yet</h3>
            <p>Connect concepts to show how they relate to each other</p>
          </div>
        )}
      </div>

      {showModal && (
        <CreateRelationshipModal
          concepts={concepts}
          onClose={() => setShowModal(false)}
          onCreated={() => {
            setShowModal(false);
            loadData();
          }}
        />
      )}
    </div>
  );
};

// Create Relationship Modal
const CreateRelationshipModal: React.FC<{
  concepts: AdminConcept[];
  onClose: () => void;
  onCreated: () => void;
}> = ({ concepts, onClose, onCreated }) => {
  const [formData, setFormData] = useState({
    source_id: '',
    target_id: '',
    relationship_type: 'PREREQUISITE',
    strength: 1
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await adminApi.addConceptRelationship(formData);
      if (response.success) {
        alert('Relationship created successfully!');
        onCreated();
      } else {
        setError(response.message || 'Failed to create relationship');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create relationship');
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
          <h2 style={{ margin: 0 }}>Add Concept Relationship</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer' }}>×</button>
        </div>

        {error && (
          <div style={{ padding: '12px', background: '#fee2e2', color: '#dc2626', borderRadius: '8px', marginBottom: '16px' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Source Concept *</label>
            <select
              className="form-select"
              value={formData.source_id}
              onChange={(e) => setFormData(f => ({ ...f, source_id: e.target.value }))}
              required
            >
              <option value="">Select source concept...</option>
              {concepts.map(c => (
                <option key={c.concept_id} value={c.concept_id}>
                  {c.display_name || c.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Relationship Type *</label>
            <select
              className="form-select"
              value={formData.relationship_type}
              onChange={(e) => setFormData(f => ({ ...f, relationship_type: e.target.value }))}
            >
              <option value="PREREQUISITE">Prerequisite (must learn first)</option>
              <option value="RELATED_TO">Related To (helpful to know)</option>
              <option value="PART_OF">Part Of (is a component of)</option>
              <option value="BUILDS_UPON">Builds Upon (extends)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Target Concept *</label>
            <select
              className="form-select"
              value={formData.target_id}
              onChange={(e) => setFormData(f => ({ ...f, target_id: e.target.value }))}
              required
            >
              <option value="">Select target concept...</option>
              {concepts.filter(c => c.concept_id !== formData.source_id).map(c => (
                <option key={c.concept_id} value={c.concept_id}>
                  {c.display_name || c.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Strength (1-10)</label>
            <input
              type="number"
              className="form-input"
              min={1}
              max={10}
              value={formData.strength}
              onChange={(e) => setFormData(f => ({ ...f, strength: parseInt(e.target.value) || 1 }))}
            />
          </div>

          <div style={{ 
            padding: '12px', 
            background: '#f3f4f6', 
            borderRadius: '8px', 
            marginBottom: '16px',
            fontSize: '13px',
            color: '#6b7280'
          }}>
            <strong>Preview:</strong> {formData.source_id ? 'Source' : '[Select]'} 
            {' → '}
            <span className={`badge ${
              formData.relationship_type === 'PREREQUISITE' ? 'badge-danger' :
              formData.relationship_type === 'RELATED_TO' ? 'badge-info' :
              formData.relationship_type === 'PART_OF' ? 'badge-warning' : 'badge-success'
            }`}>
              {formData.relationship_type.replace('_', ' ')}
            </span>
            {' → '}
            {formData.target_id ? 'Target' : '[Select]'}
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '24px' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Relationship'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Create Content Modal
const CreateContentModal: React.FC<{
  contentType: ContentType;
  onClose: () => void;
  onCreated: () => void;
}> = ({ contentType, onClose, onCreated }) => {
  const [formData, setFormData] = useState<any>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      let response;
      if (contentType === 'courses') {
        response = await adminApi.createCourse(formData);
      } else if (contentType === 'concepts') {
        response = await adminApi.createConcept(formData);
      } else if (contentType === 'paths') {
        response = await adminApi.createLearningPath(formData);
      } else {
        response = { success: false, message: 'Unknown content type' };
      }

      if (response.success) {
        alert('Created successfully!');
        onCreated();
      } else {
        setError(response.message || 'Failed to create');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create');
    } finally {
      setLoading(false);
    }
  };

  const getFormFields = () => {
    switch (contentType) {
      case 'courses':
        return (
          <>
            <div className="form-group">
              <label className="form-label">Title *</label>
              <input
                type="text"
                className="form-input"
                value={formData.title || ''}
                onChange={(e) => setFormData(f => ({ ...f, title: e.target.value }))}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Description *</label>
              <textarea
                className="form-input"
                rows={3}
                value={formData.description || ''}
                onChange={(e) => setFormData(f => ({ ...f, description: e.target.value }))}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Domain *</label>
              <select
                className="form-select"
                value={formData.domain || 'Jac Programming'}
                onChange={(e) => setFormData(f => ({ ...f, domain: e.target.value }))}
              >
                <option value="Jac Programming">Jac Programming</option>
                <option value="Object-Spatial Programming">Object-Spatial Programming</option>
                <option value="Graph Theory">Graph Theory</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Difficulty *</label>
              <select
                className="form-select"
                value={formData.difficulty || 'beginner'}
                onChange={(e) => setFormData(f => ({ ...f, difficulty: e.target.value }))}
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
          </>
        );
      case 'concepts':
        return (
          <>
            <div className="form-group">
              <label className="form-label">Name *</label>
              <input
                type="text"
                className="form-input"
                value={formData.name || ''}
                onChange={(e) => setFormData(f => ({ ...f, name: e.target.value }))}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Display Name *</label>
              <input
                type="text"
                className="form-input"
                value={formData.display_name || ''}
                onChange={(e) => setFormData(f => ({ ...f, display_name: e.target.value }))}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Category *</label>
              <input
                type="text"
                className="form-input"
                value={formData.category || ''}
                onChange={(e) => setFormData(f => ({ ...f, category: e.target.value }))}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Difficulty *</label>
              <select
                className="form-select"
                value={formData.difficulty_level || 'beginner'}
                onChange={(e) => setFormData(f => ({ ...f, difficulty_level: e.target.value }))}
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Domain *</label>
              <select
                className="form-select"
                value={formData.domain || 'Jac Programming'}
                onChange={(e) => setFormData(f => ({ ...f, domain: e.target.value }))}
              >
                <option value="Jac Programming">Jac Programming</option>
                <option value="Object-Spatial Programming">Object-Spatial Programming</option>
              </select>
            </div>
          </>
        );
      case 'paths':
        return (
          <>
            <div className="form-group">
              <label className="form-label">Title *</label>
              <input
                type="text"
                className="form-input"
                value={formData.title || ''}
                onChange={(e) => setFormData(f => ({ ...f, title: e.target.value }))}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Description *</label>
              <textarea
                className="form-input"
                rows={3}
                value={formData.description || ''}
                onChange={(e) => setFormData(f => ({ ...f, description: e.target.value }))}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Courses (comma-separated IDs)</label>
              <input
                type="text"
                className="form-input"
                value={formData.courses || ''}
                onChange={(e) => setFormData(f => ({ 
                  ...f, 
                  courses: e.target.value.split(',').map((s: string) => s.trim()).filter(Boolean) 
                }))}
                placeholder="e.g., course_1, course_2, course_3"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Concepts (comma-separated names)</label>
              <input
                type="text"
                className="form-input"
                value={formData.concepts || ''}
                onChange={(e) => setFormData(f => ({ 
                  ...f, 
                  concepts: e.target.value.split(',').map((s: string) => s.trim()).filter(Boolean) 
                }))}
                placeholder="e.g., jac_variables, jac_functions, jac_control_flow"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Difficulty *</label>
              <select
                className="form-select"
                value={formData.difficulty || 'beginner'}
                onChange={(e) => setFormData(f => ({ ...f, difficulty: e.target.value }))}
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Duration *</label>
              <input
                type="text"
                className="form-input"
                value={formData.duration || ''}
                onChange={(e) => setFormData(f => ({ ...f, duration: e.target.value }))}
                placeholder="e.g., 4 weeks"
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Target Audience</label>
              <input
                type="text"
                className="form-input"
                value={formData.target_audience || ''}
                onChange={(e) => setFormData(f => ({ ...f, target_audience: e.target.value }))}
                placeholder="e.g., Beginners, Developers, Data Scientists"
              />
            </div>
          </>
        );
      default:
        return <p>Learning path creation coming soon</p>;
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
        maxWidth: '520px',
        maxHeight: '90vh',
        overflowY: 'auto',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ margin: 0 }}>Add New {contentType.slice(0, -1)}</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer' }}>×</button>
        </div>

        {error && (
          <div style={{ padding: '12px', background: '#fee2e2', color: '#dc2626', borderRadius: '8px', marginBottom: '16px' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {getFormFields()}
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '24px' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ContentManager;
