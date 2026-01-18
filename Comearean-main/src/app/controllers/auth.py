from flask import Blueprint, render_template, redirect, url_for, request, flash, session, g, current_app
from src.app.models import User, db
from src.app.utils.license import get_hwid, save_license, verify_license
from functools import wraps

bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session: return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None: g.user = None
    else: g.user = User.query.get(user_id)

@bp.route('/activate', methods=['GET', 'POST'])
def activate():
    hwid = get_hwid()
    error = None
    if request.method == 'POST':
        key = request.form.get('activation_key')
        save_license(current_app.root_path, key)
        is_valid, msg = verify_license(current_app.root_path)
        if is_valid:
            flash("Software Activated Successfully!", "success")
            return redirect(url_for('auth.login'))
        else: error = msg
    return render_template('auth/activate.html', hwid=hwid, error=error)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            session['role'] = user.role
            if user.role == 'superadmin': return redirect(url_for('super_admin.index'))
            elif user.role == 'centeradmin': return redirect(url_for('admin.index'))
            else: return redirect(url_for('main.dashboard'))
        flash('Invalid Username or Password', 'danger')
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
