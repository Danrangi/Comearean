import json
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

# --- CONFIGURATION ---
# This MUST match the key in src/app/__init__.py
MASTER_KEY = b'8_5Qd1p1-u_M5w_R9s-w_Q9_1-w_M5w_R9s-w_Q9_1=' 

def generate_license():
    cipher = Fernet(MASTER_KEY)
    
    print("\n--- ExamArena License Generator ---")
    print("Use this tool to generate keys for your clients.\n")
    
    # 1. Get Client Info
    system_id = input("Enter Client System ID (e.g. D011...): ").strip()
    days = int(input("Enter Subscription Days (e.g. 30, 365): "))
    
    # 2. Calculate Expiry
    expiry_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    
    # 3. Create Payload
    license_data = {
        "hw_id": system_id,
        "expiry": expiry_date
    }
    
    # 4. Encrypt
    token = cipher.encrypt(json.dumps(license_data).encode()).decode()
    
    print("\n" + "="*60)
    print(f"LICENSE KEY (Valid until {expiry_date}):")
    print("-" * 60)
    print(token)
    print("="*60 + "\n")
    print("Copy the string above and send it to the client.")

if __name__ == "__main__":
    try:
        generate_license()
    except Exception as e:
        print(f"Error: {e}")
        # If the key format is wrong (unlikely with hardcoded value), it might fail here
