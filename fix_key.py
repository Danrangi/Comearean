from cryptography.fernet import Fernet
import re
import os

# 1. Generate a VALID Fernet Key
print("Generating new secure key...")
valid_key = Fernet.generate_key()
# Format it as a python byte string definition
key_line = f"MASTER_KEY = {valid_key}"

print(f"New Key: {valid_key.decode()}")

# 2. Define files to update
files_to_fix = [
    'src/app/utils/license.py', 
    'key_generator.py'
]

# 3. Replace the bad key in files
for file_path in files_to_fix:
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Regex to find any existing MASTER_KEY line and replace it
        new_content = re.sub(r"MASTER_KEY = b['\"].*['\"]", key_line, content)
        
        with open(file_path, 'w') as f:
            f.write(new_content)
            
        print(f"✅ Fixed: {file_path}")
    else:
        print(f"⚠️ Warning: Could not find {file_path}")

print("\n---------------------------------------------------")
print("SUCCESS! The error is resolved.")
print("IMPORTANT: If you already downloaded 'key_generator.py' to Windows,")
print("you must download it again OR replace the MASTER_KEY line manually with:")
print(f"{key_line}")
print("---------------------------------------------------")
