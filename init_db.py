from src.app import db, create_app
import os

app = create_app()
with app.app_context():
    try:
        # Ensure the instance folder exists inside app context logic
        if not os.path.exists(app.instance_path):
            os.makedirs(app.instance_path)
            
        db.create_all()
        print("---------------------------------------")
        print("SUCCESS: Database tables created!")
        print(f"Location: {os.path.abspath('instance/exam_data.db')}")
        print("---------------------------------------")
    except Exception as e:
        print("---------------------------------------")
        print(f"ERROR: Could not create database: {e}")
        print("---------------------------------------")
