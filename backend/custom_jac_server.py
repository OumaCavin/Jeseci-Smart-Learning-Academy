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
