#!/usr/bin/env python3
"""
Custom Jaclang Server with CORS Fix for PUT Method
This script patches the Jaclang server to include PUT in allowed CORS methods.
"""

import sys
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Add backend to path
sys.path.insert(0, SCRIPT_DIR)

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
from jaclang.runtimelib.server import JacAPIServer

if __name__ == "__main__":
    # Configuration
    port = int(os.environ.get("PORT", 8000))
    module_name = "backend.app"
    session_path = os.path.join(SCRIPT_DIR, "sessions")
    
    print(f"Starting Jaclang server with CORS fix on port {port}")
    print("CORS methods now include: GET, POST, PUT, DELETE, OPTIONS")
    
    # Create and start the server
    server = JacAPIServer(
        module_name=module_name,
        session_path=session_path,
        port=port
    )
    
    # Start the server
    server.start()
