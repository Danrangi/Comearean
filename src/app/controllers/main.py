from flask import Blueprint, render_template, redirect, url_for, g, request, session, flash
from src.app.models import Exam, Subject, Question, Result, db
from .auth import login_required

bp = Blueprint('main', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    exams = Exam.query.all()
    return render_template('student/dashboard.html', exams=exams)

@bp.route('/setup/<int:exam_id>')
@login_required
def exam_setup(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    subjects = Subject.query.filter_by(exam_id=exam.id).all()
    return render_template('student/setup.html', exam=exam, subjects=subjects)

@bp.route('/take-exam', methods=['POST'])
@login_required
def take_exam():
    exam_id = request.form.get('exam_id')
    selected_subject_ids = request.form.getlist('subjects')
    exam = Exam.query.get(exam_id)

    if len(selected_subject_ids) != exam.required_subjects:
        flash(f"Please select exactly {exam.required_subjects} subjects for {exam.name}.", "warning")
        return redirect(url_for('main.exam_setup', exam_id=exam_id))

    # Load questions for all selected subjects
    exam_data = {}
    for sid in selected_subject_ids:
        sub = Subject.query.get(sid)
        questions = Question.query.filter_by(subject_id=sid).limit(40 if exam.name == 'JAMB' else 60).all()
        # Prepare for template: list of items with options split
        sub_items = []
        for q in questions:
            opts = [
                {'key': 'A', 'text': q.option_a},
                {'key': 'B', 'text': q.option_b},
                {'key': 'C', 'text': q.option_c},
                {'key': 'D', 'text': q.option_d}
            ]
            sub_items.append({'q': q, 'opts': opts})
        exam_data[sub.name] = sub_items

    return render_template('student/war_room.html', 
                           exam_data=exam_data, 
                           exam=exam, 
                           mode=exam.name)

@bp.route('/ai-preview')
@login_required
def ai_preview():
    return "<h1>AI Performance Analysis</h1><p>Under Construction: Offline AI engine is being integrated.</p>"

@bp.route('/about')
def about():
    return "ExamArena v1.0 - Suleja Digital Innovation Hub"
