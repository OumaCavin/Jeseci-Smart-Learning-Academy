import React, { useState, useCallback, useEffect } from 'react';
import { useScheduler, ScheduledTask, TaskExecutionLog } from '../../contexts/SchedulerContext';
import './SchedulerBoard.css';

interface SchedulerBoardProps {
  onTaskSelect?: (task: ScheduledTask) => void;
}

export function SchedulerBoard({ onTaskSelect }: SchedulerBoardProps) {
  const {
    tasks,
    selectedTask,
    isLoading,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleTask,
    executeTask,
    executionLogs,
    fetchExecutionLogs,
    templates,
    createFromTemplate,
    validateCronExpression,
    getTaskStats,
  } = useScheduler();

  const [activeTab, setActiveTab] = useState<'tasks' | 'logs' | 'templates'>('tasks');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showCronHelper, setShowCronHelper] = useState(false);
  const [newTask, setNewTask] = useState({
    name: '',
    description: '',
    type: 'email_digest' as ScheduledTask['type'],
    cronExpression: '0 0 * * *',
    enabled: false,
  });
  const [cronValidation, setCronValidation] = useState<{ isValid: boolean; humanReadable: string; error?: string }>({ isValid: true, humanReadable: '' });

  const stats = getTaskStats();

  // Fetch tasks on mount
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Validate cron expression
  useEffect(() => {
    const validation = validateCronExpression(newTask.cronExpression);
    setCronValidation(validation);
  }, [newTask.cronExpression, validateCronExpression]);

  // Fetch logs when task selected
  useEffect(() => {
    if (selectedTask) {
      fetchExecutionLogs(selectedTask.id);
    }
  }, [selectedTask, fetchExecutionLogs]);

  // Handle create task
  const handleCreateTask = useCallback(async () => {
    if (!newTask.name.trim() || !cronValidation.isValid) return;
    
    await createTask({
      name: newTask.name,
      description: newTask.description,
      type: newTask.type,
      cronExpression: newTask.cronExpression,
      enabled: newTask.enabled,
    });
    
    setShowCreateModal(false);
    setNewTask({
      name: '',
      description: '',
      type: 'email_digest',
      cronExpression: '0 0 * * *',
      enabled: false,
    });
  }, [newTask, cronValidation, createTask]);

  // Handle create from template
  const handleCreateFromTemplate = useCallback(async (templateId: string) => {
    await createFromTemplate(templateId);
    setShowCreateModal(false);
  }, [createFromTemplate]);

  // Handle toggle task
  const handleToggleTask = useCallback(async (taskId: string, enabled: boolean) => {
    await toggleTask(taskId, enabled);
  }, [toggleTask]);

  // Handle delete task
  const handleDeleteTask = useCallback(async (taskId: string) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      await deleteTask(taskId);
    }
  }, [deleteTask]);

  // Format date
  const formatDate = (dateString?: string) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString();
  };

  // Get status badge
  const getStatusBadge = (task: ScheduledTask) => {
    if (!task.enabled) {
      return <span className="status-badge disabled">Disabled</span>;
    }
    if (!task.lastRun) {
      return <span className="status-badge pending">Never Run</span>;
    }
    return task.lastRun.status === 'success'
      ? <span className="status-badge success">Success</span>
      : <span className="status-badge failed">Failed</span>;
  };

  // Get execution status color
  const getExecutionStatusColor = (status: TaskExecutionLog['status']) => {
    switch (status) {
      case 'success': return '#10b981';
      case 'failed': return '#ef4444';
      case 'partial': return '#f59e0b';
      case 'running': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  return (
    <div className="scheduler-board">
      <div className="board-header">
        <div className="header-left">
          <h2>Scheduled Tasks</h2>
          <div className="task-stats">
            <span className="stat">{stats.totalTasks} total</span>
            <span className="stat">{stats.activeTasks} active</span>
            <span className="stat">{stats.successRate.toFixed(1)}% success</span>
          </div>
        </div>
        <div className="header-actions">
          <button className="btn-secondary" onClick={fetchTasks}>
            Refresh
          </button>
          <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
            + New Task
          </button>
        </div>
      </div>

      <div className="board-tabs">
        <button
          className={`tab ${activeTab === 'tasks' ? 'active' : ''}`}
          onClick={() => setActiveTab('tasks')}
        >
          Tasks
        </button>
        <button
          className={`tab ${activeTab === 'logs' ? 'active' : ''}`}
          onClick={() => setActiveTab('logs')}
        >
          Execution Logs
        </button>
        <button
          className={`tab ${activeTab === 'templates' ? 'active' : ''}`}
          onClick={() => setActiveTab('templates')}
        >
          Templates
        </button>
      </div>

      <div className="board-content">
        {isLoading ? (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <p>Loading tasks...</p>
          </div>
        ) : activeTab === 'tasks' ? (
          <div className="tasks-list">
            {tasks.length === 0 ? (
              <div className="empty-state">
                <span className="empty-icon">📅</span>
                <p>No scheduled tasks</p>
                <button onClick={() => setShowCreateModal(true)}>Create your first task</button>
              </div>
            ) : (
              <div className="tasks-table">
                <table>
                  <thead>
                    <tr>
                      <th>Status</th>
                      <th>Task</th>
                      <th>Type</th>
                      <th>Schedule</th>
                      <th>Last Run</th>
                      <th>Next Run</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tasks.map(task => (
                      <tr
                        key={task.id}
                        className={selectedTask?.id === task.id ? 'selected' : ''}
                        onClick={() => onTaskSelect?.(task)}
                      >
                        <td>{getStatusBadge(task)}</td>
                        <td>
                          <div className="task-name">
                            <strong>{task.name}</strong>
                            <span className="task-desc">{task.description}</span>
                          </div>
                        </td>
                        <td>
                          <span className="type-badge">{task.type}</span>
                        </td>
                        <td>
                          <code className="cron-expression">{task.cronExpression}</code>
                        </td>
                        <td className="date-cell">
                          {task.lastRun ? (
                            <div>
                              <span>{formatDate(task.lastRun.completedAt)}</span>
                              <span className="run-duration">
                                {(task.lastRun.status === 'success' || task.lastRun.status === 'failed') &&
                                  `${(new Date(task.lastRun.completedAt!).getTime() - new Date(task.lastRun.startedAt).getTime()) / 1000}s`}
                              </span>
                            </div>
                          ) : (
                            '-'
                          )}
                        </td>
                        <td className="date-cell">
                          {task.nextRun ? formatDate(task.nextRun) : '-'}
                        </td>
                        <td className="actions-cell">
                          <button
                            className="action-btn"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleToggleTask(task.id, !task.enabled);
                            }}
                            title={task.enabled ? 'Disable' : 'Enable'}
                          >
                            {task.enabled ? '⏸️' : '▶️'}
                          </button>
                          <button
                            className="action-btn"
                            onClick={(e) => {
                              e.stopPropagation();
                              executeTask(task.id);
                            }}
                            title="Run Now"
                          >
                            ⚡
                          </button>
                          <button
                            className="action-btn danger"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteTask(task.id);
                            }}
                            title="Delete"
                          >
                            🗑️
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ) : activeTab === 'logs' ? (
          <div className="logs-panel">
            {selectedTask ? (
              <>
                <div className="logs-header">
                  <h3>Execution Logs: {selectedTask.name}</h3>
                </div>
                <div className="logs-list">
                  {executionLogs.length === 0 ? (
                    <p className="empty-logs">No execution logs found</p>
                  ) : (
                    executionLogs.map(log => (
                      <div key={log.id} className="log-item">
                        <div className="log-status" style={{ backgroundColor: getExecutionStatusColor(log.status) }}></div>
                        <div className="log-content">
                          <div className="log-header">
                            <span className="log-time">{formatDate(log.startedAt)}</span>
                            <span className="log-duration">{log.duration}s</span>
                          </div>
                          {log.output && <p className="log-output">{log.output}</p>}
                          {log.error && <p className="log-error">{log.error}</p>}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </>
            ) : (
              <div className="empty-state">
                <p>Select a task to view its execution logs</p>
              </div>
            )}
          </div>
        ) : (
          <div className="templates-panel">
            <div className="templates-grid">
              {templates.map(template => (
                <div key={template.id} className="template-card">
                  <div className="template-icon">
                    {template.type === 'email_digest' && '📧'}
                    {template.type === 'report' && '📊'}
                    {template.type === 'cleanup' && '🧹'}
                    {template.type === 'backup' && '💾'}
                    {template.type === 'notification' && '🔔'}
                  </div>
                  <h4>{template.name}</h4>
                  <p>{template.description}</p>
                  <div className="template-schedule">
                    <code>{template.cronPreset}</code>
                  </div>
                  <button
                    className="btn-secondary"
                    onClick={() => handleCreateFromTemplate(template.id)}
                  >
                    Use Template
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Create Task Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content large" onClick={(e) => e.stopPropagation()}>
            <h3>Create Scheduled Task</h3>
            
            <div className="form-row">
              <div className="form-group">
                <label>Task Name</label>
                <input
                  type="text"
                  value={newTask.name}
                  onChange={(e) => setNewTask(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Enter task name"
                />
              </div>
              
              <div className="form-group">
                <label>Task Type</label>
                <select
                  value={newTask.type}
                  onChange={(e) => setNewTask(prev => ({ ...prev, type: e.target.value as ScheduledTask['type'] }))}
                >
                  <option value="email_digest">Email Digest</option>
                  <option value="report">Report Generation</option>
                  <option value="cleanup">Cleanup Task</option>
                  <option value="backup">Database Backup</option>
                  <option value="notification">Notification</option>
                  <option value="custom">Custom</option>
                </select>
              </div>
            </div>
            
            <div className="form-group">
              <label>Description</label>
              <textarea
                value={newTask.description}
                onChange={(e) => setNewTask(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Enter description"
              />
            </div>
            
            <div className="form-group">
              <div className="form-label-row">
                <label>Cron Expression</label>
                <button
                  className="text-btn"
                  onClick={() => setShowCronHelper(!showCronHelper)}
                >
                  Cron Helper
                </button>
              </div>
              <input
                type="text"
                value={newTask.cronExpression}
                onChange={(e) => setNewTask(prev => ({ ...prev, cronExpression: e.target.value }))}
                className={!cronValidation.isValid ? 'invalid' : ''}
              />
              {cronValidation.isValid ? (
                <span className="cron-preview">{cronValidation.humanReadable}</span>
              ) : (
                <span className="cron-error">{cronValidation.error || 'Invalid cron expression'}</span>
              )}
            </div>
            
            {showCronHelper && (
              <div className="cron-helper">
                <h4>Common Cron Expressions</h4>
                <div className="cron-presets">
                  <button onClick={() => setNewTask(prev => ({ ...prev, cronExpression: '0 * * * *' }))}>
                    Every hour
                  </button>
                  <button onClick={() => setNewTask(prev => ({ ...prev, cronExpression: '0 0 * * *' }))}>
                    Daily at midnight
                  </button>
                  <button onClick={() => setNewTask(prev => ({ ...prev, cronExpression: '0 0 * * 1' }))}>
                    Weekly on Monday
                  </button>
                  <button onClick={() => setNewTask(prev => ({ ...prev, cronExpression: '0 0 1 * *' }))}>
                    Monthly on 1st
                  </button>
                </div>
              </div>
            )}
            
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={newTask.enabled}
                onChange={(e) => setNewTask(prev => ({ ...prev, enabled: e.target.checked }))}
              />
              Enable task immediately
            </label>
            
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setShowCreateModal(false)}>
                Cancel
              </button>
              <button
                className="btn-primary"
                onClick={handleCreateTask}
                disabled={!newTask.name.trim() || !cronValidation.isValid}
              >
                Create Task
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SchedulerBoard;
