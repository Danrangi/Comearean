from flask import Blueprint, render_template, request, redirect, url_for, flash, g, Response
from src.app import db
from src.app.models import Exam, Subject, Question
import csv
import io

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        exam_id = request.form.get('exam_id')
        name = request.form.get('subject_name')
        if exam_id and name:
            new_sub = Subject(name=name, exam_id=exam_id)
            db.session.add(new_sub)
            db.session.commit()
            flash(f"Subject '{name}' created!", "success")
            return redirect(url_for('admin.index'))

    exams = Exam.query.all()
    subjects = Subject.query.all()
    return render_template('admin/admin_panel.html', exams=exams, subjects=subjects)

@bp.route('/questions/<int:subject_id>', methods=['GET', 'POST'])
def manage_questions(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
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
                flash("CSV Uploaded!", "success")
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
        return redirect(url_for('admin.manage_questions', subject_id=question.subject_id))
    return render_template('admin/edit_question.html', question=question)

@bp.route('/question/delete/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    sid = question.subject_id
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('admin.manage_questions', subject_id=sid))

@bp.route('/download_sample_csv')
def download_sample_csv():
    csv_content = "question_text,option_a,option_b,option_c,option_d,correct_answer,explanation\n"
    return Response(csv_content, mimetype="text/csv", headers={"Content-disposition": "attachment; filename=sample.csv"})
