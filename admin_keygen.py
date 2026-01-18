import json
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

# --- CONFIGURATION ---
# This matches the key we put in your Flask app
MASTER_KEY = b'eX0d_Q7w_Q9_1-w_M5w_R9s-w_Q9_1-w_M5w_R9s-w4=' 

def generate_license():
    cipher = Fernet(MASTER_KEY)
    
    print("\n--- ExamArena License Generator ---")
    
    # 1. Get Client Info
    system_id = input("Enter Client System ID (e.g. D011...): ").strip()
    if not system_id:
        print("Error: System ID is required.")
        return

    try:
        days = int(input("Enter Subscription Days (Default 365): ") or 365)
    except ValueError:
        print("Invalid number. Using 365.")
        days = 365
    
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
    print(f"ACTIVATION KEY (Expires: {expiry_date}):")
    print("-" * 60)
    print(token)
    print("="*60 + "\n")

if __name__ == "__main__":
    generate_license()
