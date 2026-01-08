from flask import Blueprint, render_template, request, redirect, url_for, flash, g, Response
from src.app import db
from src.app.models import Exam, Subject, Question, User
import csv
import io

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.before_request
def restrict_to_admin():
    if not g.user or g.user.role not in ['superadmin', 'centeradmin']:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('auth.login'))

@bp.route('/')
def index():
    exams = Exam.query.all()
    all_subjects = Subject.query.order_by(Subject.exam_id, Subject.name).all()
    return render_template('admin/admin_panel.html', exams=exams, subjects=all_subjects)

@bp.route('/questions/<int:subject_id>', methods=['GET', 'POST'])
def manage_questions(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'POST':
        # Check if it is a CSV upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename.endswith('.csv'):
                stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                reader = csv.DictReader(stream)
                for row in reader:
                    q = Question(
                        text=row['question_text'],
                        option_a=row['option_a'],
                        option_b=row['option_b'],
                        option_c=row['option_c'],
                        option_d=row['option_d'],
                        correct_option=row['correct_answer'].upper(),
                        explanation=row.get('explanation', ''),
                        subject_id=subject_id
                    )
                    db.session.add(q)
                db.session.commit()
                flash("CSV Uploaded successfully!", "success")
        
        # Or a single question add
        elif 'question_text' in request.form:
            q = Question(
                text=request.form['question_text'],
                option_a=request.form['option_a'],
                option_b=request.form['option_b'],
                option_c=request.form['option_c'],
                option_d=request.form['option_d'],
                correct_option=request.form['correct_answer'].upper(),
                explanation=request.form.get('explanation', ''),
                subject_id=subject_id
            )
            db.session.add(q)
            db.session.commit()
            flash("Question added!", "success")

    questions = Question.query.filter_by(subject_id=subject_id).all()
    return render_template('admin/questions.html', subject=subject, questions=questions)

@bp.route('/question/edit/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == 'POST':
        question.text = request.form['question_text']
        question.option_a = request.form['option_a']
        question.option_b = request.form['option_b']
        question.option_c = request.form['option_c']
        question.option_d = request.form['option_d']
        question.correct_option = request.form['correct_answer']
        question.explanation = request.form['explanation']
        db.session.commit()
        flash("Question updated!", "success")
        return redirect(url_for('admin.manage_questions', subject_id=question.subject_id))
    return render_template('admin/edit_question.html', question=question)

@bp.route('/question/delete/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    sid = question.subject_id
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted.", "info")
    return redirect(url_for('admin.manage_questions', subject_id=sid))

@bp.route('/download_sample_csv')
def download_sample_csv():
    csv_content = "question_text,option_a,option_b,option_c,option_d,correct_answer,explanation\n"
    return Response(csv_content, mimetype="text/csv", headers={"Content-disposition": "attachment; filename=sample.csv"})
