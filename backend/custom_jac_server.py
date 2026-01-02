#!/usr/bin/env python3
"""
Custom Jaclang Server with CORS Fix for PUT Method
This script patches the Jaclang server CORS headers before starting with jac serve.
"""

import sys
import os

# Patch CORS headers BEFORE jac serve imports anything
from jaclang.runtimelib import server as jac_server

# Store original method
original_add_cors_headers = jac_server.ResponseBuilder._add_cors_headers

def patched_add_cors_headers(handler):
    """Patched CORS headers that include PUT/DELETE methods."""
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

# Apply the patch
jac_server.ResponseBuilder._add_cors_headers = staticmethod(patched_add_cors_headers)

# Now spawn jac serve as a subprocess
if __name__ == "__main__":
    # Get the project root directory (parent of backend/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    backend_dir = script_dir
    jac_file = os.path.join(backend_dir, "app.jac")
    
    print("🚀 Starting Jeseci Smart Learning Academy Backend Server...")
    print("📋 Using CORS fix for PUT/DELETE method support")
    print("")
    
    # Verify the jac file exists
    if not os.path.exists(jac_file):
        print(f"❌ Error: {jac_file} not found!")
        sys.exit(1)
    
    print("🌐 Starting Jaclang server...")
    print("🔧 CORS methods: GET, POST, PUT, DELETE, OPTIONS")
    print("")
    
    # Run jac serve from PROJECT ROOT (not backend directory)
    # This ensures imports like 'import backend.database' work correctly
    try:
        # Change to project root and run jac serve with backend/app.jac
        cmd = f'cd "{project_root}" && jac serve backend/app.jac --port 8000'
        print(f"Running: {cmd}")
        result = os.system(cmd)
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
