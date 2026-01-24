import os
import sys
# We removed getpass so you can see what you type
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.app import db, create_app
from src.app.models import User

app = create_app()
with app.app_context():
    print("--- Create or Update Super Admin ---")
    username = input("Enter Username (default: admin): ").strip() or "admin"
    
    # VISIBLE INPUT VERSION
    print("NOTE: Password will be visible as you type.")
    password = input(f"Enter New Password for '{username}': ").strip()
    confirm = input("Confirm Password: ").strip()
    
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
    print("[SUCCESS] You can now log in.")
