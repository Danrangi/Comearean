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
    selected_ids = request.form.getlist('subjects')
    exam = Exam.query.get(exam_id)
    
    g.user.is_writing = True
    db.session.commit()

    exam_data = {}
    for sid in selected_ids:
        sub = Subject.query.get(sid)
        qs = Question.query.filter_by(subject_id=sid).all()
        sub_items = [{'q': q, 'opts': [{'key':'A','text':q.option_a},{'key':'B','text':q.option_b},{'key':'C','text':q.option_c},{'key':'D','text':q.option_d}]} for q in qs]
        exam_data[sub.name] = sub_items

    return render_template('student/war_room.html', exam_data=exam_data, exam=exam)

@bp.route('/submit-exam', methods=['POST'])
@login_required
def submit_exam():
    score = 0
    total = 0
    results_list = []
    
    for key, value in request.form.items():
        if key.startswith('q_'):
            total += 1
            q_id = int(key.split('_')[1])
            q = Question.query.get(q_id)
            
            is_correct = q.correct_option == value
            if is_correct:
                score += 1
                
            results_list.append({
                'question_text': q.text,
                'user_answer': value,
                'correct_answer': q.correct_option,
                'is_correct': is_correct,
                'explanation': q.explanation,
                'options': {'A': q.option_a, 'B': q.option_b, 'C': q.option_c, 'D': q.option_d}
            })

    # Save summary to DB
    new_result = Result(user_id=g.user.id, center_id=g.user.center_id, 
                        exam_name=request.form.get('exam_name'), 
                        score=float(score), total_questions=total)
    
    g.user.is_writing = False
    db.session.add(new_result)
    db.session.commit()

    # Pass detailed data to the template
    results_data = {
        'score': score,
        'total_questions': total,
        'subject_name': request.form.get('exam_name'),
        'results_list': results_list
    }
    
    return render_template('student/results.html', results=results_data)

@bp.route('/ai-preview')
def ai_preview():
    return render_template('student/under_construction.html', feature="AI Performance Analysis")
