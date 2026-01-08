import os
import json

class Config:
    # Get base directory
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
    
    # Defaults
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-123')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SKIP_LICENSE = False
    
    # Load from config.json if exists
    config_path = os.path.join(INSTANCE_DIR, 'config.json')
    if os.path.exists(config_path):
        with open(config_path) as f:
            data = json.load(f)
            SECRET_KEY = data.get('SECRET_KEY', SECRET_KEY)
            SQLALCHEMY_DATABASE_URI = data.get('SQLALCHEMY_DATABASE_URI', 
                f"sqlite:///{os.path.join(INSTANCE_DIR, 'exam_data.db')}")
            SKIP_LICENSE = data.get('SKIP_LICENSE', False)
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_DIR, 'exam_data.db')}"
