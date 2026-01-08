import os
import sys
from waitress import serve

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # Check if in development (Codespaces default is usually development)
    if os.environ.get("FLASK_ENV") == "development":
        app.run(host="0.0.0.0", port=port, debug=True)
    else:
        print(f"Starting Production Server on port {port}...")
        serve(app, host="0.0.0.0", port=port, threads=50)
