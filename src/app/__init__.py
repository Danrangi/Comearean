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

    # Register Licensing Middleware
    @app.before_request
    def check_license():
        # Allow access to the expired page and static files
        if request.endpoint in ['license_expired', 'static']:
            return
            
        from .utils.license import verify_license
        # In dev, you can set this to True in config.json to bypass
        if app.config.get('SKIP_LICENSE', False):
            return

        token_path = os.path.join(app.instance_path, 'license.bin')
        key_path = os.path.join(app.instance_path, 'license.key')
        
        if not os.path.exists(key_path):
            return redirect(url_for('license_expired'))
            
        with open(key_path, 'r') as f:
            key = f.read().strip()
            
        valid, _ = verify_license(token_path, key)
        if not valid:
            return redirect(url_for('license_expired'))

    @app.route('/license-expired')
    def license_expired():
        return "<h1>License Required</h1><p>Please contact the Super Admin to activate this center.</p>"

    # Import and register blueprints here (once created)
    # from .controllers.auth import bp as auth_bp
    # app.register_blueprint(auth_bp)

    return app
