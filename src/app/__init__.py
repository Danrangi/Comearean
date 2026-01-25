
def _resolve_instance_path():
    # When bundled (PyInstaller), write instance/ next to the EXE so DB/logs persist
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
        return os.path.join(base, "instance")
    # Normal dev run: use project instance folder
    return os.path.join(os.getcwd(), "instance")

def _setup_file_logging(instance_path):
    os.makedirs(os.path.join(instance_path, "logs"), exist_ok=True)
    log_file = os.path.join(instance_path, "logs", "server.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ],
    )
    logging.getLogger("werkzeug").setLevel(logging.INFO)
    return log_file

import logging
import sys
import os
from flask import Flask, redirect, url_for, request, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from .config import Config

db = SQLAlchemy()
csrf = CSRFProtect()

def _bootstrap_db(app):
    """
    Make packaged/offline runs safe:
    - create DB tables if missing
    - ensure default superadmin exists
    """
    try:
        from src.app import db
        from src.app.models import User

        with app.app_context():
            db.create_all()

            username = "CExamArena"
            password = "CExamArena@2026"

            u = User.query.filter_by(username=username).first()
            if not u:
                u = User(username=username, role="superadmin")
                if hasattr(u, "set_password"):
                    u.set_password(password)
                else:
                    u.password_hash = password
                db.session.add(u)
                db.session.commit()

    except Exception as e:
        # don't stop server; just print for logs/console
        print("[BOOT] bootstrap warning:", e)


def create_app():
    instance_path = _resolve_instance_path()
    os.makedirs(instance_path, exist_ok=True)

    instance_path = _resolve_instance_path()

    os.makedirs(instance_path, exist_ok=True)

    
    app = Flask(
        __name__,
        instance_path=instance_path,
        template_folder='../resources/templates',
        static_folder='../resources/static'
    )
    app.config.from_object(Config)
    db.init_app(app)

    _bootstrap_db(app)
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
