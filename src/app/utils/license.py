import os
import json
import hashlib
import platform
import uuid
from datetime import datetime
from cryptography.fernet import Fernet, InvalidToken

# ---------------- CONFIG ----------------

LICENSE_FILE = "license.dat"

# Default master key (keep your existing one)
_DEFAULT_MASTER_KEY = b"LSUKxlGQMyOXdaFBnqr9Ne8AAbAKv3YFrGewFhghLEY="


# ---------------- SECURITY ----------------

def _get_master_key() -> bytes:
    env_key = os.getenv("COMEAREAN_MASTER_KEY", "").strip()

    if not env_key:
        return _DEFAULT_MASTER_KEY

    try:
        key_bytes = env_key.encode("utf-8")
        Fernet(key_bytes)
        return key_bytes
    except Exception:
        return _DEFAULT_MASTER_KEY


# ---------------- STABLE FINGERPRINT ----------------

def get_hwid() -> str:
    """
    Stable hardware fingerprint.
    Fixes changing activation code on restart.
    """

    parts = []

    # Windows stable ID (best)
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography"
        )
        machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
        parts.append(str(machine_guid))
    except Exception:
        pass

    # MAC address fallback
    try:
        mac = uuid.getnode()
        parts.append(str(mac))
    except Exception:
        pass

    # Basic system info (extra stability)
    try:
        parts.append(platform.node())
        parts.append(platform.system())
        parts.append(platform.release())
    except Exception:
        pass

    raw = "|".join([p for p in parts if p]).encode("utf-8")
    return hashlib.sha256(raw).hexdigest().upper()


# ---------------- LICENSE PATH ----------------

def _license_path(instance_path: str) -> str:
    """
    Always store license inside instance/ folder
    so EXE restart keeps it.
    """
    os.makedirs(instance_path, exist_ok=True)
    return os.path.join(instance_path, LICENSE_FILE)


# ---------------- VERIFY ----------------

def verify_license(instance_path: str):
    license_path = _license_path(instance_path)

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


# ---------------- SAVE ----------------

def save_license(instance_path: str, token: str):
    token = (token or "").strip()
    license_path = _license_path(instance_path)

    with open(license_path, "wb") as f:
        f.write(token.encode("utf-8"))
