import React, { useState, useCallback } from 'react';
import { useCourseBuilder, CourseModuleData, ResourceData } from '../../hooks/content/useCourseBuilder';
import './CurriculumBuilder.css';

interface CurriculumBuilderBoardProps {
  courseId?: string;
  onSave?: (course: ReturnType<typeof useCourseBuilder>['course']) => void;
  onPublish?: (courseId: string) => void;
}

export function CurriculumBuilderBoard({
  courseId,
  onSave,
  onPublish,
}: CurriculumBuilderBoardProps) {
  const {
    course,
    isLoading,
    isSaving,
    hasUnsavedChanges,
    lastSavedAt,
    validationErrors,
    selectedModuleId,
    selectedResourceId,
    createCourse,
    updateCourse,
    saveCourse,
    publishCourse,
    addModule,
    updateModule,
    removeModule,
    duplicateModule,
    reorderModules,
    selectModule,
    addResource,
    removeResource,
    selectResource,
    validateCourse,
    discardChanges,
  } = useCourseBuilder({ courseId });

  const [showSettings, setShowSettings] = useState(false);
  const [draggedModuleIndex, setDraggedModuleIndex] = useState<number | null>(null);

  const handleCreateCourse = useCallback(() => {
    createCourse({ title: 'New Course' });
  }, [createCourse]);

  const handlePublish = useCallback(async () => {
    const validation = validateCourse();
    if (!validation.isValid) {
      alert(`Please fix errors before publishing:\n${validation.errors.join('\n')}`);
      return;
    }
    if (course) {
      await saveCourse();
      onPublish?.(course.id);
    }
  }, [course, saveCourse, validateCourse, onPublish]);

  const handleDragStart = (index: number) => {
    setDraggedModuleIndex(index);
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    if (draggedModuleIndex === null || draggedModuleIndex === index) return;
    
    reorderModules(draggedModuleIndex, index);
    setDraggedModuleIndex(index);
  };

  const handleDragEnd = () => {
    setDraggedModuleIndex(null);
  };

  const getResourceIcon = (type: ResourceData['type']) => {
    switch (type) {
      case 'video': return '🎬';
      case 'article': return '📄';
      case 'code_challenge': return '💻';
      case 'quiz': return '📝';
      case 'document': return '📁';
      case 'external_link': return '🔗';
      default: return '📌';
    }
  };

  if (isLoading) {
    return (
      <div className="curriculum-builder loading">
        <div className="builder-loading-spinner"></div>
        <p>Loading course...</p>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="curriculum-builder empty">
        <div className="builder-empty-state">
          <span className="empty-icon">📚</span>
          <h2>Create Your Course</h2>
          <p>Start building your learning content by creating a new course</p>
          <button className="btn-primary" onClick={handleCreateCourse}>
            Create New Course
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="curriculum-builder">
      <div className="builder-header">
        <div className="header-left">
          <input
            type="text"
            className="course-title-input"
            value={course.title}
            onChange={(e) => updateCourse({ title: e.target.value })}
            placeholder="Course Title"
          />
          <div className="header-status">
            {hasUnsavedChanges && (
              <span className="status-badge unsaved">Unsaved changes</span>
            )}
            {lastSavedAt && (
              <span className="status-badge saved">
                Saved: {lastSavedAt.toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>
        <div className="header-right">
          <button
            className="btn-secondary"
            onClick={() => setShowSettings(!showSettings)}
          >
            ⚙️ Settings
          </button>
          <button
            className="btn-secondary"
            onClick={discardChanges}
            disabled={!hasUnsavedChanges}
          >
            Discard
          </button>
          <button
            className="btn-secondary"
            onClick={saveCourse}
            disabled={!hasUnsavedChanges || isSaving}
          >
            {isSaving ? 'Saving...' : 'Save Draft'}
          </button>
          <button
            className="btn-primary"
            onClick={handlePublish}
            disabled={isSaving}
          >
            Publish Course
          </button>
        </div>
      </div>

      {validationErrors.length > 0 && (
        <div className="validation-errors">
          <h4>Please fix these issues:</h4>
          <ul>
            {validationErrors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {showSettings && (
        <div className="course-settings-panel">
          <h3>Course Settings</h3>
          <div className="settings-grid">
            <label className="setting-item">
              <span>Public Course</span>
              <input
                type="checkbox"
                checked={course.settings.isPublic}
                onChange={(e) => updateCourse({
                  settings: { ...course.settings, isPublic: e.target.checked }
                })}
              />
            </label>
            <label className="setting-item">
              <span>Allow Late Submission</span>
              <input
                type="checkbox"
                checked={course.settings.allowLateSubmission}
                onChange={(e) => updateCourse({
                  settings: { ...course.settings, allowLateSubmission: e.target.checked }
                })}
              />
            </label>
            <label className="setting-item">
              <span>Enable Discussions</span>
              <input
                type="checkbox"
                checked={course.settings.enableDiscussions}
                onChange={(e) => updateCourse({
                  settings: { ...course.settings, enableDiscussions: e.target.checked }
                })}
              />
            </label>
            <label className="setting-item">
              <span>Passing Score (%)</span>
              <input
                type="number"
                value={course.settings.passingScore}
                onChange={(e) => updateCourse({
                  settings: { ...course.settings, passingScore: parseInt(e.target.value) }
                })}
                min={0}
                max={100}
              />
            </label>
          </div>
        </div>
      )}

      <div className="builder-content">
        <div className="modules-sidebar">
          <div className="sidebar-header">
            <h3>Modules</h3>
            <button
              className="add-module-btn"
              onClick={() => addModule({ title: 'New Module' })}
            >
              + Add Module
            </button>
          </div>
          <div className="modules-list">
            {course.modules.length === 0 ? (
              <div className="no-modules">
                <p>No modules yet</p>
                <button onClick={() => addModule({ title: 'First Module' })}>
                  Add your first module
                </button>
              </div>
            ) : (
              course.modules.map((module, index) => (
                <div
                  key={module.id}
                  className={`module-item ${selectedModuleId === module.id ? 'selected' : ''}`}
                  draggable
                  onDragStart={() => handleDragStart(index)}
                  onDragOver={(e) => handleDragOver(e, index)}
                  onDragEnd={handleDragEnd}
                  onClick={() => selectModule(module.id)}
                >
                  <div className="module-drag-handle">⋮⋮</div>
                  <div className="module-info">
                    <span className="module-order">{index + 1}</span>
                    <input
                      type="text"
                      className="module-title"
                      value={module.title}
                      onChange={(e) => updateModule(module.id, { title: e.target.value })}
                      onClick={(e) => e.stopPropagation()}
                    />
                    <span className="module-resource-count">
                      {module.resources.length} resources
                    </span>
                  </div>
                  <div className="module-actions">
                    <button onClick={(e) => { e.stopPropagation(); duplicateModule(module.id); }}>
                      📋
                    </button>
                    <button onClick={(e) => { e.stopPropagation(); removeModule(module.id); }}>
                      🗑️
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="module-content">
          {selectedModuleId ? (
            (() => {
              const module = course.modules.find(m => m.id === selectedModuleId);
              if (!module) return null;
              
              return (
                <>
                  <div className="module-header">
                    <h3>{module.title}</h3>
                    <div className="module-header-actions">
                      <button
                        className="add-resource-btn"
                        onClick={() => addResource(selectedModuleId, { type: 'article', title: 'New Resource' })}
                      >
                        + Add Resource
                      </button>
                    </div>
                  </div>
                  
                  <div className="resources-grid">
                    {module.resources.length === 0 ? (
                      <div className="no-resources">
                        <p>No resources in this module</p>
                        <button onClick={() => addResource(selectedModuleId, { type: 'article', title: 'First Resource' })}>
                          Add your first resource
                        </button>
                      </div>
                    ) : (
                      module.resources.map((resource) => (
                        <div
                          key={resource.id}
                          className={`resource-card ${selectedResourceId === resource.id ? 'selected' : ''}`}
                          onClick={() => selectResource(resource.id)}
                        >
                          <div className="resource-icon">
                            {getResourceIcon(resource.type)}
                          </div>
                          <div className="resource-info">
                            <span className="resource-type">{resource.type.replace('_', ' ')}</span>
                            <input
                              type="text"
                              className="resource-title"
                              value={resource.title}
                              onChange={(e) => {
                                // Would call updateResource here
                              }}
                              onClick={(e) => e.stopPropagation()}
                            />
                          </div>
                          <div className="resource-actions">
                            <button onClick={(e) => { e.stopPropagation(); }}>
                              ✏️
                            </button>
                            <button onClick={(e) => { e.stopPropagation(); removeResource(selectedModuleId, resource.id); }}>
                              🗑️
                            </button>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </>
              );
            })()
          ) : (
            <div className="no-selection">
              <span className="selection-icon">📝</span>
              <p>Select a module to view and edit its content</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default CurriculumBuilderBoard;
