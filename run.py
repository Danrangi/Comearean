import os
import sys
import webbrowser
import platform
from threading import Timer
from waitress import serve
from src.app import create_app

# Get the absolute path of the directory containing run.py
root_path = os.path.dirname(os.path.abspath(__file__))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

app = create_app()

def open_browser():
    """Auto-opens the browser for the admin on the server"""
    webbrowser.open_new('http://localhost:8080')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    # CHECK: Are we running as a Python script or a Frozen EXE?
    if getattr(sys, 'frozen', False):
        # --- PRODUCTION MODE (EXE) ---
        print(f"[*] STARTING EXAM ARENA SERVER (Production)")
        print(f"[*] Status: ONLINE")
        print(f"[*] Address: http://localhost:{port}")
        print(f"[*] Network Access: http://{platform.node()}:{port}")
        
        # Open browser automatically after 1.5 seconds
        Timer(1.5, open_browser).start()
        
        # Run with Waitress (The "W")
        serve(app, host="0.0.0.0", port=port, threads=50)
        
    else:
        # --- DEVELOPMENT MODE (Script) ---
        # Only use Flask Debugger when we are coding (python run.py)
        print(f"[*] Development server: http://0.0.0.0:{port}")
        app.run(host="0.0.0.0", port=port, debug=True)
