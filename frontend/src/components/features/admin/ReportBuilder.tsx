import React, { useState, useCallback, useEffect } from 'react';
import { useReportBuilder, ReportMetric, ReportDimension, ReportFilter, ReportQuery } from '../../contexts/ReportBuilderContext';
import './ReportBuilder.css';

interface ReportBuilderProps {
  reportId?: string;
  onSave?: (reportId: string) => void;
  onExport?: (format: 'pdf' | 'csv' | 'excel') => void;
}

export function ReportBuilder({
  reportId,
  onSave,
  onExport,
}: ReportBuilderProps) {
  const {
    query,
    setQuery,
    resetQuery,
    visualizations,
    addVisualization,
    availableMetrics,
    availableDimensions,
    data,
    isLoading,
    error,
    executeQuery,
    refreshData,
    exportJob,
    startExport,
    savedReports,
    loadSavedReport,
    saveCurrentReport,
    getFieldLabel,
    formatValue,
  } = useReportBuilder();

  const [activeTab, setActiveTab] = useState<'data' | 'visualize' | 'schedule'>('data');
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [reportName, setReportName] = useState('');
  const [reportDescription, setReportDescription] = useState('');
  const [showAddMetric, setShowAddMetric] = useState(false);
  const [showAddDimension, setShowAddDimension] = useState(false);
  const [showAddFilter, setShowAddFilter] = useState(false);

  // Load report if ID provided
  useEffect(() => {
    if (reportId) {
      loadSavedReport(reportId);
    }
  }, [reportId, loadSavedReport]);

  // Add metric to query
  const handleAddMetric = useCallback((metric: ReportMetric) => {
    if (!query.metrics.includes(metric.field)) {
      setQuery({ metrics: [...query.metrics, metric.field] });
    }
    setShowAddMetric(false);
  }, [query.metrics, setQuery]);

  // Add dimension to query
  const handleAddDimension = useCallback((dimension: ReportDimension) => {
    if (!query.dimensions.includes(dimension.field)) {
      setQuery({ dimensions: [...query.dimensions, dimension.field] });
    }
    setShowAddDimension(false);
  }, [query.dimensions, setQuery]);

  // Add filter to query
  const handleAddFilter = useCallback((filter: Omit<ReportFilter, 'id'>) => {
    const newFilter: ReportFilter = {
      ...filter,
      id: `filter-${Date.now()}`,
    };
    setQuery({ filters: [...query.filters, newFilter] });
    setShowAddFilter(false);
  }, [query.filters, setQuery]);

  // Remove metric
  const handleRemoveMetric = useCallback((field: string) => {
    setQuery({ metrics: query.metrics.filter(m => m !== field) });
  }, [query.metrics, setQuery]);

  // Remove dimension
  const handleRemoveDimension = useCallback((field: string) => {
    setQuery({ dimensions: query.dimensions.filter(d => d !== field) });
  }, [query.dimensions, setQuery]);

  // Remove filter
  const handleRemoveFilter = useCallback((filterId: string) => {
    setQuery({ filters: query.filters.filter(f => f.id !== filterId) });
  }, [query.filters, setQuery]);

  // Handle save
  const handleSave = useCallback(async () => {
    if (!reportName.trim()) return;
    const saved = await saveCurrentReport(reportName, reportDescription, false);
    setShowSaveModal(false);
    onSave?.(saved.id);
  }, [reportName, reportDescription, saveCurrentReport, onSave]);

  // Handle export
  const handleExport = useCallback(async (format: 'pdf' | 'csv' | 'excel') => {
    await startExport(format);
    onExport?.(format);
  }, [startExport, onExport]);

  return (
    <div className="report-builder">
      <div className="builder-header">
        <div className="header-left">
          <h2>Report Builder</h2>
          <span className="execution-time">
            {data && `Last executed: ${data.executionTime}s`}
          </span>
        </div>
        <div className="header-actions">
          <button className="btn-secondary" onClick={resetQuery}>
            Reset
          </button>
          <button className="btn-secondary" onClick={refreshData}>
            Refresh
          </button>
          <button className="btn-secondary" onClick={() => setShowSaveModal(true)}>
            Save
          </button>
          <button className="btn-primary" onClick={() => executeQuery()}>
            Run Query
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setQuery({ filters: [] })}>Clear Filters</button>
        </div>
      )}

      <div className="builder-tabs">
        <button
          className={`tab ${activeTab === 'data' ? 'active' : ''}`}
          onClick={() => setActiveTab('data')}
        >
          Data
        </button>
        <button
          className={`tab ${activeTab === 'visualize' ? 'active' : ''}`}
          onClick={() => setActiveTab('visualize')}
        >
          Visualize
        </button>
        <button
          className={`tab ${activeTab === 'schedule' ? 'active' : ''}`}
          onClick={() => setActiveTab('schedule')}
        >
          Schedule
        </button>
      </div>

      <div className="builder-content">
        {activeTab === 'data' && (
          <div className="data-tab">
            <div className="query-panel">
              {/* Metrics */}
              <div className="query-section">
                <div className="section-header">
                  <h3>Metrics</h3>
                  <button onClick={() => setShowAddMetric(true)}>+ Add</button>
                </div>
                <div className="selected-items">
                  {query.metrics.length === 0 ? (
                    <p className="empty-hint">No metrics selected</p>
                  ) : (
                    query.metrics.map(field => {
                      const metric = availableMetrics.find(m => m.field === field);
                      return metric ? (
                        <div key={field} className="selected-item">
                          <span>{metric.name}</span>
                          <button onClick={() => handleRemoveMetric(field)}>×</button>
                        </div>
                      ) : null;
                    })
                  )}
                </div>
              </div>

              {/* Dimensions */}
              <div className="query-section">
                <div className="section-header">
                  <h3>Dimensions</h3>
                  <button onClick={() => setShowAddDimension(true)}>+ Add</button>
                </div>
                <div className="selected-items">
                  {query.dimensions.length === 0 ? (
                    <p className="empty-hint">No dimensions selected</p>
                  ) : (
                    query.dimensions.map(field => {
                      const dimension = availableDimensions.find(d => d.field === field);
                      return dimension ? (
                        <div key={field} className="selected-item">
                          <span>{dimension.name}</span>
                          <button onClick={() => handleRemoveDimension(field)}>×</button>
                        </div>
                      ) : null;
                    })
                  )}
                </div>
              </div>

              {/* Filters */}
              <div className="query-section">
                <div className="section-header">
                  <h3>Filters</h3>
                  <button onClick={() => setShowAddFilter(true)}>+ Add</button>
                </div>
                <div className="selected-items">
                  {query.filters.length === 0 ? (
                    <p className="empty-hint">No filters applied</p>
                  ) : (
                    query.filters.map(filter => (
                      <div key={filter.id} className="selected-item filter-item">
                        <span>{getFieldLabel(filter.field)} {filter.operator} {String(filter.value)}</span>
                        <button onClick={() => handleRemoveFilter(filter.id)}>×</button>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Time Range */}
              <div className="query-section">
                <h3>Time Range</h3>
                <select
                  value={query.timeRange.type === 'preset' ? `preset-${query.timeRange.preset}` : 'custom'}
                  onChange={(e) => {
                    if (e.target.value.startsWith('preset-')) {
                      setQuery({
                        timeRange: {
                          type: 'preset',
                          preset: e.target.value.replace('preset-', '') as ReportQuery['timeRange']['preset'],
                        },
                      });
                    } else {
                      setQuery({
                        timeRange: { type: 'custom' },
                      });
                    }
                  }}
                >
                  <option value="preset-today">Today</option>
                  <option value="preset-yesterday">Yesterday</option>
                  <option value="preset-last_7_days">Last 7 Days</option>
                  <option value="preset-last_30_days">Last 30 Days</option>
                  <option value="preset-this_month">This Month</option>
                  <option value="preset-last_month">Last Month</option>
                  <option value="preset-this_year">This Year</option>
                  <option value="custom">Custom Range</option>
                </select>
              </div>
            </div>

            {/* Results */}
            <div className="results-panel">
              {isLoading ? (
                <div className="loading-state">
                  <div className="loading-spinner"></div>
                  <p>Executing query...</p>
                </div>
              ) : data ? (
                <>
                  <div className="results-header">
                    <span>{data.totalRows} rows returned</span>
                    <div className="export-buttons">
                      <button onClick={() => handleExport('csv')}>CSV</button>
                      <button onClick={() => handleExport('excel')}>Excel</button>
                      <button onClick={() => handleExport('pdf')}>PDF</button>
                    </div>
                  </div>
                  <div className="data-table-container">
                    <table className="data-table">
                      <thead>
                        <tr>
                          {data.columns.map(col => (
                            <th key={col.id}>{col.header}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {data.rows.map((row, i) => (
                          <tr key={i}>
                            {data.columns.map(col => {
                              const value = row[col.field];
                              const metric = availableMetrics.find(m => m.field === col.field);
                              return (
                                <td key={col.id}>
                                  {metric ? formatValue(value, metric.format) : String(value)}
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  <span className="empty-icon">📊</span>
                  <p>Run a query to see results</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'visualize' && (
          <div className="visualize-tab">
            <div className="visualization-sidebar">
              <button onClick={() => addVisualization({ type: 'bar_chart', title: 'New Chart' })}>
                + Add Bar Chart
              </button>
              <button onClick={() => addVisualization({ type: 'line_chart', title: 'New Line Chart' })}>
                + Add Line Chart
              </button>
              <button onClick={() => addVisualization({ type: 'pie_chart', title: 'New Pie Chart' })}>
                + Add Pie Chart
              </button>
            </div>
            <div className="visualization-canvas">
              {visualizations.length === 0 ? (
                <div className="empty-state">
                  <span className="empty-icon">📈</span>
                  <p>Add visualizations to see them here</p>
                </div>
              ) : (
                visualizations.map((viz, i) => (
                  <div key={i} className="visualization-card">
                    <h4>{viz.title}</h4>
                    <div className="viz-placeholder">
                      {viz.type} visualization
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {activeTab === 'schedule' && (
          <div className="schedule-tab">
            <p className="schedule-info">
              Schedule this report to run automatically and send to recipients.
            </p>
            <div className="schedule-options">
              <label>
                <input type="checkbox" />
                Enable Schedule
              </label>
              <div className="schedule-settings">
                <label>Frequency</label>
                <select>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
              <div className="schedule-settings">
                <label>Time</label>
                <input type="time" defaultValue="08:00" />
              </div>
              <div className="schedule-settings">
                <label>Format</label>
                <select>
                  <option value="pdf">PDF</option>
                  <option value="csv">CSV</option>
                  <option value="excel">Excel</option>
                </select>
              </div>
              <div className="schedule-settings">
                <label>Recipients</label>
                <input type="text" placeholder="email@example.com, ..." />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Add Metric Modal */}
      {showAddMetric && (
        <div className="modal-overlay" onClick={() => setShowAddMetric(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Add Metric</h3>
            <div className="modal-list">
              {availableMetrics.map(metric => (
                <button
                  key={metric.id}
                  className={query.metrics.includes(metric.field) ? 'selected' : ''}
                  onClick={() => handleAddMetric(metric)}
                  disabled={query.metrics.includes(metric.field)}
                >
                  <span className="metric-name">{metric.name}</span>
                  <span className="metric-agg">({metric.aggregation})</span>
                </button>
              ))}
            </div>
            <button className="close-btn" onClick={() => setShowAddMetric(false)}>Cancel</button>
          </div>
        </div>
      )}

      {/* Add Dimension Modal */}
      {showAddDimension && (
        <div className="modal-overlay" onClick={() => setShowAddDimension(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Add Dimension</h3>
            <div className="modal-list">
              {availableDimensions.map(dimension => (
                <button
                  key={dimension.id}
                  className={query.dimensions.includes(dimension.field) ? 'selected' : ''}
                  onClick={() => handleAddDimension(dimension)}
                  disabled={query.dimensions.includes(dimension.field)}
                >
                  {dimension.name}
                </button>
              ))}
            </div>
            <button className="close-btn" onClick={() => setShowAddDimension(false)}>Cancel</button>
          </div>
        </div>
      )}

      {/* Save Modal */}
      {showSaveModal && (
        <div className="modal-overlay" onClick={() => setShowSaveModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Save Report</h3>
            <div className="form-group">
              <label>Report Name</label>
              <input
                type="text"
                value={reportName}
                onChange={(e) => setReportName(e.target.value)}
                placeholder="Enter report name"
              />
            </div>
            <div className="form-group">
              <label>Description</label>
              <textarea
                value={reportDescription}
                onChange={(e) => setReportDescription(e.target.value)}
                placeholder="Enter description"
              />
            </div>
            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setShowSaveModal(false)}>
                Cancel
              </button>
              <button className="btn-primary" onClick={handleSave} disabled={!reportName.trim()}>
                Save Report
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Export Progress */}
      {exportJob && exportJob.status === 'processing' && (
        <div className="export-progress-overlay">
          <div className="export-progress-content">
            <h3>Generating Report</h3>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${exportJob.progress}%` }}></div>
            </div>
            <p>{exportJob.progress}% complete</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default ReportBuilder;
