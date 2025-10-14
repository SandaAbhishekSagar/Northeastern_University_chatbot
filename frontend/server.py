#!/usr/bin/env python3
"""
Simple HTTP server for the University Chatbot frontend
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Get the directory where this script is located
FRONTEND_DIR = Path(__file__).parent.absolute()

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow cross-origin requests
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.end_headers()

def main():
    # Change to the frontend directory
    os.chdir(FRONTEND_DIR)
    
    # Use Railway's assigned port if available
    PORT = int(os.environ.get("PORT", 3000))

    # Generate a runtime config file for the frontend from env vars
    api_base_url = os.environ.get("API_BASE_URL", "")
    try:
        with open("config.js", "w", encoding="utf-8") as f:
            f.write("window.API_BASE_URL = \"" + api_base_url.replace("\\", "\\\\").replace("\"", "\\\"") + "\";\n")
        print(f"[CFG] Wrote config.js with API_BASE_URL='{api_base_url}'")
    except Exception as e:
        print(f"[WARN] Could not write config.js: {e}")
    
    print(f"[START] Starting University Chatbot Frontend Server")
    print(f"[DIR] Serving files from: {FRONTEND_DIR}")
    print(f"[URL] Frontend URL: http://0.0.0.0:{PORT}")
    print(f"[API] Default API URL assumption: http://localhost:8001 (override via API_BASE_URL env var)")
    print(f"[INFO] On Railway, set API_BASE_URL env var to your external GPU API host (e.g., https://gpu-host:8001)")
    print(f"[STOP] Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
            print(f"[OK] Server started successfully on port {PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[STOP] Server stopped by user")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"[ERROR] Port {PORT} is already in use. Please stop any other server using this port.")
        else:
            print(f"[ERROR] Error starting server: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

if __name__ == "__main__":
    main() 