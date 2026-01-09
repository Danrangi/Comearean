from flask import Blueprint, render_template, request, redirect, url_for, g, flash
from src.app.models import Center, User, Exam, Subject, db
from src.app.utils.license import get_hwid
from .auth import login_required

bp = Blueprint('super_admin', __name__, url_prefix='/super-admin')

@bp.before_request
@login_required
def restrict_to_local_server():
    # Enforce that Super Admin only works on the server machine
    if request.remote_addr != '127.0.0.1' and request.remote_addr != 'localhost':
        return "Security Violation: Super Admin access restricted to Server Machine.", 403
    if g.user.role != 'superadmin':
        return "Access Denied", 403

@bp.route('/')
def index():
    centers = Center.query.all()
    exams = Exam.query.all()
    hwid = get_hwid()
    return render_template('admin/super_dashboard.html', centers=centers, exams=exams, hwid=hwid)

@bp.route('/exam/add', methods=['POST'])
def add_exam():
    name = request.form['name']
    duration = int(request.form['duration'])
    req_sub = int(request.form['required_subjects'])
    new_exam = Exam(name=name, duration_minutes=duration, required_subjects=req_sub)
    db.session.add(new_exam)
    db.session.commit()
    flash(f"Exam type {name} created.", "success")
    return redirect(url_for('super_admin.index'))

@bp.route('/centers/add', methods=['POST'])
def add_center():
    name, loc = request.form['name'], request.form['location']
    u, p = request.form['admin_username'], request.form['admin_password']
    new_center = Center(name=name, location=loc)
    db.session.add(new_center)
    db.session.commit()
    admin = User(username=u, role='centeradmin', center_id=new_center.id)
    admin.set_password(p)
    db.session.add(admin)
    db.session.commit()
    return redirect(url_for('super_admin.index'))
