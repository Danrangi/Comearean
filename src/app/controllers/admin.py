from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from src.app import db
from src.app.models import Exam, Subject, Question, User, Result

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.before_request
def restrict_access():
    # Ensure only admins can access these routes
    if g.user is None or g.user.role not in ['admin', 'super_admin']:
        flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for('auth.login'))

@bp.route('/', methods=['GET', 'POST'])
def index():
    # Handle "Create Subject" form submission
    if request.method == 'POST':
        exam_id = request.form.get('exam_id')
        name = request.form.get('subject_name')
        
        if exam_id and name:
            new_subject = Subject(name=name, exam_id=exam_id)
            db.session.add(new_subject)
            db.session.commit()
            flash(f'Subject "{name}" created successfully.', 'success')
        else:
            flash('Please select an exam and enter a subject name.', 'error')
        return redirect(url_for('admin.index'))

    # Dashboard Data
    exams = Exam.query.all()
    subjects = Subject.query.all()
    return render_template('admin/admin_panel.html', exams=exams, subjects=subjects)

@bp.route('/subject/<int:subject_id>/questions', methods=['GET', 'POST'])
def manage_questions(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'POST':
        # Simple single question add logic
        text = request.form.get('question_text')
        options = [
            request.form.get('option_a'),
            request.form.get('option_b'),
            request.form.get('option_c'),
            request.form.get('option_d')
        ]
        correct = request.form.get('correct_option') # e.g., 'A'
        
        if text and correct:
            # Save options as JSON string or separated fields depending on your model
            # Assuming simple fields based on standard CBT structure:
            q = Question(
                subject_id=subject.id,
                text=text,
                option_a=options[0],
                option_b=options[1],
                option_c=options[2],
                option_d=options[3],
                correct_answer=correct
            )
            db.session.add(q)
            db.session.commit()
            flash('Question added.', 'success')
            
    questions = Question.query.filter_by(subject_id=subject_id).all()
    return render_template('admin/question_bank.html', subject=subject, questions=questions)

# -- The New Delete Feature --
@bp.route('/exam/delete/<int:exam_id>', methods=['POST'])
def delete_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    try:
        # SQLAlchemy cascade should handle children, but we delete explicitly to be safe
        db.session.delete(exam)
        db.session.commit()
        flash(f'Exam "{exam.name}" deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting exam. It may have associated results.', 'error')
        print(e)
    return redirect(url_for('admin.index'))
