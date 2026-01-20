import os
import sys
import getpass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.app import db, create_app
from src.app.models import User

app = create_app()
with app.app_context():
    print("--- Create Super Admin ---")
    username = input("Enter Username (default: admin): ").strip() or "admin"
    
    # Check if exists
    if User.query.filter_by(username=username).first():
        print(f"[-] User '{username}' already exists!")
        sys.exit(1)

    password = getpass.getpass(f"Enter Password for '{username}': ")
    confirm = getpass.getpass("Confirm Password: ")
    
    if password != confirm:
        print("[-] Passwords do not match!")
        sys.exit(1)
        
    user = User(username=username, role='superadmin')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f"[+] Super Admin '{username}' created successfully.")
