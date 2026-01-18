from flask import Blueprint, redirect, url_for

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # When a user visits the root domain, redirect them to login
    return redirect(url_for('auth.login'))
