from flask import Blueprint, render_template, request, redirect, url_for, flash, g, Response, current_app, send_file
from src.app import db
from src.app.models import Exam, Subject, Question, User, Result, Center
from werkzeug.utils import secure_filename
from src.app.controllers.auth import login_required

import csv, io
import os
import uuid

bp = Blueprint('admin', __name__, url_prefix='/admin')

def _save_question_image(file_storage):
    if not file_storage or not getattr(file_storage, "filename", ""):
        return None

    filename = secure_filename(file_storage.filename)
    if not filename:
        return None

    allowed = {".png", ".jpg", ".jpeg", ".webp"}
    ext = os.path.splitext(filename.lower())[1]
    if ext not in allowed:
        return None

    upload_dir = os.path.join(current_app.instance_path, "uploads", "questions")
    os.makedirs(upload_dir, exist_ok=True)

    unique = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(upload_dir, unique)
    file_storage.save(save_path)

    return os.path.join("uploads", "questions", unique).replace("\\", "/")

@bp.before_request
def restrict_access():
    if not g.user:
        return redirect(url_for('auth.login'))
    if g.user.role not in ['superadmin', 'centeradmin']:
        return redirect(url_for('main.dashboard'))

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and g.user.role == 'superadmin':
        exam_id = request.form.get('exam_id')
        name = request.form.get('subject_name')
        if exam_id and name:
            limit_raw = request.form.get('question_limit', '').strip()
            try:
                qlimit = int(limit_raw) if limit_raw else 50
            except Exception:
                qlimit = 50
            if qlimit < 1:
                qlimit = 1
            new_sub = Subject(name=name, exam_id=int(exam_id), question_limit=qlimit)
            db.session.add(new_sub)
            db.session.commit()
            flash(f"Subject '{name}' created.", "success")
        return redirect(url_for('admin.index'))

    if g.user.role == 'centeradmin':
        students = User.query.filter_by(center_id=g.user.center_id, role='student').all()
        return render_template('admin/center_dashboard.html', students=students)

    exams = Exam.query.all()
    subjects = Subject.query.all()
    return render_template('admin/question_bank.html', exams=exams, subjects=subjects)

# --- Student Management (Center Admin) ---

@bp.route('/student/add', methods=['POST'])
def add_student():
    if g.user.role != 'centeradmin':
        return "Access Denied", 403

    username = (request.form.get('username') or "").strip()
    password = (request.form.get('password') or "").strip()

    if not username or not password:
        flash("Username and password required.", "danger")
        return redirect(url_for('admin.index'))

    if User.query.filter_by(username=username).first():
        flash(f"User '{username}' already exists.", "danger")
        return redirect(url_for('admin.index'))

    student = User(username=username, role='student', center_id=g.user.center_id)
    student.set_password(password)
    db.session.add(student)
    db.session.commit()
    flash(f"Student '{username}' created.", "success")
    return redirect(url_for('admin.index'))

@bp.route('/student/edit/<int:id>', methods=['POST'])
def edit_student(id):
    student = User.query.get_or_404(id)
    if g.user.role != 'centeradmin' or student.center_id != g.user.center_id:
        return "Unauthorized", 403

    new_username = (request.form.get('username') or "").strip()
    new_password = (request.form.get('password') or "").strip()

    if not new_username:
        flash("Username is required.", "danger")
        return redirect(url_for('admin.index'))

    existing = User.query.filter_by(username=new_username).first()
    if existing and existing.id != student.id:
        flash(f"Username '{new_username}' is already taken.", "danger")
        return redirect(url_for('admin.index'))

    student.username = new_username
    if new_password:
        student.set_password(new_password)

    db.session.commit()
    flash("Student updated.", "success")
    return redirect(url_for('admin.index'))

@bp.route('/student/delete/<int:id>', methods=['POST'])
def delete_student(id):
    student = User.query.get_or_404(id)
    if g.user.role != 'centeradmin' or student.center_id != g.user.center_id:
        return "Unauthorized", 403

    Result.query.filter_by(user_id=id).delete()
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted.", "info")
    return redirect(url_for('admin.index'))

@bp.route('/student/reset/<int:id>')
def reset_student(id):
    student = User.query.get_or_404(id)
    if g.user.role != 'centeradmin' or student.center_id != g.user.center_id:
        return "Unauthorized", 403

    student.is_writing = False
    db.session.commit()
    flash(f"Session reset for {student.username}.", "info")
    return redirect(url_for('admin.index'))

# --- Question & Subject Management (Super Admin) ---

@bp.route('/questions/<int:subject_id>', methods=['GET', 'POST'])
def manage_questions(subject_id):
    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST' and g.user.role == 'superadmin':
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            reader = csv.DictReader(stream)
            for row in reader:
                q = Question(
                    text=row.get('question_text', '').strip(),
                    option_a=row.get('option_a', '').strip(),
                    option_b=row.get('option_b', '').strip(),
                    option_c=row.get('option_c', '').strip(),
                    option_d=row.get('option_d', '').strip(),
                    correct_option=(row.get('correct_answer', '').strip().upper()[:1]),
                    explanation=row.get('explanation', '').strip(),
                    subject_id=subject_id
                )
                db.session.add(q)
            db.session.commit()
            flash("CSV Imported.", "success")
        else:
            q = Question(
                text=request.form.get('question_text', '').strip(),
                option_a=request.form.get('option_a', '').strip(),
                option_b=request.form.get('option_b', '').strip(),
                option_c=request.form.get('option_c', '').strip(),
                option_d=request.form.get('option_d', '').strip(),
                correct_option=(request.form.get('correct_answer', '').strip().upper()[:1]),
                explanation=request.form.get('explanation', '').strip(),
                subject_id=subject_id
            )
            db.session.add(q)
            db.session.commit()
            flash("Question added.", "success")

    questions = Question.query.filter_by(subject_id=subject_id).all()
    return render_template('admin/questions.html', subject=subject, questions=questions)

@bp.route('/question/edit/<int:id>', methods=['GET', 'POST'])
def edit_question(id):
    q = Question.query.get_or_404(id)
    if request.method == 'POST' and g.user.role == 'superadmin':
        q.text = request.form.get('question_text', '').strip()
        q.option_a = request.form.get('option_a', '').strip()
        q.option_b = request.form.get('option_b', '').strip()
        q.option_c = request.form.get('option_c', '').strip()
        q.option_d = request.form.get('option_d', '').strip()
        q.correct_option = (request.form.get('correct_answer', '').strip().upper()[:1])
        q.explanation = request.form.get('explanation', '').strip()

        if request.form.get('remove_image') == '1':
            q.image_path = None
        new_img = _save_question_image(request.files.get('question_image'))
        if new_img:
            q.image_path = new_img

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

@bp.route('/subject/edit/<int:id>', methods=['GET', 'POST'])
def edit_subject(id):
    sub = Subject.query.get_or_404(id)
    if request.method == 'POST':
        sub.name = request.form.get('name', '').strip()
        limit_raw = request.form.get('question_limit', '').strip()
        try:
            qlimit = int(limit_raw) if limit_raw else (sub.question_limit or 50)
        except Exception:
            qlimit = sub.question_limit or 50
        if qlimit < 1:
            qlimit = 1
        sub.question_limit = qlimit
        db.session.commit()
        flash("Subject updated.", "success")
        return redirect(url_for('admin.index'))
    return render_template('admin/edit_subject.html', subject=sub)

@bp.route('/subject/delete/<int:id>', methods=['POST'])
def delete_subject(id):
    if g.user.role != 'superadmin':
        return "Access Denied", 403
    sub = Subject.query.get_or_404(id)
    Question.query.filter_by(subject_id=id).delete()
    db.session.delete(sub)
    db.session.commit()
    flash(f"Subject '{sub.name}' deleted.", "info")
    return redirect(url_for('admin.index'))

# --- Center Admin: Student Results page ---
@bp.route('/student/results/<int:student_id>')
def center_student_results(student_id):
    if g.user.role not in ['centeradmin', 'superadmin']:
        return "Unauthorized", 403

    student = User.query.get_or_404(student_id)
    if g.user.role == 'centeradmin' and student.center_id != g.user.center_id:
        return "Unauthorized", 403

    results = Result.query.filter_by(user_id=student.id).order_by(Result.created_at.desc()).all()
    return render_template('admin/student_results.html', student=student, results=results)

@bp.route('/student/<int:student_id>/result/<int:result_id>/pdf')
def download_student_result_pdf(student_id, result_id):
    if g.user.role not in ['centeradmin', 'superadmin']:
        return "Unauthorized", 403

    student = User.query.get_or_404(student_id)
    if g.user.role == 'centeradmin' and student.center_id != g.user.center_id:
        return "Unauthorized", 403

    res = Result.query.get_or_404(result_id)
    if res.user_id != student.id:
        return "Unauthorized", 403

    # center name best-effort
    center_name = "N/A"
    try:
        if res.center_id:
            c = Center.query.get(res.center_id)
            if c and getattr(c, "name", ""):
                center_name = c.name
    except Exception:
        pass

    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, h - 60, "EXAM ARENA - RESULT SLIP")

    c.setFont("Helvetica", 11)
    y = h - 100
    c.drawString(50, y, f"Student: {student.username}"); y -= 18
    c.drawString(50, y, f"Center: {center_name}"); y -= 18
    c.drawString(50, y, f"Exam: {res.exam_name or 'N/A'}"); y -= 18
    c.drawString(50, y, f"Subject: {res.subject_name or 'N/A'}"); y -= 18
    c.drawString(50, y, f"Score: {int(res.score or 0)} / {int(res.total_questions or 0)}"); y -= 18
    c.drawString(50, y, f"Date: {res.created_at}"); y -= 18

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, 40, "Generated by Exam Arena (Offline CBT)")

    c.showPage()
    c.save()
    buf.seek(0)

    filename = f"ExamArena_Result_{student.username}_{result_id}.pdf"
    return send_file(buf, as_attachment=True, download_name=filename, mimetype="application/pdf")

@bp.route('/download_sample_csv')
def download_sample_csv():
    csv_text = "question_text,option_a,option_b,option_c,option_d,correct_answer,explanation\n"
    return Response(csv_text, mimetype="text/csv", headers={"Content-disposition": "attachment; filename=sample.csv"})
