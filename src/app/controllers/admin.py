from flask import Blueprint, render_template, request, redirect, url_for, flash, g, Response
from src.app import db
from src.app.models import Exam, Subject, Question, User, Result
import csv, io

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.before_request
def restrict_access():
    if not g.user:
        return redirect(url_for('auth.login'))
    # Allow Super Admin to manage questions, Allow Center Admin to manage students
    if g.user.role not in ['superadmin', 'centeradmin']:
        return redirect(url_for('main.dashboard'))

@bp.route('/')
def index():
    if g.user.role == 'centeradmin':
        students = User.query.filter_by(center_id=g.user.center_id, role='student').all()
        results = Result.query.filter_by(center_id=g.user.center_id).all()
        return render_template('admin/center_dashboard.html', students=students, results=results)
    
    # Super Admin View (Question Bank)
    exams = Exam.query.all()
    subjects = Subject.query.all()
    return render_template('admin/question_bank.html', exams=exams, subjects=subjects)

@bp.route('/student/add', methods=['POST'])
def add_student():
    if g.user.role != 'centeradmin':
        return "Access Denied", 403
        
    username = request.form.get('username')
    password = request.form.get('password')
    
    if User.query.filter_by(username=username).first():
        flash("Student ID already exists!", "danger")
    else:
        new_student = User(username=username, role='student', center_id=g.user.center_id)
        new_student.set_password(password)
        db.session.add(new_student)
        db.session.commit()
        flash(f"Student {username} created successfully.", "success")
    return redirect(url_for('admin.index'))

@bp.route('/questions/<int:subject_id>', methods=['GET', 'POST'])
def manage_questions(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            reader = csv.DictReader(stream)
            for row in reader:
                q = Question(text=row['question_text'], option_a=row['option_a'], 
                             option_b=row['option_b'], option_c=row['option_c'], 
                             option_d=row['option_d'], correct_option=row['correct_answer'].upper(),
                             explanation=row.get('explanation', ''), subject_id=subject_id)
                db.session.add(q)
            db.session.commit()
            flash("CSV Uploaded!", "success")
        else:
            q = Question(text=request.form['question_text'], option_a=request.form['option_a'],
                         option_b=request.form['option_b'], option_c=request.form['option_c'],
                         option_d=request.form['option_d'], correct_option=request.form['correct_answer'],
                         explanation=request.form['explanation'], subject_id=subject_id)
            db.session.add(q)
            db.session.commit()
            flash("Question added!", "success")
    questions = Question.query.filter_by(subject_id=subject_id).all()
    return render_template('admin/questions.html', subject=subject, questions=questions)

@bp.route('/download_sample_csv')
def download_sample_csv():
    csv_content = "question_text,option_a,option_b,option_c,option_d,correct_answer,explanation\n"
    return Response(csv_content, mimetype="text/csv", headers={"Content-disposition": "attachment; filename=sample.csv"})

@bp.route('/question/edit/<int:id>', methods=['GET', 'POST'])
def edit_question(id):
    q = Question.query.get_or_404(id)
    if request.method == 'POST':
        q.text = request.form['question_text']
        q.option_a = request.form['option_a']
        q.option_b = request.form['option_b']
        q.option_c = request.form['option_c']
        q.option_d = request.form['option_d']
        q.correct_option = request.form['correct_answer']
        q.explanation = request.form['explanation']
        db.session.commit()
        return redirect(url_for('admin.manage_questions', subject_id=q.subject_id))
    return render_template('admin/edit_question.html', question=q)

@bp.route('/question/delete/<int:id>', methods=['POST'])
def delete_question(id):
    q = Question.query.get_or_404(id)
    sid = q.subject_id
    db.session.delete(q)
    db.session.commit()
    return redirect(url_for('admin.manage_questions', subject_id=sid))
