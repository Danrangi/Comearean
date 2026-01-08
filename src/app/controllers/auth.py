from flask import Blueprint, render_template, redirect, url_for, request, flash, session, g
from src.app.models import User, db
from functools import wraps

bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)

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
            if user.role == 'superadmin':
                return redirect(url_for('super_admin.index'))
            # Note: We will add the centeradmin redirect once admin.py is created
            return redirect(url_for('auth.login'))
        
        flash('Invalid Credentials')
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
