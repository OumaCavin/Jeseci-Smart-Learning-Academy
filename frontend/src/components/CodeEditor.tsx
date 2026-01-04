/**
 * JAC Code Editor Component
 * 
 * A full-featured code editor for Jac language with:
 * - Monaco Editor integration
 * - Multi-language support (Jac, Python, JavaScript)
 * - Syntax highlighting for multiple languages
 * - Code execution with sandboxing
 * - Version history management
 * - Test case management for auto-grading
 * - Step-through debugging
 * - Educational error suggestions
 * - Save/Load snippets
 * - Execution history
 * - Real-time Jaclang syntax validation
 * - Automatic code formatting
 */

import React, { useState, useCallback, useRef, useEffect, useMemo } from 'react';
import Editor, { OnMount } from '@monaco-editor/react';
import type * as Monaco from 'monaco-editor';
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
  MoreVertical,
  Bug,
  Beaker,
  RotateCcw,
  Eye,
  EyeOff,
  ChevronRight,
  ChevronLeft,
  Loader,
  Lightbulb,
  BookOpen,
  Wand2,
  CheckCircle2,
  AlertTriangle,
  Zap
} from 'lucide-react';
import { apiService, JaclangValidationError, JaclangFormatResponse } from '../api';

// Monaco marker severity mapping
declare const monaco: typeof Monaco;

// Debounce utility hook
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// Supported programming languages
const SUPPORTED_LANGUAGES = [
  { id: 'jac', name: 'Jac', extension: 'jac' },
  { id: 'python', name: 'Python', extension: 'py' },
  { id: 'javascript', name: 'JavaScript', extension: 'js' }
];

// Monaco marker severity mapping
const SEVERITY_MAP = {
  'Error': monaco.MarkerSeverity.Error,
  'Warning': monaco.MarkerSeverity.Warning,
  'Info': monaco.MarkerSeverity.Info
} as const;

// Default code templates for each language
const DEFAULT_CODE_TEMPLATES: Record<string, string> = {
  jac: `walker init {
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
}`,
  python: `# Python Code Example
def main():
    greeting = "Hello, Jeseci Academy!"
    print(greeting)
    print("Welcome to Python Programming!")
    
    # Calculate sum
    a = 10
    b = 20
    result = a + b
    print(f"Sum: {a} + {b} = {result}")
    return result

if __name__ == "__main__":
    main()`,
  javascript: `// JavaScript Code Example
function main() {
    const greeting = "Hello, Jeseci Academy!";
    console.log(greeting);
    console.log("Welcome to JavaScript Programming!");
    
    // Calculate sum
    const a = 10;
    const b = 20;
    const result = a + b;
    console.log(\`Sum: \${a} + \${b} = \${result}\`);
    return result;
}

main();`
};

// Interface definitions
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
  error_suggestion?: {
    title: string;
    description: string;
    suggestion: string;
    documentation_link?: string;
    examples?: string;
  };
}

interface Folder {
  id: string;
  name: string;
  description?: string;
  parent_folder_id?: string;
  color: string;
}

interface SnippetVersion {
  id: string;
  snippet_id: string;
  version_number: number;
  code_content: string;
  title: string;
  description?: string;
  created_by: number;
  change_summary?: string;
  created_at: string;
}

interface TestCase {
  id: string;
  snippet_id: string;
  name: string;
  input_data?: string;
  expected_output: string;
  is_hidden: boolean;
  order_index: number;
  timeout_ms: number;
  created_by?: number;
  created_at: string;
}

interface TestResult {
  id: string;
  test_case_id: string;
  execution_id: string;
  passed: boolean;
  actual_output: string;
  execution_time_ms: number;
  error_message?: string;
  created_at: string;
}

const CodeEditor: React.FC = () => {
  // Core state
  const [code, setCode] = useState<string>(DEFAULT_CODE_TEMPLATES['jac']);
  const [output, setOutput] = useState<string>('');
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [status, setStatus] = useState<'ready' | 'executing' | 'success' | 'error'>('ready');
  
  // UI state
  const [activePanel, setActivePanel] = useState<'none' | 'snippets' | 'history' | 'versions' | 'tests' | 'debug'>('none');
  const [activeTab, setActiveTab] = useState<'output' | 'ai'>('output');
  
  // Data state
  const [executionHistory, setExecutionHistory] = useState<any[]>([]);
  const [snippets, setSnippets] = useState<Snippet[]>([]);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [versions, setVersions] = useState<SnippetVersion[]>([]);
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  
  // Settings state
  const [language, setLanguage] = useState<string>('jac');
  const [selectedFolder, setSelectedFolder] = useState<string>('');
  const [saveTitle, setSaveTitle] = useState<string>('');
  const [saveDescription, setSaveDescription] = useState<string>('');
  const [currentSnippetId, setCurrentSnippetId] = useState<string>('');
  
  // Modal state
  const [showSaveModal, setShowSaveModal] = useState<boolean>(false);
  const [showNewFolderModal, setShowNewFolderModal] = useState<boolean>(false);
  const [showTestModal, setShowTestModal] = useState<boolean>(false);
  const [newFolderName, setNewFolderName] = useState<string>('');
  
  // Debug state
  const [isDebugMode, setIsDebugMode] = useState<boolean>(false);
  const [debugSession, setDebugSession] = useState<any>(null);
  const [currentLine, setCurrentLine] = useState<number | null>(null);
  const [variables, setVariables] = useState<Record<string, any>>({});
  
  // Test modal state
  const [newTestName, setNewTestName] = useState<string>('');
  const [newTestInput, setNewTestInput] = useState<string>('');
  const [newTestExpected, setNewTestExpected] = useState<string>('');
  const [isHiddenTest, setIsHiddenTest] = useState<boolean>(false);
  
  // Jaclang validation state
  const [isValidating, setIsValidating] = useState<boolean>(false);
  const [validationErrors, setValidationErrors] = useState<JaclangValidationError[]>([]);
  const [isValidCode, setIsValidCode] = useState<boolean>(true);
  const [isFormatting, setIsFormatting] = useState<boolean>(false);
  const [formatResult, setFormatResult] = useState<JaclangFormatResponse | null>(null);
  const [validationServiceAvailable, setValidationServiceAvailable] = useState<boolean>(true);
  
  // Refs for managing validation requests
  const validationTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const latestCodeRef = useRef<string>(code);
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<typeof import('monaco-editor') | null>(null);

  // Load data on mount
  useEffect(() => {
    loadSnippets();
    loadFolders();
    loadExecutionHistory();
    
    // Check if validation service is available
    apiService.getJaclangServiceHealth()
      .then(health => {
        setValidationServiceAvailable(health.jac_available);
      })
      .catch(() => {
        setValidationServiceAvailable(false);
      });
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

  // Load versions for current snippet
  const loadVersions = async (snippetId: string) => {
    try {
      const response = await apiService.getSnippetVersions(snippetId);
      if (response.success) {
        setVersions(response.versions);
      }
    } catch (error) {
      console.error('Error loading versions:', error);
    }
  };

  // Load test cases for current snippet
  const loadTestCases = async (snippetId: string) => {
    try {
      const response = await apiService.getSnippetTestCases(snippetId);
      if (response.success) {
        setTestCases(response.test_cases);
      }
    } catch (error) {
      console.error('Error loading test cases:', error);
    }
  };

  // ============================================================================
  // Jaclang Validation and Formatting Functions
  // ============================================================================

  /**
   * Validate Jaclang code for syntax errors
   */
  const validateJacCode = useCallback(async (codeToValidate: string) => {
    if (language !== 'jac' || !codeToValidate.trim()) {
      setValidationErrors([]);
      setIsValidCode(true);
      return;
    }

    // Update the latest code ref
    latestCodeRef.current = codeToValidate;
    setIsValidating(true);

    try {
      const result = await apiService.validateJacCode(codeToValidate);
      
      // Check if this is still the latest code (prevent race conditions)
      if (latestCodeRef.current !== codeToValidate) {
        return;
      }
      
      setValidationErrors(result.errors || []);
      setIsValidCode(result.valid);
      
      // Update Monaco markers for errors
      if (monacoRef.current && editorRef.current) {
        const model = editorRef.current.getModel();
        if (model) {
          const markers = result.errors.map(error => ({
            severity: SEVERITY_MAP[error.severity] || monaco.MarkerSeverity.Error,
            startLineNumber: error.line,
            startColumn: error.column,
            endLineNumber: error.line,
            endColumn: error.column + 1,
            message: error.message,
            source: 'jaclang-validator'
          }));
          
          monacoRef.current.editor.setModelMarkers(model, 'jaclang', markers);
        }
      }
      
      if (!result.valid && result.errors.length > 0) {
        // Show first error in output
        const firstError = result.errors[0];
        setOutput(`❌ Syntax Error at line ${firstError.line}, column ${firstError.column}:\n${firstError.message}`);
        setStatus('error');
      } else if (result.valid) {
        // Clear error output if code is valid
        if (status === 'error' && output.includes('Syntax Error')) {
          setOutput('');
          setStatus('ready');
        }
      }
    } catch (error) {
      console.error('Validation error:', error);
      setValidationServiceAvailable(false);
      // Silently fail - don't break the editor if validation is unavailable
    } finally {
      setIsValidating(false);
    }
  }, [language, status, output]);

  /**
   * Format Jaclang code using the backend service
   */
  const formatJacCode = useCallback(async () => {
    if (language !== 'jac' || !code.trim()) {
      return;
    }

    setIsFormatting(true);
    setFormatResult(null);

    try {
      const result = await apiService.formatJacCode(code);
      setFormatResult(result);

      if (result.error) {
        // Show error in output
        setOutput(`❌ Formatting Error:\n${result.error}`);
        setStatus('error');
      } else if (result.changed) {
        // Apply formatted code
        setCode(result.formatted_code);
        
        // Re-validate the formatted code
        await validateJacCode(result.formatted_code);
        
        // Show success message
        setOutput(`✅ Code formatted successfully!\n\n${result.formatted_code}`);
        setStatus('success');
        
        // Clear success message after 3 seconds
        setTimeout(() => {
          if (status === 'success' && output.includes('formatted successfully')) {
            setOutput('');
            setStatus('ready');
          }
        }, 3000);
      } else {
        // Code was already properly formatted
        setOutput('✅ Code is already properly formatted!');
        setStatus('success');
        
        setTimeout(() => {
          if (status === 'success') {
            setOutput('');
            setStatus('ready');
          }
        }, 2000);
      }
    } catch (error) {
      console.error('Formatting error:', error);
      setOutput(`❌ Formatting failed: ${error}`);
      setStatus('error');
    } finally {
      setIsFormatting(false);
    }
  }, [language, code, status, output]);

  /**
   * Debounced validation trigger
   */
  const triggerValidation = useCallback((newCode: string) => {
    // Clear any pending validation
    if (validationTimeoutRef.current) {
      clearTimeout(validationTimeoutRef.current);
    }

    // Debounce validation - wait 800ms after typing stops
    validationTimeoutRef.current = setTimeout(() => {
      validateJacCode(newCode);
    }, 800);
  }, [validateJacCode]);

  /**
   * Clear all validation markers
   */
  const clearValidationMarkers = useCallback(() => {
    if (monacoRef.current && editorRef.current) {
      const model = editorRef.current.getModel();
      if (model) {
        monacoRef.current.editor.setModelMarkers(model, 'jaclang', []);
      }
    }
    setValidationErrors([]);
    setIsValidCode(true);
  }, []);

  // Cleanup effect - moved after clearValidationMarkers declaration
  useEffect(() => {
    return () => {
      // Clear any pending validation timeout
      if (validationTimeoutRef.current) {
        clearTimeout(validationTimeoutRef.current);
      }
      // Clear validation markers
      clearValidationMarkers();
    };
  }, [clearValidationMarkers]);

  // Handle editor mount
  const handleEditorDidMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;
    
    // Register keyboard shortcut for formatting (Shift+Alt+F or Cmd+Shift+F)
    editor.addCommand(monaco.KeyMod.Shift | monaco.KeyMod.Alt | monaco.KeyCode.KeyF, () => {
      formatJacCode();
    });
    
    // Add command for Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows/Linux) to format
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyP, () => {
      formatJacCode();
    });
    
    // Initial validation for Jac code
    if (language === 'jac' && code.trim()) {
      validateJacCode(code);
    }
  };

  // Handle language change
  const handleLanguageChange = (newLanguage: string) => {
    // Clear validation markers when changing languages
    clearValidationMarkers();
    
    setLanguage(newLanguage);
    setCode(DEFAULT_CODE_TEMPLATES[newLanguage] || '');
    
    // Validate new Jac code if switching to Jac
    if (newLanguage === 'jac' && code.trim()) {
      validateJacCode(DEFAULT_CODE_TEMPLATES['jac']);
    }
  };

  // Handle code change with validation trigger
  const handleCodeChange = (value: string | undefined) => {
    const newCode = value || '';
    setCode(newCode);
    
    // Trigger debounced validation for Jac code
    if (language === 'jac') {
      triggerValidation(newCode);
    }
  };

  // Execute code
  const executeCode = async (mode: 'run' | 'debug' | 'grade' = 'run') => {
    setIsExecuting(true);
    setOutput('');
    setStatus('executing');

    try {
      const result = await apiService.executeCode(code, language, mode);

      if (result.success) {
        let outputText = '';
        
        if (mode === 'grade') {
          outputText = `✅ Auto-grading Results\n\n`;
          if (result.test_results) {
            const passed = result.test_results.filter((t: any) => t.passed).length;
            const total = result.test_results.length;
            outputText += `Tests: ${passed}/${total} passed\n\n`;
            result.test_results.forEach((test: any, index: number) => {
              outputText += `${index + 1}. ${test.name}: ${test.passed ? '✅ PASSED' : '❌ FAILED'}\n`;
              if (!test.passed) {
                outputText += `   Expected: ${test.expected_output}\n`;
                outputText += `   Got: ${test.actual_output}\n`;
              }
            });
          }
        } else {
          outputText = `✅ Execution successful!\n\n${result.output || 'No output'}`;
        }
        
        setOutput(outputText);
        setStatus('success');
      } else {
        let errorText = `❌ Error: ${result.error || 'Unknown error'}`;
        
        // Add educational suggestion if available
        if (result.error_suggestion) {
          const { title, description, suggestion, documentation_link, examples } = result.error_suggestion;
          errorText += `\n\n💡 ${title}\n\n${description}\n\nSuggestion: ${suggestion}`;
          if (documentation_link) {
            errorText += `\n\n📚 Learn more: ${documentation_link}`;
          }
          if (examples) {
            errorText += `\n\nExample:\n${examples}`;
          }
        }
        
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

  // Run tests
  const runTests = async () => {
    await executeCode('grade');
  };

  // Start debug session
  const startDebugSession = async () => {
    try {
      const response = await apiService.createDebugSession(currentSnippetId);
      if (response.success) {
        setDebugSession(response.session);
        setIsDebugMode(true);
        setCurrentLine(1);
        setVariables({});
        setActivePanel('debug');
      }
    } catch (error) {
      alert('Failed to start debug session: ' + error);
    }
  };

  // Step through debug
  const debugStep = async (action: 'step' | 'continue' | 'terminate') => {
    if (!debugSession) return;

    try {
      const response = await apiService.debugStep(debugSession.id, action);
      if (response.success) {
        if (action === 'terminate') {
          setIsDebugMode(false);
          setDebugSession(null);
          setCurrentLine(null);
        } else {
          setCurrentLine(response.current_line);
          setVariables(response.variables || {});
          
          if (response.status === 'completed') {
            setOutput(`Debug completed!\n\nOutput:\n${response.output || 'No output'}`);
            setStatus(response.success ? 'success' : 'error');
            setIsDebugMode(false);
          }
        }
      }
    } catch (error) {
      alert('Debug step failed: ' + error);
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
        language: language,
        description: saveDescription,
        snippet_id: currentSnippetId || undefined
      });

      if (response.success) {
        setShowSaveModal(false);
        setSaveTitle('');
        setSaveDescription('');
        setCurrentSnippetId(response.snippet.id);
        
        // Create initial version
        if (!currentSnippetId) {
          await apiService.createVersion(response.snippet.id, code, saveTitle, 1, 'Initial version');
        }
        
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

  // Create test case
  const createTestCase = async () => {
    if (!newTestName.trim() || !newTestExpected.trim()) {
      alert('Please fill in test name and expected output');
      return;
    }

    try {
      const response = await apiService.createTestCase({
        snippet_id: currentSnippetId,
        name: newTestName,
        input_data: newTestInput,
        expected_output: newTestExpected,
        is_hidden: isHiddenTest
      });

      if (response.success) {
        setShowTestModal(false);
        setNewTestName('');
        setNewTestInput('');
        setNewTestExpected('');
        setIsHiddenTest(false);
        loadTestCases(currentSnippetId);
      } else {
        alert('Failed to create test case: ' + response.error);
      }
    } catch (error) {
      alert('Error creating test case: ' + error);
    }
  };

  // Load snippet
  const loadSnippet = (snippet: Snippet) => {
    setCode(snippet.code_content);
    setCurrentSnippetId(snippet.id);
    setSaveTitle(snippet.title);
    setSaveDescription(snippet.description || '');
    setLanguage(snippet.language || 'jac');
    
    // Load related data
    loadVersions(snippet.id);
    loadTestCases(snippet.id);
    
    setActivePanel('none');
  };

  // Load version
  const loadVersion = (version: SnippetVersion) => {
    setCode(version.code_content);
    setOutput(`Loaded version ${version.version_number}: ${version.change_summary || 'No description'}`);
    setStatus('ready');
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

  // Format code using Jaclang backend service
  const formatCode = () => {
    if (language === 'jac') {
      // Use backend Jaclang formatting
      formatJacCode();
    } else if (editorRef.current) {
      // Fall back to Monaco's built-in formatting for other languages
      editorRef.current.getAction('editor.action.formatDocument').run();
    }
  };

  // Clear output
  const clearOutput = () => {
    setOutput('');
    setStatus('ready');
  };

  // Get language-specific syntax highlighting
  const getMonacoLanguage = () => {
    switch (language) {
      case 'python': return 'python';
      case 'javascript': return 'javascript';
      default: return 'python'; // Monaco doesn't have Jac, use Python highlighting
    }
  };

  return (
    <div className="flex h-full bg-gray-900 text-white">
      {/* Left Sidebar - Snippets */}
      <div className={`${activePanel === 'snippets' ? 'w-64' : 'w-0'} transition-all duration-300 overflow-hidden border-r border-gray-700 flex flex-col`}>
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <h3 className="font-semibold text-lg flex items-center gap-2">
            <FileCode size={18} />
            Snippets
          </h3>
          <button 
            onClick={() => setActivePanel('none')}
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
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs px-2 py-0.5 rounded bg-gray-700 text-gray-300">
                    {snippet.language}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(snippet.updated_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
        </div>
        
        {/* New snippet button */}
        <div className="p-3 border-t border-gray-700">
          <button 
            onClick={() => {
              setCode(DEFAULT_CODE_TEMPLATES[language]);
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

      {/* Version History Sidebar */}
      <div className={`${activePanel === 'versions' ? 'w-64' : 'w-0'} transition-all duration-300 overflow-hidden border-r border-gray-700 flex flex-col bg-gray-850`}>
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <h3 className="font-semibold text-lg flex items-center gap-2">
            <History size={18} />
            Version History
          </h3>
          <button 
            onClick={() => setActivePanel('none')}
            className="text-gray-400 hover:text-white"
          >
            <X size={18} />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-3">
          {versions.length === 0 ? (
            <div className="text-gray-500 text-center py-8">
              <History size={32} className="mx-auto mb-2 opacity-50" />
              <p>No versions yet</p>
              <p className="text-sm mt-2">Save your snippet to create the first version</p>
            </div>
          ) : (
            versions.map((version) => (
              <div 
                key={version.id}
                className="p-3 mb-2 bg-gray-800 rounded cursor-pointer hover:bg-gray-700"
                onClick={() => loadVersion(version)}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">v{version.version_number}</span>
                  <span className="text-xs text-gray-500">
                    {new Date(version.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mt-1 truncate">
                  {version.change_summary || 'No description'}
                </p>
                <button 
                  className="mt-2 text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
                  onClick={(e) => {
                    e.stopPropagation();
                    loadVersion(version);
                  }}
                >
                  <RotateCcw size={12} />
                  Restore this version
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Test Cases Sidebar */}
      <div className={`${activePanel === 'tests' ? 'w-72' : 'w-0'} transition-all duration-300 overflow-hidden border-r border-gray-700 flex flex-col bg-gray-850`}>
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <h3 className="font-semibold text-lg flex items-center gap-2">
            <Beaker size={18} />
            Test Cases
          </h3>
          <button 
            onClick={() => setActivePanel('none')}
            className="text-gray-400 hover:text-white"
          >
            <X size={18} />
          </button>
        </div>
        
        {/* Run tests button */}
        <div className="p-3 border-b border-gray-700">
          <button 
            onClick={runTests}
            disabled={isExecuting || !currentSnippetId}
            className={`w-full py-2 rounded flex items-center justify-center gap-2 ${
              currentSnippetId ? 'bg-purple-600 hover:bg-purple-700' : 'bg-gray-700 cursor-not-allowed'
            }`}
          >
            <Beaker size={16} />
            Run All Tests
          </button>
        </div>
        
        {/* Test cases list */}
        <div className="flex-1 overflow-y-auto p-3">
          {testCases.length === 0 ? (
            <div className="text-gray-500 text-center py-8">
              <Beaker size={32} className="mx-auto mb-2 opacity-50" />
              <p>No test cases yet</p>
              <p className="text-sm mt-2">Add test cases to enable auto-grading</p>
            </div>
          ) : (
            testCases.map((test) => (
              <div 
                key={test.id}
                className="p-3 mb-2 bg-gray-800 rounded"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{test.name}</span>
                  {test.is_hidden && (
                    <span className="text-xs px-2 py-0.5 rounded bg-yellow-900 text-yellow-300">
                      Hidden
                    </span>
                  )}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Input: {test.input_data || 'None'}
                </div>
                <div className="text-xs text-gray-500">
                  Expected: {test.expected_output}
                </div>
              </div>
            ))
          )}
        </div>
        
        {/* Add test button */}
        <div className="p-3 border-t border-gray-700">
          <button 
            onClick={() => currentSnippetId ? setShowTestModal(true) : alert('Save your snippet first to add test cases')}
            className="w-full py-2 bg-gray-700 hover:bg-gray-600 rounded flex items-center justify-center gap-2"
          >
            <Beaker size={16} />
            Add Test Case
          </button>
        </div>
      </div>

      {/* Debug Sidebar */}
      <div className={`${activePanel === 'debug' ? 'w-72' : 'w-0'} transition-all duration-300 overflow-hidden border-r border-gray-700 flex flex-col bg-gray-850`}>
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <h3 className="font-semibold text-lg flex items-center gap-2">
            <Bug size={18} />
            Debugger
          </h3>
          <button 
            onClick={() => setActivePanel('none')}
            className="text-gray-400 hover:text-white"
          >
            <X size={18} />
          </button>
        </div>
        
        {/* Debug controls */}
        <div className="p-3 border-b border-gray-700 flex gap-2">
          <button 
            onClick={() => debugStep('step')}
            disabled={!isDebugMode}
            className="flex-1 py-2 bg-yellow-600 hover:bg-yellow-700 rounded text-sm flex items-center justify-center gap-1"
          >
            <ChevronRight size={14} />
            Step
          </button>
          <button 
            onClick={() => debugStep('continue')}
            disabled={!isDebugMode}
            className="flex-1 py-2 bg-green-600 hover:bg-green-700 rounded text-sm flex items-center justify-center gap-1"
          >
            <Play size={14} />
            Continue
          </button>
          <button 
            onClick={() => debugStep('terminate')}
            disabled={!isDebugMode}
            className="flex-1 py-2 bg-red-600 hover:bg-red-700 rounded text-sm flex items-center justify-center gap-1"
          >
            <X size={14} />
            Stop
          </button>
        </div>
        
        {/* Current line indicator */}
        <div className="p-3 border-b border-gray-700">
          <div className="text-sm text-gray-400">Current Line</div>
          <div className="text-xl font-mono">{currentLine || '-'}</div>
        </div>
        
        {/* Variables */}
        <div className="flex-1 overflow-y-auto p-3">
          <div className="text-sm text-gray-400 mb-2">Variables</div>
          {Object.keys(variables).length === 0 ? (
            <div className="text-gray-500 text-sm">No variables in scope</div>
          ) : (
            <pre className="text-xs bg-gray-800 p-2 rounded overflow-x-auto">
              {JSON.stringify(variables, null, 2)}
            </pre>
          )}
        </div>
        
        {!isDebugMode && (
          <div className="p-3 border-t border-gray-700">
            <button 
              onClick={startDebugSession}
              disabled={!currentSnippetId}
              className={`w-full py-2 rounded flex items-center justify-center gap-2 ${
                currentSnippetId ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-700 cursor-not-allowed'
              }`}
            >
              <Bug size={16} />
              Start Debugging
            </button>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <div className="bg-gray-800 border-b border-gray-700 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* Toggle snippets sidebar */}
            <button 
              onClick={() => setActivePanel(activePanel === 'snippets' ? 'none' : 'snippets')}
              className={`p-2 rounded hover:bg-gray-700 ${activePanel === 'snippets' ? 'text-blue-400' : 'text-gray-400'}`}
              title="Snippets"
            >
              <FolderOpen size={18} />
            </button>
            
            {/* Toggle versions */}
            <button 
              onClick={() => setActivePanel(activePanel === 'versions' ? 'none' : 'versions')}
              className={`p-2 rounded hover:bg-gray-700 ${activePanel === 'versions' ? 'text-blue-400' : 'text-gray-400'}`}
              title="Version History"
            >
              <History size={18} />
            </button>
            
            {/* Toggle tests */}
            <button 
              onClick={() => setActivePanel(activePanel === 'tests' ? 'none' : 'tests')}
              className={`p-2 rounded hover:bg-gray-700 ${activePanel === 'tests' ? 'text-blue-400' : 'text-gray-400'}`}
              title="Test Cases"
            >
              <Beaker size={18} />
            </button>
            
            {/* Toggle debug */}
            <button 
              onClick={() => setActivePanel(activePanel === 'debug' ? 'none' : 'debug')}
              className={`p-2 rounded hover:bg-gray-700 ${activePanel === 'debug' ? 'text-blue-400' : 'text-gray-400'}`}
              title="Debugger"
            >
              <Bug size={18} />
            </button>
            
            {/* Format code */}
            <button 
              onClick={formatCode}
              disabled={isFormatting || language !== 'jac'}
              className={`p-2 rounded hover:bg-gray-700 ${
                isFormatting ? 'text-yellow-400 animate-pulse' : 'text-gray-400 hover:text-white'
              }`}
              title={isFormatting ? 'Formatting...' : 'Format Code (Shift+Alt+F)'}
            >
              {isFormatting ? <Loader size={18} className="animate-spin" /> : <Wand2 size={18} />}
            </button>
            
            {/* Jaclang validation status */}
            {language === 'jac' && (
              <div className="flex items-center gap-2">
                {isValidating ? (
                  <div className="flex items-center gap-1.5 text-yellow-400 text-sm">
                    <Loader size={14} className="animate-spin" />
                    <span>Validating...</span>
                  </div>
                ) : !validationServiceAvailable ? (
                  <div className="flex items-center gap-1.5 text-gray-500 text-sm" title="Validation service unavailable">
                    <AlertTriangle size={14} />
                    <span>No validation</span>
                  </div>
                ) : isValidCode ? (
                  <div className="flex items-center gap-1.5 text-green-400 text-sm" title="Code is valid">
                    <CheckCircle2 size={14} />
                    <span>Valid</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-1.5 text-red-400 text-sm" title={`${validationErrors.length} error(s) found`}>
                    <AlertCircle size={14} />
                    <span>{validationErrors.length} error(s)</span>
                  </div>
                )}
              </div>
            )}
            
            {/* Divider */}
            <div className="h-6 w-px bg-gray-600"></div>
            
            {/* Language selector */}
            <div className="relative">
              <select 
                value={language}
                onChange={(e) => handleLanguageChange(e.target.value)}
                className="appearance-none bg-gray-700 border border-gray-600 rounded px-3 py-1.5 pr-8 text-sm cursor-pointer hover:bg-gray-600"
              >
                {SUPPORTED_LANGUAGES.map(lang => (
                  <option key={lang.id} value={lang.id}>{lang.name}</option>
                ))}
              </select>
              <ChevronDown size={14} className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
            </div>
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
              onClick={() => executeCode('run')}
              disabled={isExecuting}
              className={`flex items-center gap-2 px-6 py-2 rounded font-medium ${
                isExecuting 
                  ? 'bg-yellow-600 cursor-not-allowed' 
                  : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              {isExecuting ? (
                <>
                  <Loader size={16} className="animate-spin" />
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
              defaultLanguage={getMonacoLanguage()}
              language={getMonacoLanguage()}
              value={code}
              onChange={handleCodeChange}
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
            
            {/* Status Bar */}
            <div className="bg-gray-900 border-t border-gray-700 px-4 py-1.5 flex items-center justify-between text-xs">
              <div className="flex items-center gap-4">
                {/* Line/Column info - from editor */}
                <span className="text-gray-500">
                  {editorRef.current && `Ln ${editorRef.current.getPosition()?.lineNumber || 1}, Col ${editorRef.current.getPosition()?.column || 1}`}
                </span>
                
                {/* Language info */}
                <span className="text-gray-500">
                  {SUPPORTED_LANGUAGES.find(l => l.id === language)?.name}
                </span>
                
                {/* Validation status for Jaclang */}
                {language === 'jac' && (
                  <>
                    <span className="text-gray-600">|</span>
                    {isValidating ? (
                      <span className="text-yellow-400 flex items-center gap-1">
                        <Loader size={12} className="animate-spin" />
                        Validating...
                      </span>
                    ) : !validationServiceAvailable ? (
                      <span className="text-gray-500 flex items-center gap-1" title="Jaclang validation service unavailable">
                        <AlertTriangle size={12} />
                        Validation unavailable
                      </span>
                    ) : isValidCode ? (
                      <span className="text-green-400 flex items-center gap-1">
                        <CheckCircle2 size={12} />
                        No errors
                      </span>
                    ) : (
                      <span className="text-red-400 flex items-center gap-1">
                        <AlertCircle size={12} />
                        {validationErrors.length} syntax error{validationErrors.length !== 1 ? 's' : ''}
                      </span>
                    )}
                  </>
                )}
              </div>
              
              <div className="flex items-center gap-4">
                {/* Formatting info */}
                {language === 'jac' && formatResult?.changed && (
                  <span className="text-blue-400 flex items-center gap-1">
                    <Zap size={12} />
                    Code formatted
                  </span>
                )}
                
                {/* Keyboard shortcut hint */}
                <span className="text-gray-600">
                  {language === 'jac' ? 'Shift+Alt+F to format' : 'Format available'}
                </span>
              </div>
            </div>
          </div>
          
          {/* Output Panel */}
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
                <Lightbulb size={16} className="inline mr-2" />
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
                    <div className="text-gray-300 bg-gray-900 p-3 rounded border border-gray-700 whitespace-pre-wrap">
                      {output}
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-gray-500 text-center mt-10">
                  <Terminal size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Write your code and click "Run Code" to execute</p>
                  <p className="text-sm mt-2 text-gray-400">
                    Language: {SUPPORTED_LANGUAGES.find(l => l.id === language)?.name}
                  </p>
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
                <label className="block text-sm text-gray-400 mb-1">Language</label>
                <select 
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                >
                  {SUPPORTED_LANGUAGES.map(lang => (
                    <option key={lang.id} value={lang.id}>{lang.name}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-1">Folder</label>
                <select 
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                  defaultValue=""
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
                  <Loader size={16} className="animate-spin" />
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
      
      {/* New Folder Modal */}
      {showNewFolderModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-96">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Create Folder</h3>
              <button 
                onClick={() => setShowNewFolderModal(false)}
                className="text-gray-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Folder Name *</label>
                <input 
                  type="text"
                  value={newFolderName}
                  onChange={(e) => setNewFolderName(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                  placeholder="Enter folder name"
                />
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button 
                onClick={() => setShowNewFolderModal(false)}
                className="flex-1 py-2 bg-gray-700 hover:bg-gray-600 rounded"
              >
                Cancel
              </button>
              <button 
                onClick={createFolder}
                className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 rounded flex items-center justify-center gap-2"
              >
                <FolderPlus size={16} />
                Create
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Test Case Modal */}
      {showTestModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-96">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Add Test Case</h3>
              <button 
                onClick={() => setShowTestModal(false)}
                className="text-gray-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Test Name *</label>
                <input 
                  type="text"
                  value={newTestName}
                  onChange={(e) => setNewTestName(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                  placeholder="e.g., Test addition"
                />
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-1">Input</label>
                <textarea 
                  value={newTestInput}
                  onChange={(e) => setNewTestInput(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                  rows={2}
                  placeholder="Input data (optional)"
                />
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-1">Expected Output *</label>
                <textarea 
                  value={newTestExpected}
                  onChange={(e) => setNewTestExpected(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2"
                  rows={2}
                  placeholder="Expected output"
                />
              </div>
              
              <div className="flex items-center gap-2">
                <input 
                  type="checkbox"
                  id="isHidden"
                  checked={isHiddenTest}
                  onChange={(e) => setIsHiddenTest(e.target.checked)}
                  className="rounded bg-gray-700 border-gray-600"
                />
                <label htmlFor="isHidden" className="text-sm text-gray-400">
                  Hidden test (only shown if failed)
                </label>
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button 
                onClick={() => setShowTestModal(false)}
                className="flex-1 py-2 bg-gray-700 hover:bg-gray-600 rounded"
              >
                Cancel
              </button>
              <button 
                onClick={createTestCase}
                className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 rounded flex items-center justify-center gap-2"
              >
                <Beaker size={16} />
                Create Test
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CodeEditor;
