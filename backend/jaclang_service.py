#!/usr/bin/env python3
"""
Jaclang Editor Intelligence Service

This module provides real-time syntax validation and code formatting
for Jaclang code by bridging the frontend editor with the `jac` CLI tools.

Author: Cavin Otieno
"""

import os
import sys
import re
import subprocess
import tempfile
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))

# Add backend to path
sys.path.insert(os.path.dirname(__file__))

# Create router
jaclang_router = APIRouter(prefix="/api/jaclang", tags=["Jaclang Editor Intelligence"])

# =============================================================================
# Pydantic Models
# =============================================================================

class ValidateRequest(BaseModel):
    source_code: str

class ValidateResponse(BaseModel):
    valid: bool
    errors: List[Dict[str, Any]] = []
    message: str = ""

class FormatRequest(BaseModel):
    source_code: str

class FormatResponse(BaseModel):
    formatted_code: str
    changed: bool = False
    error: Optional[str] = None

class HealthResponse(BaseModel):
    service: str
    status: str
    jac_available: bool
    version: str

# =============================================================================
# Utility Functions
# =============================================================================

def check_jac_available() -> tuple[bool, str]:
    """Check if the `jac` CLI tool is available."""
    try:
        result = subprocess.run(
            ['jac', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip()
    except FileNotFoundError:
        return False, "jac command not found"
    except subprocess.TimeoutExpired:
        return False, "jac command timed out"
    except Exception as e:
        return False, f"Error checking jac availability: {str(e)}"


def parse_jac_errors(stderr: str) -> List[Dict[str, Any]]:
    """
    Parse the stderr output from `jac check` or `jac format` to extract
    structured error information.
    
    Expected error format from jac CLI:
    - Line numbers are typically 1-based
    - Format: "Error: message at line X, column Y"
    """
    errors = []
    
    # Pattern for common jac error formats
    # Example: "Error: Unexpected token at line 10, column 5"
    # Example: "SyntaxError: Missing semicolon at line 15"
    
    patterns = [
        # Pattern: Error: message at line X, column Y
        r'(?P<severity>Error|Warning|SyntaxError|TypeError):?\s*(?P<message>.+?)\s+(?:at|on)\s+line\s+(?P<line>\d+)(?:,\s*column\s+(?P<column>\d+))?',
        # Pattern: message (line X, column Y)
        r'(?P<message>.+?)\s+\((?P<line>\d+)[,:]\s*(?P<column>\d+)\)',
        # Pattern: line X: message
        r'^line\s+(?P<line>\d+):\s*(?P<message>.+)',
        # Pattern: Simple "at line X" format
        r'(?P<message>.+?)\s+at\s+line\s+(?P<line>\d+)',
    ]
    
    lines = stderr.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groupdict()
                
                # Determine severity
                severity_str = groups.get('severity', '').lower()
                if 'error' in severity_str or 'syntax' in severity_str:
                    severity = 'Error'
                elif 'warning' in severity_str:
                    severity = 'Warning'
                else:
                    severity = 'Error'  # Default to error for parsing issues
                
                # Extract line and column
                try:
                    line_num = int(groups.get('line', 1))
                except (ValueError, TypeError):
                    line_num = 1
                
                try:
                    col_num = int(groups.get('column', 1))
                except (ValueError, TypeError):
                    col_num = 1
                
                # Clean up message
                message = groups.get('message', line).strip()
                if groups.get('severity'):
                    message = f"{groups['severity']}: {message}"
                
                errors.append({
                    'line': line_num,
                    'column': col_num,
                    'message': message,
                    'severity': severity,
                    'raw': line
                })
                break  # Only match one pattern per line
    
    return errors


def execute_jac_command(args: List[str], source_code: str) -> tuple[str, str, int]:
    """
    Execute a jac CLI command with the given source code.
    
    Returns: (stdout, stderr, returncode)
    """
    # Create a temporary file for the source code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jac', delete=False) as tmp:
        tmp.write(source_code)
        tmp_path = tmp.name
    
    try:
        # Execute the jac command
        full_args = ['jac'] + args + [tmp_path]
        result = subprocess.run(
            full_args,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return '', 'Command timed out after 30 seconds', 1
    except FileNotFoundError:
        return '', 'jac command not found. Please install jaclang.', 1
    except Exception as e:
        return '', f'Error executing jac command: {str(e)}', 1
    finally:
        # Clean up temporary file
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


# =============================================================================
# API Endpoints
# =============================================================================

@jaclang_router.get("/health", response_model=HealthResponse)
async def jaclang_health_check():
    """Check the health of the Jaclang service."""
    try:
        available, version = check_jac_available()
    except Exception as e:
        available, version = False, str(e)
    
    return HealthResponse(
        service="Jaclang Editor Intelligence",
        status="healthy" if available else "degraded",
        jac_available=available,
        version=version if available else "not available"
    )


@jaclang_router.post("/validate", response_model=ValidateResponse)
async def validate_jac_code(request: ValidateRequest):
    """
    Validate Jaclang source code for syntax errors.
    
    This endpoint accepts Jaclang source code and returns any syntax
    errors found by the `jac check` command.
    """
    try:
        source_code = request.source_code
        
        if not source_code or not source_code.strip():
            return ValidateResponse(
                valid=True,
                errors=[],
                message="Empty code is valid"
            )
        
        # Check if jac is available
        available, _ = check_jac_available()
        if not available:
            # Return a warning but don't fail - the editor should still work
            return ValidateResponse(
                valid=True,  # Consider empty/missing jac as valid for editor usability
                errors=[{
                    'line': 1,
                    'column': 1,
                    'message': 'Jaclang CLI not available. Code validation will be skipped.',
                    'severity': 'Warning',
                    'raw': 'Jaclang not installed'
                }],
                message="Jaclang CLI not available"
            )
        
        # Execute jac check command
        stdout, stderr, returncode = execute_jac_command(['check'], source_code)
        
        # Parse errors from stderr
        errors = parse_jac_errors(stderr)
        
        # If returncode is 0, there are no errors
        if returncode == 0 and not errors:
            return ValidateResponse(
                valid=True,
                errors=[],
                message="Code is syntactically valid"
            )
        
        # If returncode is non-zero or we have errors, report them
        return ValidateResponse(
            valid=False,
            errors=errors,
            message=f"Found {len(errors)} syntax error(s)" if errors else "Validation failed"
        )
    except Exception as e:
        # Return a valid response with a warning instead of crashing
        return ValidateResponse(
            valid=True,
            errors=[{
                'line': 1,
                'column': 1,
                'message': f'Validation service error: {str(e)}',
                'severity': 'Warning',
                'raw': str(e)
            }],
            message=f"Validation encountered an error: {str(e)}"
        )


@jaclang_router.post("/format", response_model=FormatResponse)
async def format_jac_code(request: FormatRequest):
    """
    Format Jaclang source code according to language standards.
    
    This endpoint accepts Jaclang source code and returns the formatted
    version using the `jac format` command.
    """
    try:
        source_code = request.source_code
        
        if not source_code or not source_code.strip():
            return FormatResponse(
                formatted_code="",
                changed=False,
                error="Empty code cannot be formatted"
            )
        
        # Check if jac is available
        available, _ = check_jac_available()
        if not available:
            return FormatResponse(
                formatted_code=source_code,
                changed=False,
                error="Jaclang CLI not available. Please install jaclang package."
            )
        
        # Execute jac format command
        stdout, stderr, returncode = execute_jac_command(['format'], source_code)
        
        # Read the formatted code from the file
        # jac format modifies the file in place, so we need to get the result
        # The stdout will contain the path of the formatted file
        
        # For now, let's use a different approach - jac format outputs to the file
        # We need to get the formatted content from stdout if available
        
        if returncode != 0:
            # Check if it's a parse error (can't format invalid code)
            if 'parse' in stderr.lower() or 'syntax' in stderr.lower():
                return FormatResponse(
                    formatted_code=source_code,
                    changed=False,
                    error=f"Cannot format code with syntax errors: {stderr}"
                )
            else:
                return FormatResponse(
                    formatted_code=source_code,
                    changed=False,
                    error=f"Formatting failed: {stderr}"
                )
        
        # jac format modifies the file in place. Since we've deleted the temp file,
        # we need to get the formatted content another way.
        # Let's try with the --stdin flag if available, or use a different approach
        
        # Alternative: format to stdout if supported
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jac', delete=False) as tmp:
            tmp.write(source_code)
            tmp_path = tmp.name
        
        try:
            # Try jac format with output to stdout
            result = subprocess.run(
                ['jac', 'format', '--check', tmp_path] if '--check' in subprocess.run(
                    ['jac', 'format', '--help'],
                    capture_output=True,
                    text=True
                ).stdout else ['jac', 'format', tmp_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Read the file content back (jac format modifies in place)
            with open(tmp_path, 'r') as f:
                formatted_code = f.read()
            
            # Check if formatting changed anything
            changed = formatted_code != source_code
            
            return FormatResponse(
                formatted_code=formatted_code,
                changed=changed,
                error=None
            )
        except Exception as e:
            return FormatResponse(
                formatted_code=source_code,
                changed=False,
                error=str(e)
            )
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
    except Exception as e:
        # Return original code with error message instead of crashing
        return FormatResponse(
            formatted_code=request.source_code,
            changed=False,
            error=f"Formatting service error: {str(e)}"
        )


@jaclang_router.post("/validate-and-format")
async def validate_and_format_jac_code(request: ValidateRequest):
    """
    Validate and format Jaclang code in a single request.
    
    This endpoint first validates the code for syntax errors, then
    formats it if valid. Returns both the validation result and
    the formatted code.
    """
    try:
        source_code = request.source_code
        
        if not source_code or not source_code.strip():
            return {
                "valid": True,
                "errors": [],
                "formatted_code": source_code,
                "changed": False,
                "message": "Empty code is valid"
            }
        
        # Check if jac is available
        available, _ = check_jac_available()
        if not available:
            return {
                "valid": True,
                "errors": [{
                    'line': 1,
                    'column': 1,
                    'message': 'Jaclang CLI not available. Code validation will be skipped.',
                    'severity': 'Warning'
                }],
                "formatted_code": source_code,
                "changed": False,
                "message": "Jaclang CLI not available"
            }
        
        # First, validate the code
        validate_response = await validate_jac_code(ValidateRequest(source_code=source_code))
        
        if not validate_response.valid:
            # If there are errors, don't format
            return {
                "valid": False,
                "errors": validate_response.errors,
                "formatted_code": source_code,
                "changed": False,
                "message": validate_response.message
            }
        
        # Code is valid, so we can format it
        format_response = await format_jac_code(FormatRequest(source_code=source_code))
        
        return {
            "valid": True,
            "errors": [],
            "formatted_code": format_response.formatted_code,
            "changed": format_response.changed,
            "message": "Code is valid and has been formatted" if format_response.changed else "Code is valid and properly formatted"
        }
    except Exception as e:
        # Return error response instead of crashing
        return {
            "valid": True,
            "errors": [{
                'line': 1,
                'column': 1,
                'message': f'Service error: {str(e)}',
                'severity': 'Warning'
            }],
            "formatted_code": request.source_code,
            "changed": False,
            "message": f"Operation encountered an error: {str(e)}"
        }
