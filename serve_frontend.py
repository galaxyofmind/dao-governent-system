#!/usr/bin/env python3
"""
Simple HTTP server for the DAO Governance frontend
"""
import http.server
import socketserver
import os
import sys

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    # Change to frontend directory
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    os.chdir(frontend_dir)
    
    Handler = MyHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║        🚀 DAO Governance Frontend Server Running         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

📍 Server Address: http://localhost:{PORT}
📁 Serving from:   {os.getcwd()}

🔗 Open your browser and navigate to:
   http://localhost:{PORT}

⚠️  Make sure:
   ✓ Ganache is running on port 8545
   ✓ Contract is deployed
   ✓ MetaMask is installed and configured

Press Ctrl+C to stop the server
        """)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped. Goodbye!")
            sys.exit(0)

if __name__ == "__main__":
    main()
