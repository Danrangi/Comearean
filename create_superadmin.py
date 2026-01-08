from src.app import db, create_app
from src.app.models import User

app = create_app()
with app.app_context():
    if not User.query.filter_by(username='admin').first():
        user = User(username='admin', role='superadmin')
        user.set_password('master123')
        db.session.add(user)
        db.session.commit()
        print("Super Admin created! User: admin, Pass: master123")
    else:
        print("Super Admin already exists.")
