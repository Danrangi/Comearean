import sys
import json
from cryptography.fernet import Fernet
from datetime import datetime, timedelta

def generate(hwid, days):
    key = Fernet.generate_key().decode()
    f = Fernet(key.encode())
    expiry = (datetime.utcnow() + timedelta(days=int(days))).strftime('%Y-%m-%d')
    token = f.encrypt(json.dumps({"hwid": hwid, "expiry": expiry}).encode()).decode()
    print(f"KEY: {key}\nTOKEN: {token}")

if __name__ == "__main__":
    if len(sys.argv) < 3: print("Usage: python generate_key.py <HWID> <DAYS>")
    else: generate(sys.argv[1], sys.argv[2])
