from datetime import datetime
from src.app import db
from werkzeug.security import generate_password_hash, check_password_hash

class Center(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    users = db.relationship('User', backref='center', lazy=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='student') # superadmin, centeradmin, student
    center_id = db.Column(db.Integer, db.ForeignKey('center.id'), nullable=True)
    
    # Session tracking
    is_writing = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    required_subjects = db.Column(db.Integer, default=1)
    subjects = db.relationship('Subject', backref='exam', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'))
    questions = db.relationship('Question', backref='subject', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200))
    option_b = db.Column(db.String(200))
    option_c = db.Column(db.String(200))
    option_d = db.Column(db.String(200))
    correct_option = db.Column(db.String(1))
    explanation = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    center_id = db.Column(db.Integer, db.ForeignKey('center.id'))
    exam_name = db.Column(db.String(50))
    score = db.Column(db.Float)
    total_questions = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- THIS LINE FIXES THE ERROR ---
    # It links the result back to the user so we can get the username
    user = db.relationship('User', backref=db.backref('results', lazy=True))
