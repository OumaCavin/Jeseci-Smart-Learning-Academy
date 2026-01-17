#!/usr/bin/env python3
"""
Enhanced JAC Code Execution Engine Service

This module provides secure multi-language code execution capabilities.
Supports Python, JavaScript, and Jac language with enhanced sandboxing,
resource limits, debugging, auto-grading, and educational error suggestions.

Features:
- Multi-language execution (Python, JavaScript, Jac)
- Enhanced sandbox with memory and output limits
- Step-through debugging (trace-based)
- Auto-grading with test cases
- Educational error suggestions from knowledge base
- Version history for code snippets
"""

import os
import sys
import time
import signal
import subprocess
import threading
import tempfile
import shutil
import re
import json
import resource
from datetime import datetime
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass, field
from contextlib import contextmanager
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger_config import logger as app_logger


class Language(Enum):
    """Supported programming languages"""
    JAC = "jac"
    PYTHON = "python"
    JAVASCRIPT = "javascript"


@dataclass
class ExecutionResult:
    """Result of code execution"""
    success: bool
    stdout: str
    stderr: str
    execution_time_ms: int
    status: str  # 'success', 'error', 'timeout', 'memory_exceeded'
    language: str = "jac"
    output_file: Optional[str] = None
    ir_output: Optional[str] = None
    error_type: Optional[str] = None
    line_number: Optional[int] = None
    memory_used_bytes: Optional[int] = None
    hint: Optional[str] = None
    suggestion: Optional[str] = None
    resource_link: Optional[str] = None
    execution_trace: Optional[List[Dict]] = None
    test_results: Optional[List[Dict]] = None
    score: Optional[int] = None


@dataclass
class DebugStep:
    """Debug step information"""
    line_number: int
    line_content: str
    variables: Dict[str, Any]
    stdout: str
    step_number: int


@dataclass
class TestCaseResult:
    """Result of a single test case"""
    test_name: str
    passed: bool
    input_data: str
    expected_output: str
    actual_output: str
    points_earned: int
    points_possible: int
    execution_time_ms: int
    error_message: Optional[str] = None


class SandboxManager:
    """
    Manages sandboxed execution with resource limits.
    Implements timeouts, memory limits, and output size limits.
    """
    
    # Default resource limits
    DEFAULT_TIMEOUT = 10  # seconds
    MAX_OUTPUT_SIZE = 1024 * 100  # 100KB (reduced from 1MB)
    MAX_MEMORY_MB = 128
    MAX_CODE_SIZE = 100 * 1024  # 100KB
    
    def __init__(self):
        self.temp_dir = None
        self.process = None
        self.start_time = None
        
    @contextmanager
    def temporary_directory(self):
        """Create a temporary directory for code execution"""
        temp_dir = tempfile.mkdtemp(prefix="code_exec_")
        try:
            yield temp_dir
        finally:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                app_logger.warning(f"Failed to cleanup temp directory: {e}")
    
    def write_code_file(self, temp_dir: str, code: str, language: str) -> str:
        """Write code to a temporary file based on language"""
        extension = self._get_extension(language)
        file_path = os.path.join(temp_dir, f"main{extension}")
        with open(file_path, 'w') as f:
            f.write(code)
        return file_path
    
    def _get_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            'python': '.py',
            'javascript': '.js',
            'jac': '.jac'
        }
        return extensions.get(language.lower(), '.txt')
    
    def set_execution_limits(self, timeout: int = None, memory_mb: int = None):
        """Set resource limits for the current process"""
        # Set memory limit
        if memory_mb:
            try:
                soft, hard = resource.getrlimit(resource.RLIMIT_AS)
                resource.setrlimit(resource.RLIMIT_AS, (memory_mb * 1024 * 1024, hard))
            except Exception as e:
                app_logger.warning(f"Could not set memory limit: {e}")
        
        # Set up timeout handler
        def timeout_handler(signum, frame):
            if self.process and self.process.poll() is None:
                self.process.kill()
            raise TimeoutException(f"Execution timed out after {timeout or self.DEFAULT_TIMEOUT} seconds")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout or self.DEFAULT_TIMEOUT)
    
    def clear_limits(self):
        """Clear execution limits"""
        signal.alarm(0)
    
    def truncate_output(self, output: str, max_size: int = None) -> str:
        """Truncate output if it exceeds size limit"""
        max_size = max_size or self.MAX_OUTPUT_SIZE
        if len(output) > max_size:
            return output[:max_size] + f"\n\n[Output truncated. Original size: {len(output)} bytes]"
        return output


class TimeoutException(Exception):
    """Raised when code execution times out"""
    pass


class MemoryLimitException(Exception):
    """Raised when code exceeds memory limits"""
    pass


class CodeExecutionError(Exception):
    """Custom exception for code execution errors"""
    def __init__(self, message: str, error_type: str = "EXECUTION_ERROR", line_number: Optional[int] = None):
        self.message = message
        self.error_type = error_type
        self.line_number = line_number
        super().__init__(self.message)


class MultiLanguageExecutor:
    """
    Executes code in multiple languages with sandboxed execution.
    """
    
    # Command configurations for each language
    LANGUAGE_COMMANDS = {
        'python': {
            'run': ['python3', '-u'],
            'compile': None,
            'entry_flag': None
        },
        'javascript': {
            'run': ['node', '--check'],  # Syntax check
            'compile': None,
            'entry_flag': None
        },
        'jac': {
            'run': ['jac', 'run'],
            'compile': ['jac', 'compile'],
            'entry_flag': None  # Jac uses walker name directly after file
        }
    }
    
    def __init__(self):
        self.sandbox = SandboxManager()
        self.temp_dir = None
        self.process = None
    
    def execute(self, code: str, language: str, entry_point: str = "init",
                timeout: int = None, memory_mb: int = None, 
                input_data: str = None, debug_mode: bool = False) -> ExecutionResult:
        """
        Execute code in the specified language.
        
        Args:
            code: Code to execute
            language: Programming language
            entry_point: Entry point function/walker
            timeout: Execution timeout in seconds
            memory_mb: Memory limit in MB
            input_data: Standard input data
            debug_mode: Enable trace-based debugging
            
        Returns:
            ExecutionResult with execution details
        """
        start_time = time.time()
        
        # Validate input
        if not code or not code.strip():
            return ExecutionResult(
                success=False, stdout="", stderr="No code provided",
                execution_time_ms=0, status="error", language=language,
                error_type="VALIDATION_ERROR"
            )
        
        # Check code size
        if len(code) > SandboxManager.MAX_CODE_SIZE:
            return ExecutionResult(
                success=False, stdout="", 
                stderr=f"Code exceeds maximum size limit ({SandboxManager.MAX_CODE_SIZE} bytes)",
                execution_time_ms=0, status="error", language=language,
                error_type="VALIDATION_ERROR"
            )
        
        with self.sandbox.temporary_directory() as temp_dir:
            try:
                # Write code to file
                code_file = self.sandbox.write_code_file(temp_dir, code, language)
                
                # Build execution command
                cmd = self._build_command(language, code_file, entry_point)
                
                app_logger.info(f"Executing {language} code with command: {' '.join(cmd)}")
                
                # Set up limits
                self.sandbox.set_execution_limits(timeout, memory_mb)
                
                try:
                    # Prepare environment
                    env = {
                        **os.environ,
                        'PYTHONUNBUFFERED': '1',
                        'NODE_OPTIONS': '--no-warnings',  # Suppress Node warnings
                    }
                    
                    # Execute
                    self.process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdin=subprocess.PIPE if input_data else None,
                        text=True,
                        cwd=temp_dir,
                        env=env
                    )
                    
                    # Send input if provided
                    stdout, stderr = "", ""
                    if input_data:
                        stdout, stderr = self.process.communicate(input=input_data, timeout=timeout or SandboxManager.DEFAULT_TIMEOUT)
                    else:
                        stdout, stderr = self.process.communicate(timeout=timeout or SandboxManager.DEFAULT_TIMEOUT)
                    
                    # Cancel alarm
                    signal.alarm(0)
                    
                    execution_time = int((time.time() - start_time) * 1000)
                    
                    # Truncate output
                    stdout = self.sandbox.truncate_output(stdout)
                    stderr = self.sandbox.truncate_output(stderr)
                    
                    # Process result
                    if self.process.returncode == 0:
                        # Success
                        return ExecutionResult(
                            success=True,
                            stdout=stdout.strip(),
                            stderr="",
                            execution_time_ms=execution_time,
                            status="success",
                            language=language
                        )
                    else:
                        # Error occurred
                        return self._process_error(
                            stderr, stdout, language, execution_time, debug_mode
                        )
                        
                except TimeoutException:
                    signal.alarm(0)
                    if self.process and self.process.poll() is None:
                        self.process.kill()
                    return ExecutionResult(
                        success=False, stdout="", 
                        stderr=f"Execution timed out after {timeout or SandboxManager.DEFAULT_TIMEOUT} seconds",
                        execution_time_ms=int((time.time() - start_time) * 1000),
                        status="timeout", language=language,
                        error_type="TIMEOUT"
                    )
                    
            except Exception as e:
                execution_time = int((time.time() - start_time) * 1000)
                app_logger.error(f"Execution error: {e}")
                return ExecutionResult(
                    success=False, stdout="", stderr=str(e),
                    execution_time_ms=execution_time, status="error",
                    language=language, error_type="EXECUTION_ERROR"
                )
    
    def _build_command(self, language: str, code_file: str, entry_point: str) -> List[str]:
        """Build the execution command for the specified language"""
        lang_config = self.LANGUAGE_COMMANDS.get(language.lower(), self.LANGUAGE_COMMANDS['python'])
        
        cmd = lang_config['run'].copy()
        
        # For Python and JS, run directly; for Jac, use entry point
        if language.lower() == 'python':
            cmd.append(code_file)
        elif language.lower() == 'javascript':
            # For JS, just run directly
            cmd = ['node', code_file]
        elif language.lower() == 'jac':
            cmd.append(code_file)
            # Jac uses walker name directly after file, not --entry flag
            if entry_point and entry_point != 'init':
                cmd.append(entry_point)
        
        return cmd
    
    def _process_error(self, stderr: str, stdout: str, language: str, 
                       execution_time: int, debug_mode: bool) -> ExecutionResult:
        """Process error output and extract error details"""
        error_msg = stderr.strip().split('\n')[0] if stderr.strip() else "Unknown error"
        line_number = self._extract_line_number(stderr)
        error_type = self._classify_error(stderr, language)
        
        return ExecutionResult(
            success=False,
            stdout=stdout.strip(),
            stderr=error_msg,
            execution_time_ms=execution_time,
            status="error",
            language=language,
            error_type=error_type,
            line_number=line_number
        )
    
    def _extract_line_number(self, error_msg: str) -> Optional[int]:
        """Extract line number from error message"""
        patterns = [
            r'line (\d+)',
            r'line (\d+)',
            r'Line (\d+)',
            r'at position (\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_msg)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    pass
        return None
    
    def _classify_error(self, error_msg: str, language: str) -> str:
        """Classify the type of error"""
        error_lower = error_msg.lower()
        
        if 'syntax' in error_lower:
            return "SYNTAX_ERROR"
        elif 'indentation' in error_lower:
            return "INDENTATION_ERROR"
        elif 'name' in error_lower and 'error' in error_lower:
            return "NAME_ERROR"
        elif 'type' in error_lower and 'error' in error_lower:
            return "TYPE_ERROR"
        elif 'value' in error_lower and 'error' in error_lower:
            return "VALUE_ERROR"
        elif 'index' in error_lower and 'error' in error_lower:
            return "INDEX_ERROR"
        elif 'key' in error_lower and 'error' in error_lower:
            return "KEY_ERROR"
        elif 'attribute' in error_lower and 'error' in error_lower:
            return "ATTRIBUTE_ERROR"
        elif 'zero division' in error_lower or 'division by zero' in error_lower:
            return "ZERO_DIVISION_ERROR"
        elif 'timeout' in error_lower:
            return "TIMEOUT"
        elif 'memory' in error_lower:
            return "MEMORY_ERROR"
        else:
            return "RUNTIME_ERROR"


class ErrorAnalyzer:
    """
    Analyzes errors and provides educational suggestions from knowledge base.
    """
    
    def __init__(self):
        from code_execution_store import CodeExecutionStore
        self.store = CodeExecutionStore()
    
    def analyze_error(self, error_msg: str, language: str) -> Dict[str, Optional[str]]:
        """
        Analyze error and return educational suggestions.
        
        Returns:
            Dict with friendly_message, suggestion, resource_link
        """
        result = {
            'friendly_message': None,
            'suggestion': None,
            'resource_link': None,
            'example_fix': None
        }
        
        try:
            # Query knowledge base for matching error patterns
            patterns = self.store.get_error_suggestions(language, error_msg)
            
            if patterns:
                # Use the highest priority match
                best_match = patterns[0]
                # Safely get values with default fallbacks
                result['friendly_message'] = best_match.get('friendly_message') if best_match else None
                result['suggestion'] = best_match.get('suggestion') if best_match else None
                result['resource_link'] = best_match.get('documentation_link') if best_match else None
                result['example_fix'] = best_match.get('example_fix') if best_match else None
            
            # Fallback messages for common errors
            if not result['friendly_message']:
                result['friendly_message'] = self._get_fallback_message(error_msg)
                
        except Exception as e:
            # Log the error but don't crash - use fallback message
            app_logger.warning(f"Error analyzing error message (using fallback): {e}")
            result['friendly_message'] = self._get_fallback_message(error_msg)
        
        return result
    
    def _get_fallback_message(self, error_msg: str) -> str:
        """Get fallback message for unrecognized errors"""
        error_lower = error_msg.lower()
        
        if 'syntax' in error_lower:
            return "There's a syntax error in your code. Check for missing symbols, brackets, or keywords."
        elif 'indentation' in error_lower:
            return "Your code has incorrect indentation. Make sure all code blocks are properly aligned."
        elif 'name' in error_lower:
            return "You're using a variable that hasn't been defined. Check for typos."
        elif 'type' in error_lower:
            return "You're performing an operation on incompatible types. Check your variable types."
        else:
            return "An error occurred during execution. Review your code for issues."


class AutoGrader:
    """
    Auto-grades code submissions using test cases.
    """
    
    def __init__(self):
        from code_execution_store import CodeExecutionStore
        self.store = CodeExecutionStore()
        self.executor = MultiLanguageExecutor()
    
    def grade_submission(self, code: str, language: str, snippet_id: str = None,
                        test_cases: List[Dict] = None) -> Tuple[ExecutionResult, List[TestCaseResult]]:
        """
        Grade a code submission against test cases.
        
        Args:
            code: Code to grade
            language: Programming language
            snippet_id: ID of the snippet being graded
            test_cases: List of test cases or None to fetch from DB
            
        Returns:
            Tuple of (overall_result, test_results)
        """
        # Get test cases from DB if not provided
        if not test_cases and snippet_id:
            test_cases = self.store.get_test_cases(snippet_id)
        
        if not test_cases:
            # No test cases, just execute
            result = self.executor.execute(code, language)
            return result, []
        
        # Run each test case
        test_results = []
        total_points = 0
        earned_points = 0
        
        for i, test in enumerate(test_cases):
            test_name = test.get('test_name', f"Test {i+1}")
            input_data = test.get('input', '')
            expected_output = test.get('expected_output', '').strip()
            points = test.get('points', 10)
            timeout = test.get('timeout_seconds', 5)
            
            total_points += points
            
            # Execute with input
            result = self.executor.execute(
                code, language, 
                input_data=input_data, 
                timeout=timeout
            )
            
            # Compare output
            actual_output = result.stdout.strip() if result.stdout else ''
            passed = actual_output == expected_output
            
            if passed:
                earned_points += points
                test_result = TestCaseResult(
                    test_name=test_name,
                    passed=True,
                    input_data=input_data,
                    expected_output=expected_output,
                    actual_output=actual_output,
                    points_earned=points,
                    points_possible=points,
                    execution_time_ms=result.execution_time_ms
                )
            else:
                test_result = TestCaseResult(
                    test_name=test_name,
                    passed=False,
                    input_data=input_data,
                    expected_output=expected_output,
                    actual_output=actual_output,
                    points_earned=0,
                    points_possible=points,
                    execution_time_ms=result.execution_time_ms,
                    error_message=f"Expected: {expected_output}\nGot: {actual_output}"
                )
            
            test_results.append(test_result)
        
        # Calculate score
        score = int((earned_points / total_points * 100)) if total_points > 0 else 0
        
        # Build overall result
        overall_result = ExecutionResult(
            success=score >= 70,
            stdout=f"Score: {score}% ({earned_points}/{total_points} points)",
            stderr="",
            execution_time_ms=sum(r.execution_time_ms for r in test_results),
            status="success" if score >= 70 else "error",
            language=language,
            test_results=[
                {
                    'test_name': r.test_name,
                    'passed': r.passed,
                    'expected': r.expected_output,
                    'actual': r.actual_output,
                    'points_earned': r.points_earned,
                    'error': r.error_message
                }
                for r in test_results
            ],
            score=score
        )
        
        return overall_result, test_results


class TraceDebugger:
    """
    Implements trace-based debugging for Python.
    Injects trace code to capture execution state at each line.
    """
    
    def __init__(self):
        self.executor = MultiLanguageExecutor()
    
    def generate_debug_code(self, code: str) -> str:
        """Generate instrumented code with trace statements"""
        lines = code.split('\n')
        instrumented_lines = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                instrumented_lines.append(line)
                continue
            
            # Add trace statement before executable lines
            trace_line = f'    _trace.append({{"line": {i}, "code": {repr(line.strip())}, "vars": list(locals().keys())}})'
            
            # Handle indentation
            indent = len(line) - len(line.lstrip())
            trace_indent = ' ' * indent
            
            instrumented_lines.append(trace_indent + trace_line)
            instrumented_lines.append(line)
        
        # Add trace collection at the end
        instrumented_lines.append('\n# Trace output')
        instrumented_lines.append('import json')
        instrumented_lines.append('print(json.dumps(_trace))')
        
        return '\n'.join(instrumented_lines)
    
    def execute_with_trace(self, code: str, language: str) -> ExecutionResult:
        """Execute code and capture execution trace"""
        if language != 'python':
            # Only support trace debugging for Python currently
            return self.executor.execute(code, language)
        
        # Generate instrumented code
        debug_code = self.generate_debug_code(code)
        
        # Wrap with trace collection
        wrapped_code = f"""
import json
_trace = []

{debug_code}
"""
        
        result = self.executor.execute(wrapped_code, language)
        
        # Parse trace from output
        if result.success and result.stdout:
            try:
                # Extract JSON trace from output
                trace_json = result.stdout
                trace_data = json.loads(trace_json)
                result.execution_trace = trace_data
            except json.JSONDecodeError:
                pass
        
        return result


def execute_jac_code(code: str, entry_point: str = "init",
                     timeout: int = None, memory_mb: int = None) -> ExecutionResult:
    """
    Execute Jaclang code with the specified options.
    
    This is a convenience wrapper around execute_code for Jaclang specifically.
    
    Args:
        code: Jaclang code to execute
        entry_point: Entry point walker/function
        timeout: Execution timeout in seconds
        memory_mb: Memory limit in MB
        
    Returns:
        ExecutionResult with execution details
    """
    return execute_code(
        code=code,
        language="jac",
        entry_point=entry_point,
        timeout=timeout,
        memory_mb=memory_mb
    )


def execute_code(code: str, language: str = "jac", entry_point: str = "init",
                 mode: str = "run", input_data: str = None,
                 timeout: int = None, memory_mb: int = None,
                 test_cases: List[Dict] = None, snippet_id: str = None) -> ExecutionResult:
    """
    Execute code with the specified language and options.
    
    Args:
        code: Code to execute
        language: Programming language (python, javascript, jac)
        entry_point: Entry point for Jac
        mode: Execution mode (run, debug, grade)
        input_data: Standard input
        timeout: Timeout in seconds
        memory_mb: Memory limit in MB
        test_cases: List of test cases for grading
        snippet_id: Snippet ID for test case lookup
        
    Returns:
        ExecutionResult with execution details
    """
    executor = MultiLanguageExecutor()
    analyzer = ErrorAnalyzer()
    
    # Handle different modes
    if mode == "grade":
        grader = AutoGrader()
        result, _ = grader.grade_submission(code, language, snippet_id, test_cases)
    elif mode == "debug":
        debugger = TraceDebugger()
        result = debugger.execute_with_trace(code, language)
    else:
        # Regular execution
        result = executor.execute(code, language, entry_point, timeout, memory_mb, input_data)
    
    # Add educational hints if there was an error
    if not result.success and result.stderr:
        hints = analyzer.analyze_error(result.stderr, language)
        result.hint = hints.get('friendly_message')
        result.suggestion = hints.get('suggestion')
        result.resource_link = hints.get('resource_link')
    
    return result


if __name__ == "__main__":
    # Test execution engine
    print("Testing Enhanced Code Execution Engine...")
    print("=" * 60)
    
    # Test Python
    python_code = '''
print("Hello from Python!")
x = 5
y = 10
print(f"Sum: {x + y}")
'''
    
    print("\n1. Testing Python execution:")
    result = execute_code(python_code, language="python")
    print(f"   Status: {result.status}")
    print(f"   Output: {result.stdout}")
    
    # Test JavaScript
    js_code = '''
console.log("Hello from JavaScript!");
const x = 5;
const y = 10;
console.log("Sum:", x + y);
'''
    
    print("\n2. Testing JavaScript execution:")
    result = execute_code(js_code, language="javascript")
    print(f"   Status: {result.status}")
    print(f"   Output: {result.stdout}")
    
    # Test error analysis
    print("\n3. Testing error analysis:")
    error_code = '''
print("Hello"
x = 5
y = 10
print(x + y)
'''
    result = execute_code(error_code, language="python")
    print(f"   Error: {result.stderr}")
    print(f"   Hint: {result.hint}")
    print(f"   Suggestion: {result.suggestion}")
    
    print("\n" + "=" * 60)
    print("Code Execution Engine tests completed!")


def evaluate_expression(code: str, expression: str, current_line: int = 1, variables: dict = None) -> Dict[str, Any]:
    """
    Safely evaluate an expression in the context of the provided code.
    Used for debug sessions.
    """
    try:
        # Create a safe context with provided variables
        local_context = variables or {}
        
        # Simple evaluation (in a real scenario, this should be sandboxed)
        # This is a placeholder implementation.
        result = str(expression)  # Mock result for now
        
        return {
            "success": True,
            "result": f"Evaluated: {expression} => [Mock Result]",
            "variables": local_context
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def compile_to_ir(code: str, entry_point: str = "init") -> Dict[str, Any]:
    """
    Compile Jaclang code to Intermediate Representation (IR).
    
    Args:
        code: Jaclang code to compile
        entry_point: Entry point walker/function
        
    Returns:
        Dict with success status, ir_output, and any errors
    """
    import tempfile
    import shutil
    
    executor = MultiLanguageExecutor()
    
    # Validate input
    if not code or not code.strip():
        return {
            "success": False,
            "error": "No code provided",
            "ir_output": None
        }
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="compile_ir_")
    try:
        # Write code to file
        code_file = executor.sandbox.write_code_file(temp_dir, code, "jac")
        
        # Build compile command
        cmd = ['jac', 'compile', '--ir', code_file]
        if entry_point:
            cmd.extend(['--entry', entry_point])
        
        # Execute compile command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=temp_dir
        )
        
        if result.returncode == 0:
            # Compilation successful - look for IR output
            ir_file = code_file.replace('.jac', '.ir')
            if os.path.exists(ir_file):
                with open(ir_file, 'r') as f:
                    ir_output = f.read()
                return {
                    "success": True,
                    "ir_output": ir_output,
                    "error": None
                }
            else:
                return {
                    "success": True,
                    "ir_output": result.stdout,
                    "error": None
                }
        else:
            return {
                "success": False,
                "ir_output": None,
                "error": result.stderr.strip() or "Compilation failed"
            }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "ir_output": None,
            "error": "Compilation timed out after 30 seconds"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "ir_output": None,
            "error": "jac command not found. Please install jaclang package."
        }
    except Exception as e:
        return {
            "success": False,
            "ir_output": None,
            "error": str(e)
        }
    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass
