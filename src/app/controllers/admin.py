from flask import Blueprint, render_template, request, redirect, url_for, flash, g, Response, current_app, send_file
from src.app import db
from src.app.models import Exam, Subject, Question, User, Result
from werkzeug.utils import secure_filename
import csv, io
import os
import uuid

bp = Blueprint('admin', __name__, url_prefix='/admin')

def _save_question_image(file_storage):
    """Save uploaded image under instance/uploads/questions and return relative path or None."""
    if not file_storage or not getattr(file_storage, "filename", ""):
        return None

    filename = secure_filename(file_storage.filename)
    if not filename:
        return None

    # Basic extension allowlist (diagrams/photos)
    allowed = {".png", ".jpg", ".jpeg", ".webp"}
    ext = os.path.splitext(filename.lower())[1]
    if ext not in allowed:
        return None

    # Ensure folder exists
    upload_dir = os.path.join(current_app.instance_path, "uploads", "questions")
    os.makedirs(upload_dir, exist_ok=True)

    # Unique name to avoid collisions
    unique = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(upload_dir, unique)
    file_storage.save(save_path)

    # Store relative path (served via /uploads/<path>)
    return os.path.join("uploads", "questions", unique).replace("\\", "/")


@bp.before_request
def restrict_access():
    if not g.user:
        return redirect(url_for('auth.login'))
    if g.user.role not in ['superadmin', 'centeradmin']:
        return redirect(url_for('main.dashboard'))

@bp.route('/', methods=['GET', 'POST'])
def index():
    # POST: Subject Creation (Super Admin)
    if request.method == 'POST' and g.user.role == 'superadmin':
        exam_id = request.form.get('exam_id')
        name = request.form.get('subject_name')
        if exam_id and name:
            limit_raw = (request.form.get('question_limit') or '').strip()
            try:
                qlimit = int(limit_raw) if limit_raw else 50
            except Exception:
                qlimit = 50
            if qlimit < 1:
                qlimit = 1
            new_sub = Subject(name=name, exam_id=exam_id, question_limit=qlimit)
            db.session.add(new_sub)
            db.session.commit()
            flash(f"Subject '{name}' created successfully.", "success")
        return redirect(url_for('admin.index'))

    # GET: View Determination
    if g.user.role == 'centeradmin':
        students = User.query.filter_by(center_id=g.user.center_id, role='student').all()
        return render_template('admin/center_dashboard.html', students=students)
    
    # Super Admin falls through to here
    exams = Exam.query.all()
    subjects = Subject.query.all()
    return render_template('admin/question_bank.html', exams=exams, subjects=subjects)

# --- Student Management (Center Admin) ---

@bp.route('/student/add', methods=['POST'])
def add_student():
    if g.user.role != 'centeradmin': return "Access Denied", 403
    username = request.form.get('username')
    password = request.form.get('password')
    
    if User.query.filter_by(username=username).first():
        flash(f"User '{username}' already exists.", "danger")
    else:
        student = User(username=username, role='student', center_id=g.user.center_id)
        student.set_password(password)
        db.session.add(student)
        db.session.commit()
        flash(f"Student '{username}' registered successfully.", "success")
    return redirect(url_for('admin.index'))

@bp.route('/student/edit/<int:id>', methods=['POST'])
def edit_student(id):
    student = User.query.get_or_404(id)
    if g.user.role != 'centeradmin' or student.center_id != g.user.center_id:
        return "Unauthorized", 403
    
    new_username = request.form.get('username')
    new_password = request.form.get('password')
    
    existing = User.query.filter_by(username=new_username).first()
    if existing and existing.id != student.id:
        flash(f"Username '{new_username}' is already taken.", "danger")
    else:
        student.username = new_username
        if new_password:
            student.set_password(new_password)
        db.session.commit()
        flash("Student record updated.", "success")
        
    return redirect(url_for('admin.index'))

@bp.route('/student/delete/<int:id>', methods=['POST'])
def delete_student(id):
    student = User.query.get_or_404(id)
    if g.user.role != 'centeradmin' or student.center_id != g.user.center_id:
        return "Unauthorized", 403
    
    # Clean up results first
    Result.query.filter_by(user_id=id).delete()
    db.session.delete(student)
    db.session.commit()
    flash("Student account deleted.", "info")
    return redirect(url_for('admin.index'))

@bp.route('/student/reset/<int:id>')
def reset_student(id):
    student = User.query.get_or_404(id)
    student.is_writing = False
    db.session.commit()
    flash(f"Exam session reset for {student.username}", "info")
    return redirect(url_for('admin.index'))

# --- Question & Subject Management (Super Admin) ---

@bp.route('/questions/<int:subject_id>', methods=['GET', 'POST'])
def manage_questions(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST' and g.user.role == 'superadmin':
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
            flash("CSV Imported.", "success")
        else:
            q = Question(text=request.form['question_text'], option_a=request.form['option_a'],
                         option_b=request.form['option_b'], option_c=request.form['option_c'],
                         option_d=request.form['option_d'], correct_option=request.form['correct_answer'],
                         explanation=request.form['explanation'], subject_id=subject_id)
            db.session.add(q)
            db.session.commit()
            flash("Question added manually.", "success")
    questions = Question.query.filter_by(subject_id=subject_id).all()
    return render_template('admin/questions.html', subject=subject, questions=questions)

@bp.route('/question/edit/<int:id>', methods=['GET', 'POST'])
def edit_question(id):
    q = Question.query.get_or_404(id)
    if request.method == 'POST' and g.user.role == 'superadmin':
        q.text = request.form['question_text']
        q.option_a = request.form['option_a']
        q.option_b = request.form['option_b']
        q.option_c = request.form['option_c']
        q.option_d = request.form['option_d']
        q.correct_option = request.form['correct_answer']
        q.explanation = request.form['explanation']
        # Image replace/remove
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
        sub.name = request.form['name']
        limit_raw = (request.form.get('question_limit') or '').strip()
        try:
            qlimit = int(limit_raw) if limit_raw else (sub.question_limit or 50)
        except Exception:
            qlimit = sub.question_limit or 50
        if qlimit < 1:
            qlimit = 1
        sub.question_limit = qlimit
        db.session.commit()
        flash("Subject name updated.", "success")
        return redirect(url_for('admin.index'))
    return render_template('admin/edit_subject.html', subject=sub)

@bp.route('/subject/delete/<int:id>', methods=['POST'])
def delete_subject(id):
    if g.user.role != 'superadmin': return "Access Denied", 403
    sub = Subject.query.get_or_404(id)
    Question.query.filter_by(subject_id=id).delete()
    db.session.delete(sub)
    db.session.commit()
    flash(f"Subject '{sub.name}' deleted.", "info")
    return redirect(url_for('admin.index'))

@bp.route('/student/<int:student_id>/results')
def center_student_results(student_id):
    # Center admin can only view their own center students
    if g.user.role not in ['centeradmin', 'superadmin']:
        return "Unauthorized", 403

    student = User.query.get_or_404(student_id)

    if g.user.role == 'centeradmin' and student.center_id != g.user.center_id:
        return "Unauthorized", 403

    # Latest first
    results = Result.query.filter_by(user_id=student.id).order_by(Result.created_at.desc()).all()
    return render_template('admin/student_results.html', student=student, results=results)


@bp.route('/student/<int:student_id>/results/<int:result_id>/download')
def download_student_result_pdf(student_id, result_id):
    if g.user.role not in ['centeradmin', 'superadmin']:
        return "Unauthorized", 403

    student = User.query.get_or_404(student_id)

    if g.user.role == 'centeradmin' and student.center_id != g.user.center_id:
        return "Unauthorized", 403

    res = Result.query.get_or_404(result_id)
    if res.user_id != student.id:
        return "Unauthorized", 403

    # Build a small PDF slip (works even if you don't have an existing PDF util)
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, h - 60, "EXAM ARENA - RESULT SLIP")

    # Basic info
    c.setFont("Helvetica", 11)
    y = h - 100
    c.drawString(50, y, f"Student: {student.username}")
    y -= 18
    c.drawString(50, y, f"Role: {student.role}")
    y -= 18

    # Center info (best effort)
    center_name = getattr(g.user, "center_id", None)
    if hasattr(res, "center_id") and res.center_id:
        center_name = res.center_id
    c.drawString(50, y, f"Center: {center_name if center_name else 'N/A'}")
    y -= 18

    # Exam info (best effort fields)
    exam_name = getattr(res, "exam_name", None) or getattr(res, "exam", None) or "N/A"
    subject_name = getattr(res, "subject_name", None) or getattr(res, "subject", None) or "N/A"
    c.drawString(50, y, f"Exam: {exam_name}")
    y -= 18
    c.drawString(50, y, f"Subject: {subject_name}")
    y -= 18

    # Scores (best effort)
    score = getattr(res, "score", None)
    total = getattr(res, "total", None) or getattr(res, "total_questions", None)

    c.drawString(50, y, f"Score: {score if score is not None else 'N/A'}")
    y -= 18
    c.drawString(50, y, f"Total Questions: {total if total is not None else 'N/A'}")
    y -= 18

    # Timestamp
    created = getattr(res, "created_at", None)
    c.drawString(50, y, f"Date: {created if created else 'N/A'}")

    # Footer
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, 40, "Generated by Exam Arena (Offline CBT)")

    c.showPage()
    c.save()
    buf.seek(0)

    filename = f"ExamArena_Result_{student.username}_{result_id}.pdf"
    return send_file(buf, as_attachment=True, download_name=filename, mimetype="application/pdf")


@bp.route('/download_sample_csv')
def download_sample_csv():
    csv = "question_text,option_a,option_b,option_c,option_d,correct_answer,explanation\n"
    return Response(csv, mimetype="text/csv", headers={"Content-disposition": "attachment; filename=sample.csv"})
