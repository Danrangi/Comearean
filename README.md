**Exam Arena: The Ultimate Commercial CBT Platform**

Exam Arena is a polished, commercial-grade Computer-Based Testing (CBT) platform built for educational centers, certification bodies, and enterprises that require a LAN-first, privacy-respecting, and high-availability exam system.

---

**Product Vision**

Exam Arena is designed as a Server-Client (LAN) platform that empowers exam centers to run secure, scalable, and reliable assessments on their local network. The application is offline-first — clients (browsers) can continue functioning during intermittent connectivity to the server, while the server provides authoritative data persistence, licensing enforcement, and analytics processing. Coming soon: advanced AI Performance Analytics to provide personalized tutoring, automated question analysis, and candidate-level recommendations.

**Primary Goals**
- Secure, hardware-bound licensing for center operators
- Multi-tenant architecture with a clear SuperAdmin / CenterAdmin / Student hierarchy
- Reliable offline-first behavior for exams on LANs
- Extensible AI analytics pipeline (Phase 3 roadmap)

---

**Feature Matrix**

- Super Admin (Global)
	- License activation and hardware-bound license management
	- Create and manage Centers and Center Admin accounts
	- Global exams, subjects, and question pools (optionally tenant-scoped)
- Center Admin (Per-Center)
	- Manage students and bulk-import via CSV
	- Run exams, monitor live sessions, kick/extend sessions
	- View center analytics, export CSV reports
- Student (War Room)
	- Fast, distraction-minimized exam interface (War Room)
	- View historical results and subject-level breakdowns

---

**Licensing System**

Exam Arena uses a hardware-bound licensing model: each license token is cryptographically encrypted and tied to a center's hardware fingerprint (server machine). License tokens may be issued for different durations (30-day trial, annual subscription). The system checks the encrypted token on the server at runtime and will deny access if the token is missing, expired, or bound to a different hardware fingerprint. A Super Admin UI is provided to paste or upload license tokens and view the server fingerprint.

Supported license plans
- 30-Day Trial — Limited feature access, single center
- Annual — Full feature set for a single licensed server

---

**Visuals (placeholders)**

- Dashboard screenshot: ![Dashboard Placeholder](src/resources/static/img/dashboard-placeholder.png)
- Exam interface (War Room): ![Exam Interface Placeholder](src/resources/templates/exam/exam-placeholder.png)
- Analytics and AI preview: ![Analytics Placeholder](src/resources/static/img/analytics-placeholder.png)

---

**Tech Stack**

- Backend: Python 3.x with Flask
- ORM: SQLAlchemy (via Flask-SQLAlchemy)
- Forms: Flask-WTF
- Encryption: cryptography.Fernet (for license tokens)
- Production WSGI: Waitress (Windows-friendly) or your preferred WSGI server
- Configuration: python-dotenv for environment management

---

**Installation (Server)**

1. Clone the repository to your server machine.

2. Create a Python virtual environment and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r ExamArena/requirements.txt
```

4. Initialize instance folder and configuration (example):

```bash
cp -r ExamArena/instance.example ExamArena/instance
export FLASK_APP=ExamArena/run.py
export FLASK_ENV=production
# Put your SECRET_KEY and DB URI into instance/config.json or use .env
```

5. Initialize the database (development quickstart):

```bash
python3 ExamArena/scripts/init_db.py
```

6. Generate or obtain a license token for your server. Use the `scripts/generate_key.py` helper on the operator machine to produce a key/token; upload or paste token into the SuperAdmin -> Licensing page.

7. Run the server (development):

```bash
flask --app ExamArena.run run --host=0.0.0.0 --port=5000
```

Run in production using Waitress:

```bash
waitress-serve --listen=0.0.0.0:8080 ExamArena.run:create_app()
```

**Connecting Clients**

Clients connect via browser to the server's IP and port on the LAN (e.g., http://10.0.0.5:8080). Exam Arena is designed to be responsive and work on modern browsers.

---

**Phase 3 Roadmap — AI Tutor & Analytics**

- Phase 3.1 — AI Performance Analytics (Q2)
	- Per-student insights and difficulty modeling
	- Topic-based performance heatmaps
- Phase 3.2 — AI Tutor (Q3)
	- Personalized practice recommendations
	- Auto-generated micro-explanations and targeted drills
- Phase 3.3 — Auto-Quality Assurance (Q4)
	- Auto-flagging of ambiguous or low-quality questions
	- Guided item banking and difficulty recalibration

---

Contributing and Support

If you're deploying this commercially we recommend:
- Use Alembic for database migrations in production
- Store the `license.key` in a secure secret manager (avoid storing on disk in production)
- Harden server networking and use HTTPS via a reverse-proxy in front of Waitress

For questions, feature requests or enterprise integration help, open an issue or contact the maintainer.

Thank you for choosing Exam Arena — built for reliability, security, and impactful assessment analytics. 

-- The Exam Arena Team
