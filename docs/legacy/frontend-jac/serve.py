#!/usr/bin/env python3
"""
JAC Frontend Development Server
Simple HTTP server to serve the JAC frontend during development
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Configuration
PORT = 8080
FRONTEND_DIR = Path(__file__).parent
INDEX_FILE = FRONTEND_DIR / "index.html"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve JAC frontend files"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)
    
    def end_headers(self):
        # Add CORS headers for development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Custom logging with timestamps
        print(f"[{self.address_string()}] {format % args}")
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.path = '/index.html'
        
        # Check if file exists
        file_path = FRONTEND_DIR / self.path.lstrip('/')
        if file_path.is_file():
            super().do_GET()
        else:
            # Return 404 for missing files
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_message = f"""
            <html>
            <head><title>404 Not Found</title></head>
            <body>
                <h1>404 - File Not Found</h1>
                <p>The requested file <code>{self.path}</code> was not found.</p>
                <p><a href="/">Return to Home</a></p>
            </body>
            </html>
            """
            self.wfile.write(error_message.encode())

def check_dependencies():
    """Check if all required files exist"""
    required_files = [
        "index.html",
        "app.jac", 
        "styles/main.css",
        "components/__init__.jac",
        "pages/__init__.jac",
        "services/__init__.jac"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (FRONTEND_DIR / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ All required files present")
    return True

def start_server():
    """Start the development server"""
    print("🚀 Starting JAC Frontend Development Server")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please ensure all JAC frontend files are present")
        return False
    
    # Change to frontend directory
    os.chdir(FRONTEND_DIR)
    
    try:
        # Create server
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            server_url = f"http://localhost:{PORT}"
            
            print(f"📡 Server running at: {server_url}")
            print(f"📁 Serving files from: {FRONTEND_DIR}")
            print(f"🏠 Frontend URL: {server_url}")
            print(f"📚 Backend API: http://127.0.0.1:8000")
            print(f"📖 API Docs: http://127.0.0.1:8000/docs")
            print("\n" + "=" * 50)
            print("🎯 Quick Access:")
            print(f"   Frontend: {server_url}")
            print(f"   Backend:  http://127.0.0.1:8000")
            print("=" * 50)
            print("💡 Press Ctrl+C to stop the server")
            print()
            
            # Try to open browser automatically
            try:
                webbrowser.open(server_url)
                print("🌐 Opened browser automatically")
            except Exception as e:
                print(f"⚠️  Could not open browser automatically: {e}")
                print(f"   Please manually open: {server_url}")
            
            # Start serving
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        return True
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ Port {PORT} is already in use")
            print(f"   Please stop any existing server or use a different port")
            return False
        else:
            print(f"❌ Server error: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function"""
    print("🎓 Jeseci Smart Learning Companion - JAC Frontend Server")
    print("Powered by JAC Runtime and FastAPI")
    print()
    
    # Check if backend is running
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/health", timeout=2)
        if response.status_code == 200:
            print("✅ FastAPI backend is running")
        else:
            print("⚠️  FastAPI backend responded but with error status")
    except Exception:
        print("⚠️  FastAPI backend is not running")
        print("   Please start the backend with: python main.py")
        print("   The frontend will still work but API calls will fail")
        print()
    
    # Start the server
    success = start_server()
    
    if success:
        print("\n✅ Server shutdown completed")
    else:
        print("\n❌ Server failed to start")
    
    return success

if __name__ == "__main__":
    main()