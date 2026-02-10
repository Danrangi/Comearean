from datetime import datetime
from src.app import db

class Center(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True, default="")

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
    question_limit = db.Column(db.Integer, default=50)  # per-subject question count
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
    image_path = db.Column(db.String(300))  # uploads/questions/....
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(30), default="student")
    center_id = db.Column(db.Integer, db.ForeignKey('center.id'), nullable=True)
    is_writing = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, raw):
        # keep your existing hashing if you already had it elsewhere
        # (fallback: store as-is only if hashing is not wired)
        try:
            from werkzeug.security import generate_password_hash
            self.password_hash = generate_password_hash(raw)
        except Exception:
            self.password_hash = raw

    def check_password(self, raw):
        try:
            from werkzeug.security import check_password_hash
            return check_password_hash(self.password_hash, raw)
        except Exception:
            return self.password_hash == raw

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # ownership
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    center_id = db.Column(db.Integer, db.ForeignKey('center.id'))

    # grouping
    attempt_id = db.Column(db.String(64), nullable=True, index=True)   # same attempt groups subjects
    exam_id = db.Column(db.Integer, nullable=True)
    subject_id = db.Column(db.Integer, nullable=True)

    # display fields
    exam_name = db.Column(db.String(80), nullable=True)
    subject_name = db.Column(db.String(80), nullable=True)

    # scoring
    score = db.Column(db.Float, default=0)
    total_questions = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('results', lazy=True))
