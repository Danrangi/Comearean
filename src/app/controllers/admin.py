from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from src.app import db
from src.app.models import User, Result
from .auth import login_required

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.before_request
@login_required
def restrict_access():
    if g.user.role != 'centeradmin':
        return redirect(url_for('auth.login'))

@bp.route('/')
def index():
    students = User.query.filter_by(center_id=g.user.center_id, role='student').all()
    return render_template('admin/center_dashboard.html', students=students)

@bp.route('/student/add', methods=['POST'])
def add_student():
    username = request.form.get('username')
    password = request.form.get('password')
    if User.query.filter_by(username=username).first():
        flash("Student ID already exists.", "danger")
    else:
        student = User(username=username, role='student', center_id=g.user.center_id)
        student.set_password(password)
        db.session.add(student)
        db.session.commit()
        flash(f"Student {username} registered.", "success")
    return redirect(url_for('admin.index'))

@bp.route('/student/edit/<int:id>', methods=['POST'])
def edit_student(id):
    student = User.query.get_or_404(id)
    if student.center_id != g.user.center_id:
        return "Unauthorized", 403
    
    new_username = request.form.get('username')
    new_password = request.form.get('password')
    
    student.username = new_username
    if new_password:
        student.set_password(new_password)
    
    db.session.commit()
    flash("Student record updated.", "success")
    return redirect(url_for('admin.index'))

@bp.route('/student/delete/<int:id>', methods=['POST'])
def delete_student(id):
    student = User.query.get_or_404(id)
    if student.center_id != g.user.center_id:
        return "Unauthorized", 403
    
    # Delete associated results first to avoid foreign key errors
    Result.query.filter_by(user_id=id).delete()
    db.session.delete(student)
    db.session.commit()
    flash("Student and their results deleted.", "info")
    return redirect(url_for('admin.index'))

@bp.route('/student/reset/<int:id>')
def reset_student(id):
    student = User.query.get_or_404(id)
    if student.center_id == g.user.center_id:
        student.is_writing = False
        db.session.commit()
        flash(f"Session reset for {student.username}", "info")
    return redirect(url_for('admin.index'))
