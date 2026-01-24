import subprocess
import platform
import os
import hashlib
import json
from datetime import datetime
from cryptography.fernet import Fernet

# --- SECURITY CONFIGURATION ---
MASTER_KEY = b'LSUKxlGQMyOXdaFBnqr9Ne8AAbAKv3YFrGewFhghLEY=' 
LICENSE_FILE = 'license.dat'

def get_hwid():
    """Generates a unique hardware ID based on the motherboard/disk."""
    system = platform.system()
    raw_id = "UNKNOWN"
    
    try:
        if system == "Windows":
            cmd = 'wmic diskdrive get serialnumber'
            raw_id = subprocess.check_output(cmd, shell=True).decode().split('\n')[1].strip()
        elif system == "Linux":
            if os.path.exists("/etc/machine-id"):
                with open("/etc/machine-id") as f: 
                    raw_id = f.read().strip()
            else:
                raw_id = subprocess.check_output(['cat', '/sys/class/dmi/id/product_uuid']).decode().strip()
    except Exception:
        raw_id = platform.node() 

    return hashlib.sha256(raw_id.encode()).hexdigest()[:16].upper()

def verify_license(app_root):
    license_path = os.path.join(app_root, 'instance', LICENSE_FILE)
    if not os.path.exists(license_path): return False, "License Not Found"
    try:
        with open(license_path, 'rb') as f: encrypted_token = f.read()
        cipher = Fernet(MASTER_KEY)
        data = json.loads(cipher.decrypt(encrypted_token).decode())
        
        if data['hw_id'] != get_hwid(): return False, "Invalid Machine (Hardware Mismatch)"
        if datetime.now() > datetime.strptime(data['expiry'], '%Y-%m-%d'): return False, "License Expired"
        
        return True, f"Active until {data['expiry']}"
    except: return False, "Invalid License Key"

def save_license(app_root, token):
    instance_dir = os.path.join(app_root, 'instance')
    if not os.path.exists(instance_dir): os.makedirs(instance_dir)
    with open(os.path.join(instance_dir, LICENSE_FILE), 'wb') as f: f.write(token.encode())
