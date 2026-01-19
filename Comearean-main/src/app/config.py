import os
import sys
import json

class Config:
    # --- LOGIC FOR EXE DATA PERSISTENCE ---
    if getattr(sys, 'frozen', False):
        # If running as a compiled .exe, use the folder where the .exe sits
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        # If running as a standard python script, use the project root
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-123')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SKIP_LICENSE = False
    
    # Ensure instance directory exists
    if not os.path.exists(INSTANCE_DIR):
        try:
            os.makedirs(INSTANCE_DIR)
        except OSError:
            pass # Ignore if it exists or permission issues (handled by write checks later)

    config_path = os.path.join(INSTANCE_DIR, 'config.json')
    if os.path.exists(config_path):
        with open(config_path) as f:
            data = json.load(f)
            SECRET_KEY = data.get('SECRET_KEY', SECRET_KEY)
            SKIP_LICENSE = data.get('SKIP_LICENSE', False)
    
    # Use absolute path for SQLite
    db_path = os.path.join(INSTANCE_DIR, 'exam_data.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
