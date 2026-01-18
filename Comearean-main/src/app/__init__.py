import os
from flask import Flask, redirect, url_for, request, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from .config import Config

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, template_folder='../resources/templates', static_folder='../resources/static')
    app.config.from_object(Config)
    db.init_app(app)
    csrf.init_app(app)

    from src.app.utils.license import verify_license
    @app.before_request
    def check_license_gate():
        if request.endpoint in ['auth.activate', 'static', 'auth.login']: return
        is_valid, _ = verify_license(app.root_path)
        if not is_valid: return redirect(url_for('auth.activate'))

    from src.app.controllers import auth, super_admin, admin, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(super_admin.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(main.bp)
    
    @app.route('/')
    def root(): return redirect(url_for('auth.login'))
    return app
