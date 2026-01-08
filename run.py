import os
from src.app import create_app
from waitress import serve

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    env = os.environ.get("FLASK_ENV", "production")
    
    if env == "development":
        app.run(host="0.0.0.0", port=port, debug=True)
    else:
        print(f"Server starting on http://0.0.0.0:{port}")
        serve(app, host="0.0.0.0", port=port, threads=100)
