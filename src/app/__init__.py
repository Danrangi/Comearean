import os
import json
from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet

db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, template_folder='../resources/templates', static_folder='../resources/static')
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Default Config
    app.config.from_mapping(
        SECRET_KEY='dev',
        # In production, this LICENSE_SECRET_KEY must be fixed/constant, not generated randomly on every restart!
        LICENSE_SECRET_KEY=Fernet.generate_key(), 
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'exam_data.db'),
    )

    if test_config is None:
        # Now 'json' is imported, so this line will work
        app.config.from_file('config.json', load=json.load, silent=True)
    else:
        app.config.from_mapping(test_config)

    db.init_app(app)

    # Register Blueprints
    from .controllers import auth, admin, student, main, activation
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(student.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(activation.bp)

    # -- THE LICENSE CHECK --
    from .utils.license import verify_license
    
    @app.before_request
    def check_license():
        # Allow static files and activation page to load without license
        if request.endpoint and ('static' in request.endpoint or 'activation' in request.endpoint):
            return

        status = verify_license()
        if not status['valid']:
            # Redirect to activation "popup" page if license fails
            return redirect(url_for('activation.index'))

    return app
