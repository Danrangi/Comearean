from src.app import create_app, db
from src.app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Clear old user if exists to avoid conflicts
    existing = User.query.filter_by(username='admin').first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        print("Existing admin removed.")

    print("Creating Super Admin...")
    admin = User(
        username='admin',
        email='admin@examarena.com',
        # FIX: Assign to password_hash
        password_hash=generate_password_hash('admin123'), 
        role='super_admin'
    )
    db.session.add(admin)
    db.session.commit()
    print("Super Admin created successfully!")
    print("User: admin")
    print("Pass: admin123")
