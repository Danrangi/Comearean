import os
import json

class Config:
    # Force the base directory to be the absolute path of the project root
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-123')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SKIP_LICENSE = False
    
    # Ensure instance directory exists
    if not os.path.exists(INSTANCE_DIR):
        os.makedirs(INSTANCE_DIR)

    config_path = os.path.join(INSTANCE_DIR, 'config.json')
    if os.path.exists(config_path):
        with open(config_path) as f:
            data = json.load(f)
            SECRET_KEY = data.get('SECRET_KEY', SECRET_KEY)
            SKIP_LICENSE = data.get('SKIP_LICENSE', False)
    
    # Use absolute path for SQLite
    db_path = os.path.join(INSTANCE_DIR, 'exam_data.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
