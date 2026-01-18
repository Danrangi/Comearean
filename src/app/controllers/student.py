from flask import Blueprint, render_template, session, g, request, redirect, url_for, flash, make_response
from src.app.models import Result, User, Exam, Subject, Question
from src.app import db
from datetime import datetime
import weasyprint

bp = Blueprint('student', __name__, url_prefix='/student')

@bp.before_request
def check_student_auth():
    if g.user is None:
        return redirect(url_for('auth.login'))

@bp.route('/dashboard')
def dashboard():
    exams = Exam.query.all()
    # Get previous results for this student
    history = Result.query.filter_by(user_id=g.user.id).order_by(Result.date_taken.desc()).all()
    return render_template('student/dashboard.html', exams=exams, history=history)

@bp.route('/take_exam/<int:exam_id>', methods=['GET', 'POST'])
def take_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    
    # 1. Fetch all subjects and questions for this exam
    subjects = Subject.query.filter_by(exam_id=exam_id).all()
    if not subjects:
        flash("This exam has no subjects yet.", "error")
        return redirect(url_for('student.dashboard'))

    # 2. Handle Exam Submission (Grading)
    if request.method == 'POST':
        total_score = 0
        total_questions = 0
        
        # Loop through submitted answers
        for key, value in request.form.items():
            if key.startswith('q_'):
                q_id = int(key.split('_')[1])
                question = Question.query.get(q_id)
                if question:
                    total_questions += 1
                    # Compare selected option (value) with correct answer
                    if value == question.correct_answer:
                        total_score += 1
        
        # 3. Save Result
        result = Result(
            user_id=g.user.id,
            exam_id=exam.id,
            score=total_score,
            total_possible=total_questions,
            date_taken=datetime.now()
        )
        db.session.add(result)
        db.session.commit()
        
        flash(f"Exam Submitted! You scored {total_score}/{total_questions}", "success")
        return redirect(url_for('student.dashboard'))

    # 3. Render Exam Interface (GET request)
    return render_template('student/war_room.html', exam=exam, subjects=subjects)

@bp.route('/result/download/<int:result_id>')
def download_result_slip(result_id):
    result = Result.query.get_or_404(result_id)
    # Ensure student owns this result
    if result.user_id != g.user.id:
        flash("Unauthorized access to result.", "error")
        return redirect(url_for('student.dashboard'))

    student = User.query.get(result.user_id)
    exam = Exam.query.get(result.exam_id)
    
    html = render_template('pdf/result_slip.html', result=result, student=student, exam=exam)
    pdf = weasyprint.HTML(string=html).write_pdf()
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Result_Slip_{student.username}.pdf'
    return response
