# 🎓 Exam Arena — Offline CBT Examination System

**Exam Arena** is a fully offline, LAN-based Computer-Based Testing (CBT) system designed for schools, tutorial centers, and examination centers preparing students for **JAMB, WAEC, and NECO**.

It runs as a **local server** on one computer and allows multiple students to take exams simultaneously from other computers connected via **Wi-Fi / hotspot / LAN**, without internet access.

---

## 🚀 Key Highlights

- ✅ **100% Offline** — no internet required after setup  
- 🖥️ **One-Click Server (.exe)** — no Python installation needed  
- 🌐 **LAN / Hotspot Based** — students connect via browser  
- 🔐 **License Activation** — per-center activation  
- 🧑‍🏫 **Role-Based Access**
  - Super Admin
  - Center Admin
  - Students
- 📚 **JAMB / WAEC / NECO Exam Logic**
- 🧮 **Per-Subject Question Limits**
- 📊 **Result Management & PDF Downloads**
- 🖨️ **Printable Result Slips**

---

## 🧠 How Exam Arena Works (Simple Flow)

1. **Server Computer**
   - Runs `ExamArena_Server.exe`
   - Hosts the CBT system
   - Stores all data (questions, students, results)

2. **Client Computers**
   - Connect to the server via Wi-Fi / hotspot / LAN
   - Open browser and access:
     ```
     http://SERVER-IP:8080
     ```

3. **Admins**
   - Manage exams, subjects, questions, students
   - Download student result PDFs

4. **Students**
   - Login and take exams
   - See only the required number of questions (not all)

---

## 👥 User Roles Explained

### 🔑 Super Admin
- Creates exams (JAMB / WAEC / NECO)
- Creates subjects
- Sets **question limit per subject**
- Uploads questions (CSV or manual)
- Full system control

### 🏫 Center Admin
- Registers students
- Manages students in their center
- Views & downloads **each student’s result**
- Prints result slips (PDF)

### 👨‍🎓 Students
- Login with credentials
- Take exams
- Questions are **randomized**
- Only see the number of questions allowed for that subject

---

## 📘 Exam Logic Supported

### JAMB
- English: **60 questions**
- Other subjects: **40 questions each**

### WAEC
- Objective questions (50–60)
- Essay/theory supported in future versions

### NECO
- Objective + theory structure supported (objective currently active)

> Each subject has its **own question limit**, configurable by Super Admin.

---

## 📂 Question Management

- Add questions manually
- Upload questions via **CSV**
- Questions are:
  - Randomized per student
  - Limited by subject setting
- Students never see all uploaded questions

---

## 📊 Results & Reporting

- Automatic score calculation
- Results saved per student
- Center Admin can:
  - View all results
  - Download **individual student result PDFs**
  - Print result slips

---

## 🖨️ Result Slip (PDF)

Each result slip includes:
- Student name
- Center
- Exam & subject
- Score
- Total questions
- Date & time

Generated offline using PDF engine.

---

## 🔐 License & Activation

- First launch requires activation
- License is tied to the **server computer**
- After activation:
  - No repeated activation on restart
  - Works offline permanently

---

## 🛠️ Installation & Usage

### ✅ Server Setup (Windows)

1. Copy the provided setup folder to the server computer
2. Run:

or
3. First launch → activate license
4. Login as Super Admin

### 🌐 Client Access

1. Connect client computers to the **server hotspot / LAN**
2. Open browser
3. Visit:

(Change after setup)

---

## 🧪 Tested Environment

- Windows 7 / 8 / 10 / 11
- Offline LAN / Hotspot
- Modern browsers (Chrome, Edge, Firefox)

---

## 🧱 Tech Stack (Internal)

- Python (Flask)
- SQLite (offline database)
- Jinja2 (templates)
- Bootstrap (offline)
- ReportLab (PDF)
- PyInstaller (.exe packaging)

---

## 📌 Project Status

✅ **MVP Completed & Functional**  
🚧 Future Improvements:
- Essay/theory marking
- Question diagrams & images
- Passages (English comprehension)
- Analytics dashboard
- Multi-center deployment

---

## 🤝 Credits

Developed by **Danrangi**  
Built for real CBT centers — not demos.

---

## 📞 Support

For deployment help, customization, or improvements:
- Contact the developer
- Or open an issue in this repository

---

**Exam Arena — Practice Smart. Exam Ready.** 🎯
