from flask import Blueprint, render_template, request, redirect, url_for, g
from src.app.models import Center, User, db
from .auth import login_required

bp = Blueprint('super_admin', __name__, url_prefix='/super-admin')

@bp.before_request
@login_required
def restrict_to_super_admin():
    if g.user.role != 'superadmin':
        return "Access Denied", 403

@bp.route('/')
def index():
    centers = Center.query.all()
    return render_template('admin/centers.html', centers=centers)

@bp.route('/centers/add', methods=['POST'])
def add_center():
    name = request.form['name']
    location = request.form['location']
    new_center = Center(name=name, location=location)
    db.session.add(new_center)
    db.session.commit()
    
    admin = User(username=f"admin_{new_center.id}", role='centeradmin', center_id=new_center.id)
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    return redirect(url_for('super_admin.index'))
