import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.app import db, create_app
from src.app.models import Exam

app = create_app()
with app.app_context():
    if not Exam.query.filter_by(name='JAMB').first():
        db.session.add(Exam(name='JAMB'))
        db.session.add(Exam(name='WAEC'))
        db.session.commit()
        print("[+] Standard Exam types created.")
