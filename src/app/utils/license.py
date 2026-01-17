import platform
import hashlib
import os
import json
from datetime import datetime
from cryptography.fernet import Fernet
from flask import current_app

# -- 1. Hardware Fingerprinting --
def get_hardware_fingerprint():
    """Generates a unique SHA-256 hash based on the machine's hardware."""
    # Combine Node Name (Computer Name) + Machine Type + Processor
    raw_data = f"{platform.node()}-{platform.machine()}-{platform.processor()}"
    return hashlib.sha256(raw_data.encode()).hexdigest().upper()[:16] # Shorten to 16 chars

# -- 2. License Validation --
def load_license_key():
    """Loads the license key from the instance folder."""
    key_path = os.path.join(current_app.instance_path, 'license.key')
    if not os.path.exists(key_path):
        return None
    try:
        with open(key_path, 'r') as f:
            return f.read().strip()
    except:
        return None

def verify_license():
    """
    Checks if the license is:
    1. Present
    2. Valid for this specific machine (Hardware Lock)
    3. Not expired
    """
    license_token = load_license_key()
    if not license_token:
        return {'valid': False, 'reason': 'No license found'}

    fingerprint = get_hardware_fingerprint()
    
    # In a real app, you would verify a digital signature here.
    # For now, we decode the simple JSON token structure: 
    # Token Format: base64(json({ "hw_id": "...", "expiry": "YYYY-MM-DD" }))
    
    try:
        # We use the App's SECRET_KEY to decrypt (Symmetric Encryption)
        # NOTE: For maximum security, use Asymmetric (Private/Public Key) in future.
        fernet = Fernet(current_app.config.get('LICENSE_SECRET_KEY')) 
        data = json.loads(fernet.decrypt(license_token.encode()).decode())
        
        if data['hw_id'] != fingerprint:
             return {'valid': False, 'reason': 'License does not match this computer'}
        
        expiry_date = datetime.strptime(data['expiry'], '%Y-%m-%d')
        if datetime.now() > expiry_date:
            return {'valid': False, 'reason': 'License expired'}

        return {'valid': True, 'expiry': data['expiry']}

    except Exception as e:
        return {'valid': False, 'reason': 'Invalid license file'}
