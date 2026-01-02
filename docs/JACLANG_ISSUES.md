# Jaclang Library Issues Documentation

This document captures all issues discovered while using the Jaclang library during the development of Jeseci Smart Learning Academy. These issues are documented for reference and have been reported (or will be reported) to the Jaclang development team.

**Project**: Jeseci Smart Learning Academy  
**Repository**: https://github.com/OumaCavin/Jeseci-Smart-Learning-Academy  
**Document Created**: 2026-01-02  
**Last Updated**: 2026-01-02

---

## Issue #1: CORS - Built-in HTTP Server Missing PUT/DELETE Methods

### Severity: Medium

### Problem Description

The built-in Jaclang HTTP server (`jac serve`) has hardcoded CORS methods that only include `GET, POST, OPTIONS`. This prevents frontend applications from making PUT and DELETE requests to walkers due to CORS preflight failures.

### Error Message

```
Access to fetch at 'http://localhost:8000/walker/admin_users_update' from origin 'http://localhost:3000' has been blocked by CORS policy: Method PUT is not allowed by Access-Control-Allow-Methods in preflight response.
```

### Affected Endpoints

All walker endpoints that use PUT or DELETE HTTP methods are affected:
- `/walker/admin_users_update` (PUT)
- Any other update/delete walkers

### Environment

- **Jaclang Version**: 0.8.x (latest from PyPI)
- **Python Version**: 3.12
- **Operating System**: Linux
- **Frontend Framework**: React with Vite

### Location of Issue

**File**: `jaclang/runtimelib/server.py`  
**Line**: 666  
**Code**:
```python
handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
```

### Expected Behavior

The server should allow all standard REST methods:
```python
handler.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
```

### Impact

Any frontend application (React, Vue, Angular, etc.) making PUT/DELETE requests to the Jaclang server will fail with CORS errors during the preflight OPTIONS request. This breaks standard REST API patterns.

### Workaround Applied

A monkey-patch solution was implemented to fix this issue at runtime:

**File**: `backend/custom_jac_server.py`
```python
#!/usr/bin/env python3
"""
Custom Jaclang Server with CORS Fix for PUT Method
This script patches the Jaclang server to include PUT in allowed CORS methods.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Patch CORS headers BEFORE importing Jaclang server modules
from jaclang.runtimelib import server as jac_server

# Store original method
original_add_cors_headers = jac_server.ResponseBuilder._add_cors_headers

def patched_add_cors_headers(handler):
    """Patched CORS headers that include PUT method."""
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

# Apply the patch
jac_server.ResponseBuilder._add_cors_headers = staticmethod(patched_add_cors_headers)

# Now import and run the server
from jaclang.runtimelib.server import spawn_server

if __name__ == "__main__":
    # Set environment variables if needed
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"Starting Jaclang server with CORS fix on {host}:{port}")
    print("CORS methods now include: GET, POST, PUT, DELETE, OPTIONS")
    
    # Start the server
    spawn_server(host=host, port=port)
```

**Startup Script**: `backend/start_server.sh`
```bash
#!/bin/bash

# Jeseci Smart Learning Academy - Custom Backend Server Startup Script
# This script starts the Jaclang server with CORS fix for PUT method support

echo "🚀 Starting Jeseci Smart Learning Academy Backend Server..."
echo "📋 Using custom server with CORS fix for PUT method support"

# Navigate to backend directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ -d "../.venv" ]; then
    echo "✅ Found virtual environment"
else
    echo "⚠️ Virtual environment not found. Run ./scripts/setup.sh first."
    exit 1
fi

# Activate virtual environment
source ../.venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "🐍 Python version: $(python3 --version)"
echo ""

# Start the custom server with CORS fix
echo "🌐 Starting custom Jaclang server on port 8000..."
echo "🔧 CORS methods: GET, POST, PUT, DELETE, OPTIONS"
echo ""

# Use the custom server script instead of direct jac serve
python3 custom_jac_server.py

echo "🛑 Server stopped"
```

### Usage

Instead of running `jac serve backend/app.jac`, users should run:
```bash
bash backend/start_server.sh
```

Or directly:
```bash
python3 backend/custom_jac_server.py
```

### Suggested Fix

Update `jaclang/runtimelib/server.py` line 666 from:
```python
handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
```

To:
```python
handler.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
```

### Alternative Solutions

1. **Make CORS methods configurable** via environment variable:
   ```python
   import os
   allowed_methods = os.environ.get("CORS_ALLOWED_METHODS", "GET, POST, OPTIONS")
   handler.send_header("Access-Control-Allow-Methods", allowed_methods)
   ```

2. **Add configuration option to `jac serve` command**:
   ```bash
   jac serve app.jac --cors-methods "GET,POST,PUT,DELETE,OPTIONS"
   ```

3. **Make it configurable in the Jac file**:
   Add a special syntax in the Jaclang file to specify allowed CORS methods.

### GitHub Issue Link

**Status**: Not yet reported  
**Link**: (To be created at https://github.com/jaseci-labs/jaclang/issues)

---

## Issue #2: [TBD - Add Future Issues Here]

### Severity: [Low/Medium/High]

### Problem Description

[Description of the issue]

### Error Message

```
[Error message here]
```

### Environment

- **Jaclang Version**: 
- **Python Version**: 
- **Operating System**: 

### Location of Issue

**File**:  
**Line**:  

### Expected Behavior

[What should happen]

### Impact

[Impact on users/developers]

### Workaround

[Any workaround discovered]

### Suggested Fix

[Proposed solution]

### GitHub Issue Link

**Status**: [Open/Pending/Closed]  
**Link**: [GitHub issue URL]

---

## Contributing to This Document

When encountering new issues with the Jaclang library:

1. Reproduce the issue consistently
2. Document all environment details
3. Capture exact error messages and stack traces
4. Note the file and line number where the issue occurs
5. Document any workarounds discovered
6. Report the issue to the Jaclang team
7. Update this document with the issue details

---

## References

- **Jaclang Official Repository**: https://github.com/jaseci-labs/jaclang
- **Jaclang Documentation**: https://jac-lang.org/
- **Jaseci Discord Community**: https://discord.gg/jaseci
- **Jaclang PyPI Package**: https://pypi.org/project/jaclang/
- **Contributing Guide**: https://jac-lang.org/internals/contrib/

---

## License

This document is part of the Jeseci Smart Learning Academy project and is licensed under the MIT License.
