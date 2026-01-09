import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import db, create_app

app = create_app()
with app.app_context():
    db.create_all()
    print("[+] Database recreated with duration_minutes and required_subjects columns.")
