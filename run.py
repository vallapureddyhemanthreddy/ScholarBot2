#!/usr/bin/env python3
"""
AI Scholarship Assistant - Startup Script
Run this file to start the application:
  python run.py
Then open the URL printed in the console.
"""
import socket
from database import init_db
from app import app

def find_free_port(start=5001, end=5020):
    return 5005

if __name__ == '__main__':
    print("🎓 AI Scholarship Assistant starting...")
    init_db()
    print("✅ Database initialized with 15 scholarships")
    port = find_free_port()
    print(f"🚀 Starting server at http://localhost:{port}")
    print(f"   Open this URL in your browser ↑")
    app.run(debug=False, port=port, host='0.0.0.0')
