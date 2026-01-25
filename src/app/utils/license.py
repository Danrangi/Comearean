import subprocess
import platform
import os
import hashlib
import json
from datetime import datetime
from cryptography.fernet import Fernet, InvalidToken

# --- LICENSE STORAGE ---
LICENSE_FILE = "license.dat"

# --- SECURITY CONFIGURATION ---
# Default key (kept for backward compatibility).
# You can override this at runtime using the environment variable:
#   COMEAREAN_MASTER_KEY="base64_fernet_key_here"
_DEFAULT_MASTER_KEY = b"LSUKxlGQMyOXdaFBnqr9Ne8AAbAKv3YFrGewFhghLEY="

def _get_master_key() -> bytes:
    """Returns the Fernet key. Uses env override if present."""
    env_key = os.getenv("COMEAREAN_MASTER_KEY", "").strip()
    if not env_key:
        return _DEFAULT_MASTER_KEY

    try:
        key_bytes = env_key.encode("utf-8")
    except Exception:
        return _DEFAULT_MASTER_KEY

    # Validate format; if invalid, fall back to default (avoids breaking runtime).
    try:
        Fernet(key_bytes)
        return key_bytes
    except Exception:
        return _DEFAULT_MASTER_KEY

def get_hwid() -> str:
    """Generates a stable hardware ID (best effort) and returns a short hash."""
    system = platform.system()
    raw_id = "UNKNOWN"

    try:
        if system == "Windows":
            cmd = "wmic diskdrive get serialnumber"
            raw = subprocess.check_output(cmd, shell=True).decode(errors="ignore").splitlines()
            candidates = [x.strip() for x in raw[1:] if x.strip()]
            raw_id = candidates[0] if candidates else platform.node()
        elif system == "Linux":
            if os.path.exists("/etc/machine-id"):
                with open("/etc/machine-id", "r", encoding="utf-8", errors="ignore") as f:
                    raw_id = f.read().strip()
            elif os.path.exists("/sys/class/dmi/id/product_uuid"):
                raw_id = subprocess.check_output(["cat", "/sys/class/dmi/id/product_uuid"]).decode().strip()
            else:
                raw_id = platform.node()
        else:
            raw_id = platform.node()
    except Exception:
        raw_id = platform.node()

    return hashlib.sha256(raw_id.encode("utf-8", errors="ignore")).hexdigest()[:16].upper()

def _license_path(app_root: str) -> str:
    instance_dir = os.path.join(app_root, "instance")
    return os.path.join(instance_dir, LICENSE_FILE)

def verify_license(app_root: str):
    """Validates the license token stored on disk."""
    license_path = _license_path(app_root)
    if not os.path.exists(license_path):
        return False, "License Not Found"

    try:
        with open(license_path, "rb") as f:
            encrypted_token = f.read()

        cipher = Fernet(_get_master_key())
        payload = cipher.decrypt(encrypted_token).decode("utf-8", errors="ignore")
        data = json.loads(payload)

        if data.get("hw_id") != get_hwid():
            return False, "Invalid Machine (Hardware Mismatch)"

        expiry_str = data.get("expiry")
        if not expiry_str:
            return False, "Invalid License Key"

        expiry_dt = datetime.strptime(expiry_str, "%Y-%m-%d")
        if datetime.now() > expiry_dt:
            return False, "License Expired"

        return True, f"Active until {expiry_str}"

    except InvalidToken:
        return False, "Invalid License Key"
    except Exception:
        return False, "Invalid License Key"

def save_license(app_root: str, token: str):
    """Saves the license token string to disk as bytes."""
    token = (token or "").strip()
    instance_dir = os.path.join(app_root, "instance")
    os.makedirs(instance_dir, exist_ok=True)

    with open(os.path.join(instance_dir, LICENSE_FILE), "wb") as f:
        f.write(token.encode("utf-8"))
