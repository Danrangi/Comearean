from flask import Blueprint, render_template, request, redirect, url_for, g, flash
from src.app.models import Center, User, Exam, Subject, Question, db
from src.app.utils.license import get_hwid
from .auth import login_required

bp = Blueprint('super_admin', __name__, url_prefix='/super-admin')

@bp.before_request
@login_required
def restrict_to_local_server():
    if g.user.role != 'superadmin': return "Access Denied", 403

@bp.route('/')
def index():
    centers = Center.query.all()
    exams = Exam.query.all()
    hwid = get_hwid()
    return render_template('admin/super_dashboard.html', centers=centers, exams=exams, hwid=hwid)

@bp.route('/exam/add', methods=['POST'])
def add_exam():
    name = request.form.get('name')
    duration = int(request.form.get('duration'))
    req_sub = int(request.form.get('required_subjects'))
    if Exam.query.filter_by(name=name).first(): flash(f"Exam '{name}' already exists.", "warning")
    else:
        new_exam = Exam(name=name, duration_minutes=duration, required_subjects=req_sub)
        db.session.add(new_exam)
        db.session.commit()
        flash(f"Exam category '{name}' created successfully.", "success")
    return redirect(url_for('super_admin.index'))

@bp.route('/exam/delete/<int:id>', methods=['POST'])
def delete_exam(id):
    exam = Exam.query.get_or_404(id)
    subjects = Subject.query.filter_by(exam_id=id).all()
    for sub in subjects:
        Question.query.filter_by(subject_id=sub.id).delete()
        db.session.delete(sub)
    db.session.delete(exam)
    db.session.commit()
    flash(f"Exam '{exam.name}' and all associated data deleted.", "success")
    return redirect(url_for('super_admin.index'))

@bp.route('/centers/add', methods=['POST'])
def add_center():
    name = request.form.get('name')
    loc = request.form.get('location')
    u = request.form.get('admin_username')
    p = request.form.get('admin_password')
    if User.query.filter_by(username=u).first():
        flash("Username already taken.", "danger")
        return redirect(url_for('super_admin.index'))
    new_center = Center(name=name, location=loc)
    db.session.add(new_center)
    db.session.commit()
    admin = User(username=u, role='centeradmin', center_id=new_center.id)
    admin.set_password(p)
    db.session.add(admin)
    db.session.commit()
    flash(f"Center '{name}' and admin '{u}' created.", "success")
    return redirect(url_for('super_admin.index'))
