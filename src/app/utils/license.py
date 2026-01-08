import hashlib
import platform
import subprocess
import os
import json
from cryptography.fernet import Fernet
from datetime import datetime

def get_hwid():
    system = platform.system()
    raw_id = platform.node()
    try:
        if system == "Windows":
            raw_id = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()
        elif system == "Linux":
            if os.path.exists("/etc/machine-id"):
                with open("/etc/machine-id") as f: raw_id = f.read().strip()
    except: pass
    return hashlib.sha256(raw_id.encode()).hexdigest()

def verify_license(token_path, key):
    if not os.path.exists(token_path): return False, "License file missing"
    try:
        f = Fernet(key.encode())
        with open(token_path, 'rb') as file:
            data = json.loads(f.decrypt(file.read()).decode())
        if data['hwid'] != get_hwid(): return False, "Hardware mismatch"
        if datetime.utcnow() > datetime.strptime(data['expiry'], '%Y-%m-%d'):
            return False, "License expired"
        return True, data
    except: return False, "Invalid license"
