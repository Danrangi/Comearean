from flask import Blueprint, render_template, request, redirect, url_for, g, session
from src.app.models import Exam, Subject, Question, db

bp = Blueprint('student', __name__, url_prefix='/exam')

@bp.route('/dashboard')
def dashboard():
    exams = Exam.query.all()
    return render_template('student/dashboard.html', exams=exams)

@bp.route('/setup/<int:exam_id>')
def setup(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    subjects = Subject.query.filter_by(exam_id=exam_id).all()
    return render_template('student/setup.html', exam=exam, subjects=subjects)

@bp.route('/start', methods=['POST'])
def start():
    exam_id = request.form['exam_id']
    selected_subjects = request.form.getlist('subjects')
    exam = Exam.query.get(exam_id)
    
    if len(selected_subjects) != exam.required_subjects:
        return f"Error: You must select exactly {exam.required_subjects} subjects."
    
    # Store in session for the timer logic
    session['current_exam'] = exam.name
    session['duration'] = exam.duration_minutes
    # Logic to fetch questions would follow here
    return render_template('student/war_room.html', exam=exam)
