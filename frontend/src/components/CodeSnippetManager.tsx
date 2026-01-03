import React, { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';

interface Snippet {
  snippet_id: string;
  title: string;
  code: string;
  description?: string;
  is_public: boolean;
  folder_id?: string;
  language: string;
  created_at: string;
  updated_at: string;
  execution_count: number;
}

interface Folder {
  folder_id: string;
  name: string;
  description?: string;
  parent_folder_id?: string;
  color: string;
  created_at: string;
}

interface SnippetVersion {
  version_id: string;
  version_number: number;
  title: string;
  code: string;
  description?: string;
  change_summary?: string;
  created_at: string;
  created_by: string;
}

interface TestCase {
  test_case_id: string;
  name: string;
  input_data?: string;
  expected_output: string;
  is_hidden: boolean;
  order_index: number;
  timeout_ms: number;
}

interface DebugSession {
  session_id: string;
  snippet_id: string;
  status: string;
  current_line: number;
  breakpoints: number[];
  variables: Record<string, any>;
  started_at: string;
}

const CodeSnippetManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'snippets' | 'folders' | 'history' | 'test_cases'>('snippets');
  const [snippets, setSnippets] = useState<Snippet[]>([]);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null);
  const [selectedSnippet, setSelectedSnippet] = useState<Snippet | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<SnippetVersion | null>(null);
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [debugSession, setDebugSession] = useState<DebugSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Editor state
  const [code, setCode] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  const [folderId, setFolderId] = useState('');

  // Modal states
  const [showFolderModal, setShowFolderModal] = useState(false);
  const [showVersionModal, setShowVersionModal] = useState(false);
  const [showTestCaseModal, setShowTestCaseModal] = useState(false);
  const [showDebugPanel, setShowDebugPanel] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Folder form
  const [newFolderName, setNewFolderName] = useState('');
  const [newFolderColor, setNewFolderColor] = useState('#3b82f6');

  // Test case form
  const [testCaseForm, setTestCaseForm] = useState({
    name: '',
    input_data: '',
    expected_output: '',
    is_hidden: false,
    timeout_ms: 5000
  });

  // Debug state
  const [breakpointLine, setBreakpointLine] = useState<number | null>(null);
  const [debugVariables, setDebugVariables] = useState<Record<string, any>>({});
  const [executionResult, setExecutionResult] = useState<any>(null);

  useEffect(() => {
    loadData();
  }, [selectedFolder]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [snippetsData, foldersData] = await Promise.all([
        apiService.getSnippets(selectedFolder || undefined),
        apiService.getFolders()
      ]);
      setSnippets(Array.isArray(snippetsData) ? snippetsData : []);
      setFolders(Array.isArray(foldersData) ? foldersData : []);
    } catch (error) {
      console.error('Error loading data:', error);
      setSnippets([]);
      setFolders([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSnippet = async () => {
    if (!title.trim()) {
      setMessage({ type: 'error', text: 'Title is required' });
      return;
    }
    if (!code.trim()) {
      setMessage({ type: 'error', text: 'Code content is required' });
      return;
    }

    try {
      setLoading(true);
      await apiService.saveSnippet({
        title,
        code,
        description,
        is_public: isPublic,
        folder_id: folderId || undefined,
        snippet_id: selectedSnippet?.snippet_id
      });
      setMessage({ type: 'success', text: 'Snippet saved successfully!' });
      loadData();
      if (!selectedSnippet) {
        setTitle('');
        setCode('');
        setDescription('');
      }
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to save snippet' });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSnippet = async () => {
    if (!selectedSnippet) return;

    try {
      setLoading(true);
      await apiService.deleteSnippet(selectedSnippet.snippet_id);
      setMessage({ type: 'success', text: 'Snippet deleted successfully!' });
      setSelectedSnippet(null);
      setShowDeleteConfirm(false);
      loadData();
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to delete snippet' });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) {
      setMessage({ type: 'error', text: 'Folder name is required' });
      return;
    }

    try {
      await apiService.createFolder(newFolderName, '', selectedFolder || undefined, newFolderColor);
      setMessage({ type: 'success', text: 'Folder created successfully!' });
      setShowFolderModal(false);
      setNewFolderName('');
      loadData();
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to create folder' });
    }
  };

  const handleExecuteCode = async () => {
    try {
      setLoading(true);
      const result = await apiService.executeCode(code);
      setExecutionResult(result);
      if (selectedSnippet) {
        loadData();
      }
    } catch (error: any) {
      setExecutionResult({ error: error.message || 'Execution failed' });
    } finally {
      setLoading(false);
    }
  };

  const handleVersionAction = async (action: string, params: any = {}) => {
    try {
      setLoading(true);
      const result = await apiService.snippetVersion(action, params);
      if (action === 'list' && selectedSnippet) {
        const versions = await apiService.snippetVersion('list', { snippet_id: selectedSnippet.snippet_id });
        // Handle version response
      }
      setMessage({ type: 'success', text: `Version ${action} successful!` });
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || `Version action failed` });
    } finally {
      setLoading(false);
    }
  };

  const handleTestCaseAction = async (action: string, params: any = {}) => {
    try {
      setLoading(true);
      await apiService.testCase(action, { snippet_id: selectedSnippet?.snippet_id, ...params });
      if (selectedSnippet && action === 'list') {
        const cases = await apiService.testCase('list', { snippet_id: selectedSnippet.snippet_id });
        setTestCases(Array.isArray(cases) ? cases : []);
      }
      setMessage({ type: 'success', text: `Test case ${action} successful!` });
      if (action === 'create') {
        setShowTestCaseModal(false);
        setTestCaseForm({ name: '', input_data: '', expected_output: '', is_hidden: false, timeout_ms: 5000 });
      }
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || `Test case action failed` });
    } finally {
      setLoading(false);
    }
  };

  const handleDebugAction = async (action: string, params: any = {}) => {
    try {
      setLoading(true);
      const result = await apiService.debugSession(action, { snippet_id: selectedSnippet?.snippet_id, ...params });
      if (action === 'create' && result.session) {
        setDebugSession(result.session);
        setShowDebugPanel(true);
      } else if (result.session) {
        setDebugSession(result.session);
      }
      if (result.result) {
        setExecutionResult(result.result);
      }
      if (result.variables) {
        setDebugVariables(result.variables);
      }
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || `Debug action failed` });
    } finally {
      setLoading(false);
    }
  };

  const handleAddBreakpoint = async () => {
    if (breakpointLine !== null && debugSession) {
      await handleDebugAction('breakpoint', { breakpoint_line: breakpointLine });
    }
  };

  const selectSnippet = async (snippet: Snippet) => {
    setSelectedSnippet(snippet);
    setTitle(snippet.title);
    setCode(snippet.code);
    setDescription(snippet.description || '');
    setIsPublic(snippet.is_public);
    setFolderId(snippet.folder_id || '');

    // Load test cases
    try {
      const cases = await apiService.testCase('list', { snippet_id: snippet.snippet_id });
      setTestCases(Array.isArray(cases) ? cases : []);
    } catch (error) {
      setTestCases([]);
    }
  };

  const renderFolderTree = (parentId: string | null, level: number = 0): React.ReactNode => {
    const childFolders = folders.filter(f => f.parent_folder_id === parentId);

    return (
      <>
        {childFolders.map(folder => (
          <div key={folder.folder_id} style={{ marginLeft: level * 16 }}>
            <button
              className={`folder-item ${selectedFolder === folder.folder_id ? 'selected' : ''}`}
              onClick={() => setSelectedFolder(selectedFolder === folder.folder_id ? null : folder.folder_id)}
            >
              <span className="folder-color" style={{ backgroundColor: folder.color }}></span>
              {folder.name}
            </button>
            {renderFolderTree(folder.folder_id, level + 1)}
          </div>
        ))}
      </>
    );
  };

  const renderSnippetsList = () => (
    <div className="snippets-list">
      {loading ? (
        <div className="loading-placeholder">Loading...</div>
      ) : snippets.length === 0 ? (
        <div className="empty-placeholder">
          <p>No snippets found</p>
          <p className="hint">Create a new snippet to get started</p>
        </div>
      ) : (
        snippets.map(snippet => (
          <div
            key={snippet.snippet_id}
            className={`snippet-item ${selectedSnippet?.snippet_id === snippet.snippet_id ? 'selected' : ''}`}
            onClick={() => selectSnippet(snippet)}
          >
            <div className="snippet-icon">{snippet.language === 'jac' ? '📝' : '💻'}</div>
            <div className="snippet-info">
              <div className="snippet-title">{snippet.title}</div>
              <div className="snippet-meta">
                {snippet.execution_count} executions • {new Date(snippet.updated_at).toLocaleDateString()}
              </div>
            </div>
            {snippet.is_public && <span className="public-badge">Public</span>}
          </div>
        ))
      )}
    </div>
  );

  const renderEditor = () => (
    <div className="snippet-editor">
      <div className="editor-header">
        <input
          type="text"
          className="title-input"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Snippet title..."
        />
        <div className="editor-actions">
          <button className="btn-icon" onClick={() => setShowFolderModal(true)} title="Create Folder">
            📁
          </button>
          <button className="btn-icon" onClick={() => setShowVersionModal(true)} title="Version History">
            📜
          </button>
          <button className="btn-icon" onClick={() => setShowTestCaseModal(true)} title="Test Cases">
            🧪
          </button>
          <button className="btn-icon" onClick={() => handleDebugAction('create')} title="Debug">
            🐛
          </button>
        </div>
      </div>

      <div className="editor-meta">
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Description (optional)..."
          className="description-input"
        />
        <div className="meta-row">
          <select value={folderId} onChange={(e) => setFolderId(e.target.value)}>
            <option value="">No Folder</option>
            {folders.map(f => (
              <option key={f.folder_id} value={f.folder_id}>{f.name}</option>
            ))}
          </select>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={isPublic}
              onChange={(e) => setIsPublic(e.target.checked)}
            />
            Public
          </label>
        </div>
      </div>

      <div className="code-editor-container">
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="// Write your Jac code here..."
          className="code-editor"
          spellCheck={false}
        />
      </div>

      <div className="editor-footer">
        <button className="btn btn-secondary" onClick={handleExecuteCode} disabled={loading}>
          ▶ Run
        </button>
        <button className="btn btn-primary" onClick={handleSaveSnippet} disabled={loading}>
          💾 Save
        </button>
        {selectedSnippet && (
          <button className="btn btn-danger" onClick={() => setShowDeleteConfirm(true)}>
            🗑️ Delete
          </button>
        )}
      </div>

      {executionResult && (
        <div className={`execution-result ${executionResult.error ? 'error' : 'success'}`}>
          <h4>Execution Result</h4>
          {executionResult.error ? (
            <pre className="error-output">{executionResult.error}</pre>
          ) : (
            <>
              <pre>{executionResult.stdout || executionResult.output || 'No output'}</pre>
              {executionResult.stderr && (
                <pre className="error-output">{executionResult.stderr}</pre>
              )}
              <div className="execution-meta">
                Time: {executionResult.execution_time_ms}ms
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );

  const renderDebugPanel = () => (
    <div className="debug-panel">
      <div className="debug-header">
        <h4>🐛 Debug Session</h4>
        <button onClick={() => setShowDebugPanel(false)}>×</button>
      </div>

      <div className="debug-controls">
        <button onClick={() => handleDebugAction('step', { command: 'step', current_line: debugSession?.current_line })}>
          Step
        </button>
        <button onClick={() => handleDebugAction('continue', { current_line: debugSession?.current_line })}>
          Continue
        </button>
        <button onClick={() => handleDebugAction('evaluate', { command: '', current_line: debugSession?.current_line })}>
          Evaluate
        </button>
        <button onClick={() => handleDebugAction('end')}>
          End
        </button>
      </div>

      <div className="breakpoint-input">
        <input
          type="number"
          placeholder="Line #"
          value={breakpointLine || ''}
          onChange={(e) => setBreakpointLine(parseInt(e.target.value) || null)}
        />
        <button onClick={handleAddBreakpoint}>Add Breakpoint</button>
      </div>

      <div className="variables-panel">
        <h5>Variables</h5>
        <pre>{JSON.stringify(debugVariables, null, 2)}</pre>
      </div>

      <div className="breakpoints-list">
        <h5>Breakpoints</h5>
        {debugSession?.breakpoints?.map((line, idx) => (
          <span key={idx} className="breakpoint-tag">Line {line}</span>
        ))}
      </div>
    </div>
  );

  return (
    <div className="snippet-manager">
      {message && (
        <div className={`manager-message ${message.type}`}>
          {message.text}
          <button onClick={() => setMessage(null)}>×</button>
        </div>
      )}

      <div className="manager-layout">
        <aside className="manager-sidebar">
          <div className="sidebar-header">
            <button
              className={activeTab === 'snippets' ? 'active' : ''}
              onClick={() => setActiveTab('snippets')}
            >
              📝 Snippets
            </button>
            <button
              className={activeTab === 'folders' ? 'active' : ''}
              onClick={() => setActiveTab('folders')}
            >
              📁 Folders
            </button>
          </div>

          <div className="folders-section">
            <div className="section-header">
              <span>Folders</span>
              <button onClick={() => setShowFolderModal(true)}>+</button>
            </div>
            <div className="folders-tree">
              <button
                className={`folder-item ${selectedFolder === null ? 'selected' : ''}`}
                onClick={() => setSelectedFolder(null)}
              >
                📂 All Snippets
              </button>
              {renderFolderTree(null)}
            </div>
          </div>

          {renderSnippetsList()}
        </aside>

        <main className="manager-main">
          {showDebugPanel && debugSession ? renderDebugPanel() : renderEditor()}
        </main>
      </div>

      {showFolderModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Create New Folder</h3>
            <input
              type="text"
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              placeholder="Folder name..."
            />
            <div className="color-picker">
              <label>Color:</label>
              <input
                type="color"
                value={newFolderColor}
                onChange={(e) => setNewFolderColor(e.target.value)}
              />
            </div>
            <div className="modal-actions">
              <button onClick={() => setShowFolderModal(false)}>Cancel</button>
              <button onClick={handleCreateFolder}>Create</button>
            </div>
          </div>
        </div>
      )}

      {showTestCaseModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Add Test Case</h3>
            <input
              type="text"
              value={testCaseForm.name}
              onChange={(e) => setTestCaseForm(prev => ({ ...prev, name: e.target.value }))}
              placeholder="Test name..."
            />
            <textarea
              value={testCaseForm.input_data}
              onChange={(e) => setTestCaseForm(prev => ({ ...prev, input_data: e.target.value }))}
              placeholder="Input data..."
            />
            <textarea
              value={testCaseForm.expected_output}
              onChange={(e) => setTestCaseForm(prev => ({ ...prev, expected_output: e.target.value }))}
              placeholder="Expected output..."
            />
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={testCaseForm.is_hidden}
                onChange={(e) => setTestCaseForm(prev => ({ ...prev, is_hidden: e.target.checked }))}
              />
              Hidden test case
            </label>
            <div className="modal-actions">
              <button onClick={() => setShowTestCaseModal(false)}>Cancel</button>
              <button onClick={() => handleTestCaseAction('create', testCaseForm)}>Create</button>
            </div>
          </div>
        </div>
      )}

      {showDeleteConfirm && (
        <div className="modal-overlay">
          <div className="modal confirmation">
            <h3>Delete Snippet</h3>
            <p>Are you sure you want to delete "{selectedSnippet?.title}"? This action cannot be undone.</p>
            <div className="modal-actions">
              <button onClick={() => setShowDeleteConfirm(false)}>Cancel</button>
              <button onClick={handleDeleteSnippet} className="danger">Delete</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CodeSnippetManager;
