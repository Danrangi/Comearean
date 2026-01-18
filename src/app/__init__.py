import os
import json
from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from cryptography.fernet import Fernet

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app(test_config=None):
    # 1. Force the instance path to be inside the project root
    base_dir = os.path.abspath(os.path.dirname(__file__)) # src/app/
    project_root = os.path.abspath(os.path.join(base_dir, '..', '..')) # Comearean/
    instance_path = os.path.join(project_root, 'instance')

    app = Flask(__name__, 
                instance_path=instance_path,
                instance_relative_config=True, 
                template_folder='../resources/templates', 
                static_folder='../resources/static')
    
    # 2. Create the instance folder immediately
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # 3. Master Key (Do not change)
    MASTER_KEY = b'eX0d_Q7w_Q9_1-w_M5w_R9s-w_Q9_1-w_M5w_R9s-w4=' 

    # 4. Correct Database URI for Linux/Windows
    db_file_path = os.path.join(app.instance_path, 'exam_data.db')
    
    # SQLite needs 4 slashes for absolute paths on Unix (Linux/Codespaces)
    if os.name == 'nt': # Windows
        db_uri = f'sqlite:///{db_file_path}'
    else: # Linux
        db_uri = f'sqlite:////{db_file_path}'

    app.config.from_mapping(
        SECRET_KEY='dev',
        LICENSE_SECRET_KEY=MASTER_KEY, 
        SQLALCHEMY_DATABASE_URI=db_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    # 5. Load config but DO NOT overwrite DB URI if it fails
    if test_config is None:
        try:
            app.config.from_file('config.json', load=json.load, silent=True)
        except:
            pass
    else:
        app.config.from_mapping(test_config)

    db.init_app(app)
    csrf.init_app(app)

    # 6. Import Controllers
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
