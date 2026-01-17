from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from src.app.utils.license import get_hardware_fingerprint
import os

bp = Blueprint('activation', __name__, url_prefix='/activate')

@bp.route('/', methods=['GET', 'POST'])
def index():
    fingerprint = get_hardware_fingerprint()
    
    if request.method == 'POST':
        license_key = request.form.get('license_key')
        
        # Save the key file
        try:
            key_path = os.path.join(current_app.instance_path, 'license.key')
            with open(key_path, 'w') as f:
                f.write(license_key)
            
            # Simple reload check (in production, verify immediately)
            flash("License saved! Please restart the software.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash("Error saving license.", "error")

    return render_template('activation.html', fingerprint=fingerprint)
