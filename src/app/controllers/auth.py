from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from src.app.models import User
from src.app import db
from werkzeug.security import check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        # FIX: Check against user.password_hash
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session['user_id'] = user.id
            flash('Logged in successfully.', 'success')
            
            if user.role in ['super_admin', 'admin']:
                return redirect(url_for('admin.index'))
            else:
                return redirect(url_for('student.dashboard'))
                
        flash('Incorrect username or password.', 'error')

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)
