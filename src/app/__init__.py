import os
import json
from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet

db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, template_folder='../resources/templates', static_folder='../resources/static')
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # --- MASTER KEY (VALIDATED) ---
    # This specific key works. Do not change it unless you reset everyone's license.
    MASTER_KEY = b'eX0d_Q7w_Q9_1-w_M5w_R9s-w_Q9_1-w_M5w_R9s-w4=' 

    app.config.from_mapping(
        SECRET_KEY='dev',
        LICENSE_SECRET_KEY=MASTER_KEY, 
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'exam_data.db'),
    )

    if test_config is None:
        app.config.from_file('config.json', load=json.load, silent=True)
    else:
        app.config.from_mapping(test_config)

    db.init_app(app)

    from .controllers import auth, admin, student, main, activation
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(student.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(activation.bp)

    from .utils.license import verify_license
    
    @app.before_request
    def check_license():
        if request.endpoint and ('static' in request.endpoint or 'activation' in request.endpoint):
            return

        status = verify_license()
        if not status['valid']:
            return redirect(url_for('activation.index'))

    return app
