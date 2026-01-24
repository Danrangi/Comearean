import os
import sys

# Ensure src module can be found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import db, create_app
from src.app.models import User

app = create_app()

with app.app_context():
    print("--- Create or Update Super Admin ---")
    
    # 1. Try Environment Variables (For GitHub Actions)
    # 2. Try Interactive Input (For Local Testing)
    # 3. Fallback to Defaults (Safety Net)
    
    username = os.environ.get("SUPER_USER")
    if not username:
        try:
            username = input("Enter Username (default: CExamArena): ").strip() or "CExamArena"
        except EOFError:
            username = "CExamArena"

    password = os.environ.get("SUPER_PASS")
    if not password:
        try:
            print("Note: Password will be visible.")
            password = input(f"Enter Password for {username}: ").strip() or "CExamArena@2026"
        except EOFError:
            password = "CExamArena@2026"
            
    # Create User Logic
    existing_user = User.query.filter_by(username=username).first()
    
    if existing_user:
        existing_user.set_password(password)
        existing_user.role = 'superadmin'
        print(f"[+] Updated existing user '{username}'.")
    else:
        new_user = User(username=username, role='superadmin')
        new_user.set_password(password)
        db.session.add(new_user)
        print(f"[+] Created new Super Admin '{username}'.")

    db.session.commit()
    print("[SUCCESS] Super Admin ready.")
