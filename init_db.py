import os
import sys
# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import db, create_app

app = create_app()
with app.app_context():
    # Print where we are trying to create the DB
    print(f"[*] Targeting DB at: {app.config['SQLALCHEMY_DATABASE_URI']}")
    db.create_all()
    print("[+] Database initialized successfully.")
