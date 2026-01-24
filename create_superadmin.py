import os
import sys

# Ensure src module can be found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import db, create_app
from src.app.models import User

app = create_app()

def get_input_or_default(prompt, default_value):
    """Try to get input, but return default if running in CI/Non-interactive mode"""
    try:
        val = input(prompt).strip()
        return val if val else default_value
    except EOFError:
        # This block catches the error in GitHub Actions
        print(f"[*] Non-interactive mode detected. Using default: {default_value}")
        return default_value

with app.app_context():
    print("--- Create or Update Super Admin ---")
    
    # 1. Get Username (Default to CExamArena for the build)
    username = get_input_or_default("Enter Username (default: CExamArena): ", "CExamArena")
    
    # 2. Get Password (Default to CExamArena@2026 for the build)
    print("NOTE: Password will be visible as you type.")
    password = get_input_or_default(f"Enter New Password for '{username}': ", "CExamArena@2026")
    
    # 3. Confirm Password (logic handled automatically in non-interactive)
    try:
        confirm = input("Confirm Password: ").strip()
    except EOFError:
        confirm = password

    if password != confirm:
        print("[-] Passwords do not match!")
        sys.exit(1)
    
    if not password:
         print("[-] Password cannot be empty.")
         sys.exit(1)

    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    
    if existing_user:
        existing_user.set_password(password)
        existing_user.role = 'superadmin'
        print(f"[+] Updated existing user '{username}' with new password.")
    else:
        new_user = User(username=username, role='superadmin')
        new_user.set_password(password)
        db.session.add(new_user)
        print(f"[+] Created new Super Admin '{username}'.")

    db.session.commit()
    print("[SUCCESS] Super Admin ready.")
