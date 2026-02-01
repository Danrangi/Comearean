import os
import sys
import logging

from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from .config import Config

db = SQLAlchemy()
csrf = CSRFProtect()


def _resolve_instance_path():
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
        return os.path.join(base, "instance")
    return os.path.join(os.getcwd(), "instance")


def _setup_file_logging(instance_path: str) -> str:
    logs_dir = os.path.join(instance_path, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, "server.log")

    root_logger = logging.getLogger()
    if not root_logger.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
        logging.getLogger("werkzeug").setLevel(logging.INFO)

    return log_file


# ✅ MUST BE ABOVE create_app()
def _bootstrap_db(app: Flask):
    try:
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

            app.logger.info("[BOOT] Database ready")

    except Exception as e:
        print("[BOOT] bootstrap warning:", e)


def create_app():
    instance_path = _resolve_instance_path()
    os.makedirs(instance_path, exist_ok=True)

    log_file = _setup_file_logging(instance_path)

    app = Flask(
        __name__,
        instance_path=instance_path,
        template_folder="../resources/templates",
        static_folder="../resources/static",
    )

    app.config.from_object(Config)

    db.init_app(app)
    csrf.init_app(app)

    # ✅ Now this exists
    _bootstrap_db(app)

    app.logger.info(f"[BOOT] Instance path: {instance_path}")
    app.logger.info(f"[BOOT] Logging to: {log_file}")

    # License gate
    from src.app.utils.license import verify_license

    @app.before_request
    def check_license_gate():
        if request.endpoint in ["auth.activate", "auth.login", "auth.logout", "auth.about", "static"]:
            return

        is_valid, _ = verify_license(app.instance_path)
        if not is_valid:
            return redirect(url_for("auth.activate"))

    from src.app.controllers import auth, super_admin, admin, main

    app.register_blueprint(auth.bp)
    app.register_blueprint(super_admin.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(main.bp)

    @app.route("/")
    def root():
        return redirect(url_for("auth.login"))

    return app
