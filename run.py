import os
import sys
import webbrowser
import platform
from threading import Timer
from waitress import serve
from src.app import create_app

def _bootstrap_database(app):
    """
    Ensures DB + tables exist in packaged builds.
    Safe: runs only if tables are missing.
    """
    try:
        from sqlalchemy import text
        from src.app import db
        from src.app.models.user import User  # adjust if your path differs

        with app.app_context():
            # Create tables (no-op if they already exist)
            db.create_all()

            # Quick check: does "user" table exist?
            # SQLite: querying sqlite_master is safe.
            r = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")).fetchone()
            if not r:
                # create_all should have created it; if not, something is wrong
                db.create_all()

            # Ensure superadmin exists (uses your known credentials)
            username = "CExamArena"
            password = "CExamArena@2026"

            existing = User.query.filter_by(username=username).first()
            if not existing:
                u = User(username=username, role="superadmin")
                # Try common methods; fallback to direct hash setter if present
                if hasattr(u, "set_password"):
                    u.set_password(password)
                elif hasattr(u, "password_hash"):
                    # If your model expects already-hashed, your login code will fail.
                    # But most of your repo uses set_password; this is just a fallback.
                    u.password_hash = password
                db.session.add(u)
                db.session.commit()
                print("[*] Bootstrapped superadmin: CExamArena")
            else:
                print("[*] Superadmin exists.")
    except Exception as e:
        print("[!] DB bootstrap warning:", e)
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