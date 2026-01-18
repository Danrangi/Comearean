import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.app import db, create_app
from src.app.models import Exam

app = create_app()
with app.app_context():
    # Clear existing to prevent duplicates
    Exam.query.delete()
    
    jamb = Exam(name='JAMB', duration_minutes=120, required_subjects=4)
    waec = Exam(name='WAEC', duration_minutes=60, required_subjects=1)
    neco = Exam(name='NECO', duration_minutes=60, required_subjects=1)
    
    db.session.add_all([jamb, waec, neco])
    db.session.commit()
    print("[+] JAMB (2hr/4sub), WAEC (1hr/1sub), NECO (1hr/1sub) configured.")
