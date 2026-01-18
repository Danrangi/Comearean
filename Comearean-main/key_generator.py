import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import sys
import os

# --- CONFIGURATION ---
# MUST MATCH src/app/utils/license.py EXACTLY
MASTER_KEY = b'LSUKxlGQMyOXdaFBnqr9Ne8AAbAKv3YFrGewFhghLEY=' 

class KeyGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ExamArena License Generator")
        self.root.geometry("500x450")
        try:
            self.root.configure(bg="#f0f0f0")
        except: pass

        # Title
        tk.Label(root, text="License Generator", font=("Arial", 16, "bold"), fg="#333").pack(pady=20)

        # System ID Input
        tk.Label(root, text="Client System ID:", font=("Arial", 10)).pack(anchor="w", padx=20)
        self.entry_sys_id = tk.Entry(root, font=("Arial", 11), width=40)
        self.entry_sys_id.pack(pady=5, padx=20)

        # Duration Input
        tk.Label(root, text="Duration (Days):", font=("Arial", 10)).pack(anchor="w", padx=20)
        self.entry_days = tk.Entry(root, font=("Arial", 11), width=40)
        self.entry_days.insert(0, "365") # Default to 1 year
        self.entry_days.pack(pady=5, padx=20)

        # Generate Button
        self.btn_generate = tk.Button(root, text="Generate Key", font=("Arial", 11, "bold"),
                                      bg="#007bff", fg="white", command=self.generate_key,
                                      padx=20, pady=5, bd=0)
        self.btn_generate.pack(pady=20)

        # Output Area
        tk.Label(root, text="Activation Key (Copy this):", font=("Arial", 10)).pack(anchor="w", padx=20)
        self.text_output = tk.Text(root, height=5, font=("Consolas", 9), width=55)
        self.text_output.pack(pady=5, padx=20)

    def generate_key(self):
        sys_id = self.entry_sys_id.get().strip()
        days_str = self.entry_days.get().strip()

        if not sys_id:
            messagebox.showerror("Error", "Please enter a System ID")
            return
        
        try:
            days = int(days_str)
        except ValueError:
            messagebox.showerror("Error", "Days must be a number")
            return

        try:
            cipher = Fernet(MASTER_KEY)
            expiry_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            
            license_data = {
                "hw_id": sys_id,
                "expiry": expiry_date
            }
            
            token = cipher.encrypt(json.dumps(license_data).encode()).decode()
            
            self.text_output.delete(1.0, tk.END)
            self.text_output.insert(tk.END, token)
            messagebox.showinfo("Success", f"Key Generated! Valid until {expiry_date}")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    if os.environ.get('DISPLAY','') == '':
        print('no display found. Using :0.0')
        os.environ.__setitem__('DISPLAY', ':0.0')
    root = tk.Tk()
    app = KeyGeneratorApp(root)
    root.mainloop()
