import os
import sys
from waitress import serve

# Get the absolute path of the directory containing run.py
root_path = os.path.dirname(os.path.abspath(__file__))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from src.app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # Forces development mode if FLASK_ENV is not specifically set to production
    env = os.environ.get("FLASK_ENV", "development")
    
    if env == "development":
        print(f"[*] Development server: http://0.0.0.0:{port}")
        app.run(host="0.0.0.0", port=port, debug=True)
    else:
        print(f"[*] Production server (Waitress) on port {port}")
        serve(app, host="0.0.0.0", port=port, threads=50)
