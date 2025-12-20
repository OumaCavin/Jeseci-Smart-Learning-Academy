#!/usr/bin/env python3
"""
Jeseci Backend Startup Script with Logging
"""
import os
import sys
import logging

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Start the Jeseci backend with proper logging"""
    try:
        print("🚀 Starting Jeseci Smart Learning Companion API...")
        print("📝 Logging configured for console and file output")
        print("📁 Check 'logs/' directory for detailed log files")
        print("-" * 50)
        
        # Import and run uvicorn
        import uvicorn
        from main import app
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            log_config=None  # Use our custom logging configuration
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Jeseci API...")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        logging.error(f"Server startup failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()