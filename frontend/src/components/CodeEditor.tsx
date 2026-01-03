/**
 * JAC Code Editor Component
 * 
 * A full-featured code editor for Jac language with:
 * - Monaco Editor integration
 * - Syntax highlighting for Jac language
 * - Code execution
 * - Save/Load snippets
 * - Execution history
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { 
  Play, 
  Save, 
  FolderOpen, 
  Clock, 
  Trash2, 
  Copy, 
  Check, 
  X,
  Terminal,
  AlertCircle,
  FileCode,
  History,
  ChevronDown,
  FolderPlus,
  MoreVertical
} from 'lucide-react';
import { apiService } from '../api';

// Jac language keywords for syntax highlighting
const JAC_KEYWORDS = [
  'walker', 'node', 'edge', 'can', 'has', 'with', 'import',
  'if', 'else', 'for', 'while', 'return', 'break', 'continue',
  'try', 'except', 'finally', 'raise', 'assert', 'pass',
  'global', 'nonlocal', 'del', 'yield', 'from', 'as', 'in',
  'is', 'not', 'and', 'or', 'True', 'False', 'None',
  'report', 'ignore', 'spawn', 'here', 'root', 'super',
  'static', 'public', 'private', 'protected'
];

const JAC_TYPES = [
  'str', 'int', 'float', 'bool', 'list', 'dict', 'tuple',
  'set', 'any', 'void', 'null', 'async', 'await'
];

// Default Jac code template
const DEFAULT_CODE = `walker init {
    has greeting: str = "Hello, Jeseci Academy!";
    
    can init with entry {
        print(greeting);
        print("Welcome to Jac Language Programming!");
    }
}

// You can define more walkers here
walker calculate_sum {
    has a: int = 10;
    has b: int = 20;
    
    can calculate with entry {
        result = self.a + self.b;
        print(f"Sum: {self.a} + {self.b} = {result}");
        report result;
    }
}`;

interface Snippet {
  id: string;
  title: string;
  code_content: string;
  language: string;
  description?: string;
  is_public: boolean;
  folder_id?: string;
  execution_count: number;
  last_executed_at?: string;
  created_at: string;
  updated_at: string;
}

interface ExecutionResult {
  success: boolean;
  stdout: string;
  stderr: string;
  execution_time_ms: number;
  status: string;
  error_type?: string;
  line_number?: number;
}

interface Folder {
  id: string;
  name: string;
  description?: string;
  parent_folder_id?: string;
  color: string;
}

const CodeEditor: React.FC = () => {
  // State
  const [code, setCode] = useState<string>(DEFAULT_CODE);
  const [output, setOutput] = useState<string>('');
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [showHistory, setShowHistory] = useState<boolean>(false);
  const [showSnippets, setShowSnippets] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'output' | 'ai'>('output');
  const [executionHistory, setExecutionHistory] = useState<any[]>([]);
  const [snippets, setSnippets] = useState<Snippet[]>([]);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [selectedFolder, setSelectedFolder] = useState<string>('');
  const [saveTitle, setSaveTitle] = useState<string>('');
  const [saveDescription, setSaveDescription] = useState<string>('');
  const [showSaveModal, setShowSaveModal] = useState<boolean>(false);
  const [showNewFolderModal, setShowNewFolderModal] = useState<boolean>(false);
  const [newFolderName, setNewFolderName] = useState<string>('');
  const [currentSnippetId, setCurrentSnippetId] = useState<string>('');
  const [status, setStatus] = useState<string>('ready');
  
  const editorRef = useRef<any>(null);

  // Load data on mount
  useEffect(() => {
    loadSnippets();
    loadFolders();
    loadExecutionHistory();
  }, []);

  // Load snippets from API
  const loadSnippets = async () => {
    try {
      const response = await apiService.getUserSnippets();
      if (response.success) {
        setSnippets(response.snippets);
      }
    } catch (error) {
      console.error('Error loading snippets:', error);
    }
  };

  // Load folders from API
  const loadFolders = async () => {
    try {
      const response = await apiService.getCodeFolders();
      if (response.success) {
        setFolders(response.folders);
      }
    } catch (error) {
      console.error('Error loading folders:', error);
    }
  };

  // Load execution history
  const loadExecutionHistory = async () => {
    try {
      const response = await apiService.getExecutionHistory();
      if (response.success) {
        setExecutionHistory(response.history);
      }
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  // Handle editor mount
  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor;
  };

  // Execute code
  const executeCode = async () => {
    setIsExecuting(true);
    setOutput('');
    setStatus('executing');

    try {
      const result = await apiService.executeJacCode(code);

      if (result.success) {
        const outputText = `✅ Execution successful!\n\n${result.output || 'No output'}`;
        setOutput(outputText);
        setStatus('success');
      } else {
        let errorText = `❌ Error: ${result.error || 'Unknown error'}`;
        setOutput(errorText);
        setStatus('error');
      }

      // Reload history
      loadExecutionHistory();

    } catch (error) {
      setOutput(`❌ Failed to execute code: ${error}`);
      setStatus('error');
    } finally {
      setIsExecuting(false);
    }
  };

  // Save snippet
  const saveSnippet = async () => {
    if (!saveTitle.trim()) {
      alert('Please enter a title for the snippet');
      return;
    }

    setIsSaving(true);
    try {
      const response = await apiService.saveSnippet({
        title: saveTitle,
        code: code,
        description: saveDescription,
        snippet_id: currentSnippetId || undefined
      });

      if (response.success) {
        setShowSaveModal(false);
        setSaveTitle('');
        setSaveDescription('');
        setCurrentSnippetId(response.snippet.id);
        loadSnippets();
      } else {
        alert('Failed to save snippet: ' + response.error);
      }
    } catch (error) {
      alert('Error saving snippet: ' + error);
    } finally {
      setIsSaving(false);
    }
  };

  // Create new folder
  const createFolder = async () => {
    if (!newFolderName.trim()) {
      alert('Please enter a folder name');
      return;
    }

    try {
      const response = await apiService.createFolder({
        name: newFolderName
      });

      if (response.success) {
        setShowNewFolderModal(false);
        setNewFolderName('');
        loadFolders();
      } else {
        alert('Failed to create folder: ' + response.error);
      }
    } catch (error) {
      alert('Error creating folder: ' + error);
    }
  };

  // Load snippet
  const loadSnippet = (snippet: Snippet) => {
    setCode(snippet.code_content);
    setCurrentSnippetId(snippet.id);
    setSaveTitle(snippet.title);
    setSaveDescription(snippet.description || '');
    setShowSnippets(false);
  };

  // Delete snippet
  const deleteSnippet = async (snippetId: string) => {
    if (!confirm('Are you sure you want to delete this snippet?')) return;

    try {
      const response = await apiService.deleteSnippet(snippetId);
      if (response.success) {
        loadSnippets();
        if (currentSnippetId === snippetId) {
          setCurrentSnippetId('');
          setSaveTitle('');
        }
      } else {
        alert('Failed to delete snippet');
      }
    } catch (error) {
      alert('Error deleting snippet: ' + error);
    }
  };

  // Format code
  const formatCode = () => {
    if (editorRef.current) {
      editorRef.current.getAction('editor.action.formatDocument').run();
    }
  };

  // Clear output
  const clearOutput = () => {
    setOutput('');
    setStatus('ready');
  };

  return (
    <div className="flex h-full bg-gray-900 text-white">
      {/* Left Sidebar - Snippets */}
      <div className={`${showSnippets ? 'w-64' : 'w-0'} transition-all duration-300 overflow-hidden border-r border-gray-700 flex flex-col`}>
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <h3 className="font-semibold text-lg flex items-center gap-2">
            <FileCode size={18} />
            Snippets
          </h3>
          <button 
            onClick={() => setShowSnippets(false)}
            className="text-gray-400 hover:text-white"
          >
            <X size={18} />
          </button>
        </div>
        
        {/* Folder filter */}
        <div className="p-3 border-b border-gray-700">
          <select 
            className="w-full bg-gray-800 border border-gray-600 rounded px-3 py-2 text-sm"
            value={selectedFolder}
            onChange={(e) => setSelectedFolder(e.target.value)}
          >
            <option value="">All Snippets</option>
            {folders.map(folder => (
              <option key={folder.id} value={folder.id}>{folder.name}</option>
            ))}
          </select>
        </div>
        
        {/* Snippets list */}
        <div className="flex-1 overflow-y-auto">
          {snippets
            .filter(s => !selectedFolder || s.folder_id === selectedFolder)
            .map(snippet => (
              <div 
                key={snippet.id}
                className={`p-3 border-b border-gray-800 cursor-pointer hover:bg-gray-800 ${
                  currentSnippetId === snippet.id ? 'bg-gray-800 border-l-2 border-l-blue-500' : ''
                }`}
                onClick={() => loadSnippet(snippet)}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-sm truncate">{snippet.title}</span>
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteSnippet(snippet.id);
                    }}
                    className="text-gray-500 hover:text-red-400"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {new Date(snippet.updated_at).toLocaleDateString()}
                </div>
              </div>
            ))}
        </div>
        
        {/* New snippet button */}
        <div className="p-3 border-t border-gray-700">
          <button 
            onClick={() => {
              setCode(DEFAULT_CODE);
              setCurrentSnippetId('');
              setSaveTitle('');
              setSaveDescription('');
            }}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded flex items-center justify-center gap-2"
          >
            <FileCode size={16} />
            New Snippet
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <div className="bg-gray-800 border-b border-gray-700 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* Toggle snippets sidebar */}
            <button 
              onClick={() => setShowSnippets(!showSnippets)}
              className={`p-2 rounded hover:bg-gray-700 ${showSnippets ? 'text-blue-400' : 'text-gray-400'}`}
              title="Toggle Snippets"
            >
              <FolderOpen size={18} />
            </button>
            
            {/* Toggle history */}
            <button 
              onClick={() => setShowHistory(!showHistory)}
              className={`p-2 rounded hover:bg-gray-700 ${showHistory ? 'text-blue-400' : 'text-gray-400'}`}
              title="Execution History"
            >
              <History size={18} />
            </button>
            
            {/* Format code */}
            <button 
              onClick={formatCode}
              className="p-2 rounded hover:bg-gray-700 text-gray-400 hover:text-white"
              title="Format Code"
            >
              <FileCode size={18} />
            </button>
          </div>
          
          {/* Action buttons */}
          <div className="flex items-center gap-2">
            {/* Save button */}
            <button 
              onClick={() => setShowSaveModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm"
            >
              <Save size={16} />
              Save
            </button>
            
            {/* Execute button */}
            <button 
              onClick={executeCode}
              disabled={isExecuting}
              className={`flex items-center gap-2 px-6 py-2 rounded font-medium ${
                isExecuting 
                  ? 'bg-yellow-600 cursor-not-allowed' 
                  : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              {isExecuting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Running...
                </>
              ) : (
                <>
                  <Play size={16} />
                  Run Code
                </>
              )}
            </button>
          </div>
        </div>
        
        {/* Editor and Output */}
        <div className="flex-1 flex overflow-hidden">
          {/* Code Editor */}
          <div className="flex-1 flex flex-col">
            <Editor
              height="100%"
              defaultLanguage="python"
              value={code}
              onChange={(value) => setCode(value || '')}
              onMount={handleEditorDidMount}
              theme="vs-dark"
              options={{
                fontSize: 14,
                fontFamily: "'Fira Code', 'JetBrains Mono', monospace",
                minimap: { enabled: true },
                scrollBeyondLastLine: false,
                automaticLayout: true,
                tabSize: 4,
                wordWrap: 'on',
                lineNumbers: 'on',
                renderLineHighlight: 'all',
                selectOnLineNumbers: true,
                roundedSelection: true,
                cursorBlinking: 'smooth',
                cursorSmoothCaretAnimation: 'on',
                smoothScrolling: true,
                padding: { top: 16, bottom: 16 }
              }}
            />
          </div>
          
          {/* Output Panel */}
          {showHistory ? (
            /* Execution History Panel */
            <div className="w-80 border-l border-gray-700 flex flex-col bg-gray-850">
              <div className="p-4 border-b border-gray-700">
                <h3 className="font-semibold flex items-center gap-2">
                  <Clock size={18} />
                  Execution History
                </h3>
              </div>
              <div className="flex-1 overflow-y-auto">
                {executionHistory.length === 0 ? (
                  <div className="p-4 text-gray-500 text-center">
                    No execution history yet
                  </div>
                ) : (
                  executionHistory.map((item, index) => (
                    <div 
                      key={item.id || index}
                      className="p-3 border-b border-gray-800 cursor-pointer hover:bg-gray-800"
                      onClick={() => {
                        setCode(item.code_content);
                        setOutput(item.output);
                        setStatus(item.status);
                        setShowHistory(false);
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <span className={`text-xs px-2 py-1 rounded ${
                          item.status === 'success' ? 'bg-green-900 text-green-300' : 
                          item.status === 'error' ? 'bg-red-900 text-red-300' : 
                          'bg-yellow-900 text-yellow-300'
                        }`}>
                          {item.status}
                        </span>
                        <span className="text-xs text-gray-500">
                          {item.execution_time_ms}ms
                        </span>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {new Date(item.created_at).toLocaleString()}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          ) : (
            /* Output Panel */
            <div className="w-80 border-l border-gray-700 flex flex-col bg-gray-850">
              {/* Tabs */}
              <div className="flex border-b border-gray-700">
                <button 
                  onClick={() => setActiveTab('output')}
                  className={`flex-1 py-3 text-sm font-medium ${
                    activeTab === 'output' 
                      ? 'text-blue-400 border-b-2 border-blue-400' 
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  <Terminal size={16} className="inline mr-2" />
                  Output
                </button>
                <button 
                  onClick={() => setActiveTab('ai')}
                  className={`flex-1 py-3 text-sm font-medium ${
                    activeTab === 'ai' 
                      ? 'text-blue-400 border-b-2 border-blue-400' 
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  AI Help
                </button>
              </div>
              
              {/* Output content */}
              <div className="flex-1 overflow-y-auto p-4 font-mono text-sm">
                {output ? (
                  <div className="whitespace-pre-wrap">
                    <div className={`mb-4 ${
                      status === 'success' ? 'text-green-400' : 
                      status === 'error' ? 'text-red-400' : 'text-yellow-400'
                    }`}>
                      {status === 'success' && '✅ '}
                      {status === 'error' && '❌ '}
                      {status === 'executing' && '⏳ '}
                      {status === 'ready' && '📝 '}
                      {status === 'success' ? 'Execution completed successfully!' :
                       status === 'error' ? 'Execution failed' :
                       status === 'executing' ? 'Executing code...' : 'Ready'}
                    </div>
                    {output && (
                      <div className="text-gray-300 bg-gray-900 p-3 rounded border border-gray-700">
                        {output}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-gray-500 text-center mt-10">
                    <Terminal size={48} className="mx-auto mb-4 opacity-50" />
                    <p>Write your Jac code and click "Run Code" to execute</p>
                  </div>
                )}
              </div>
              
              {/* Clear button */}
              {output && (
                <div className="p-3 border-t border-gray-700">
                  <button 
                    onClick={clearOutput}
                    className="w-full py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm flex items-center justify-center gap-2"
                  >
                    <Trash2 size={16} />
                    Clear Output
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      
      {/* Save Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-96">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">
                {currentSnippetId ? 'Update Snippet' : 'Save Snippet'}
              </h3>
              <button 
                onClick={() => setShowSaveModal(false)}
                className="text-gray-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Title *</label>
                <input 
                  type="text"
                  value={saveTitle}
                  onChange={(e) => setSaveTitle(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                  placeholder="Enter snippet title"
                />
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-1">Description</label>
                <textarea 
                  value={saveDescription}
                  onChange={(e) => setSaveDescription(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                  rows={3}
                  placeholder="Optional description"
                />
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-1">Folder</label>
                <select 
                  value={folders.find(f => f.id === snippets.find(s => s.id === currentSnippetId)?.folder_id)?.id || ''}
                  onChange={(e) => {}}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                >
                  <option value="">No folder</option>
                  {folders.map(folder => (
                    <option key={folder.id} value={folder.id}>{folder.name}</option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button 
                onClick={() => setShowSaveModal(false)}
                className="flex-1 py-2 bg-gray-700 hover:bg-gray-600 rounded"
              >
                Cancel
              </button>
              <button 
                onClick={saveSnippet}
                disabled={isSaving}
                className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 rounded flex items-center justify-center gap-2"
              >
                {isSaving ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                ) : (
                  <>
                    <Save size={16} />
                    Save
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CodeEditor;
