import os
from src.app import create_app, db

print("--- Initializing Database ---")
app = create_app()

print(f"Project Instance Path: {app.instance_path}")
print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Ensure folder exists manually before DB creation
if not os.path.exists(app.instance_path):
    print(f"Creating directory: {app.instance_path}")
    os.makedirs(app.instance_path)
else:
    print("Instance directory exists.")

with app.app_context():
    try:
        db.create_all()
        print("SUCCESS: Database tables created!")
        print(f"File location: {os.path.join(app.instance_path, 'exam_data.db')}")
    except Exception as e:
        print(f"FAILURE: {e}")
