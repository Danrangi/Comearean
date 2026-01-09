from flask import Blueprint, render_template, redirect, url_for, g, request, session, flash
from src.app.models import Exam, Subject, Question, Result, db
from .auth import login_required
import json

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
    selected_ids = request.form.getlist('subjects')
    exam = Exam.query.get(exam_id)
    
    g.user.is_writing = True
    db.session.commit()

    exam_data = {}
    for sid in selected_ids:
        sub = Subject.query.get(sid)
        # Limit questions: JAMB 40/sub, WAEC/NECO 60/sub
        qs = Question.query.filter_by(subject_id=sid).limit(40 if exam.name == 'JAMB' else 60).all()
        sub_items = [{'q': q, 'opts': [{'key':'A','text':q.option_a},{'key':'B','text':q.option_b},{'key':'C','text':q.option_c},{'key':'D','text':q.option_d}]} for q in qs]
        exam_data[sub.name] = sub_items

    return render_template('student/war_room.html', exam_data=exam_data, exam=exam, mode=exam.name)

@bp.route('/submit-exam', methods=['POST'])
@login_required
def submit_exam():
    total_score = 0
    total_q = 0
    
    # Process answers from request.form
    for key, value in request.form.items():
        if key.startswith('q_'):
            q_id = int(key.split('_')[1])
            question = Question.query.get(q_id)
            if question and question.correct_option == value:
                total_score += 1
            total_q += 1

    res = Result(user_id=g.user.id, center_id=g.user.center_id, 
                 exam_name=request.form.get('exam_name', 'Mock'),
                 score=float(total_score), total_questions=total_q)
    
    g.user.is_writing = False
    db.session.add(res)
    db.session.commit()
    
    flash(f"Exam Submitted! Your score: {total_score}/{total_q}", "success")
    return redirect(url_for('main.dashboard'))

@bp.route('/ai-preview')
def ai_preview():
    return "<h1>AI Review</h1><p>Offline AI Analysis engine under construction.</p>"
