import os
from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, 
                template_folder='../resources/templates',
                static_folder='../resources/static')
    
    app.config.from_object(Config)
    db.init_app(app)

    @app.before_request
    def check_license():
        if request.endpoint in ['license_expired', 'static', 'auth.login']:
            return
        from src.app.utils.license import verify_license
        if app.config.get('SKIP_LICENSE', False):
            return
        token_path = os.path.join(app.INSTANCE_DIR, 'license.bin')
        key_path = os.path.join(app.INSTANCE_DIR, 'license.key')
        if not os.path.exists(key_path):
            return redirect(url_for('license_expired'))
        with open(key_path, 'r') as f:
            key = f.read().strip()
        valid, _ = verify_license(token_path, key)
        if not valid:
            return redirect(url_for('license_expired'))

    @app.route('/license-expired')
    def license_expired():
        return "<h1>License Required</h1><p>Contact Super Admin.</p>"

    # Register Blueprints
    from src.app.controllers import auth, super_admin, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(super_admin.bp)
    app.register_blueprint(admin.bp)

    @app.route('/')
    def root():
        return redirect(url_for('auth.login'))

    return app
