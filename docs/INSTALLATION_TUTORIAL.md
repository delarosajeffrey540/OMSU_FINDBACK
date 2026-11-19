# OMSU FindBack — installation and backend tutorial

## 1. Requirements
- Windows 10/11
- Python 3.10 or newer
- XAMPP (Apache is optional; start MySQL)
- VS Code

## 2. Extract and open the project
Extract `OMSU_FINDBACK.zip`. Open the `OMSU_FINDBACK` folder in VS Code.

## 3. Create a virtual environment
Open the VS Code terminal (PowerShell) and run:

```powershell
py -3.13 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and activate again.

## 4. Create the MySQL database in XAMPP
1. Open XAMPP Control Panel.
2. Click **Start** beside MySQL.
3. Open `http://localhost/phpmyadmin`.
4. Select **New** and create a database named `omsu_findback`.
5. Use collation `utf8mb4_unicode_ci`.

Alternatively, import `database/schema.sql` in phpMyAdmin.

## 5. Configure environment variables
1. Copy `.env.example` and rename the copy to `.env`.
2. Open `.env`.
3. Set DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD to match your XAMPP MySQL setup.
4. Replace SECRET_KEY with a long random value. Do not share or upload `.env`.
5. If your existing `.env` contains `UPLOAD_FOLDER=static/uploads`, change it to `UPLOAD_FOLDER=instance/uploads`; uploaded images must not be stored in a public static folder.

Default XAMPP commonly uses user `root` with an empty password, but use the credentials configured on your computer.

## 6. Create the first administrator
Run from the project root:

```powershell
python -m database.seed_admin
```

Enter the admin name, email, and a password of at least 12 characters. The script creates an administrator directly; public registration never offers an admin role.

## 7. Start the website
From the project root:

```powershell
python app.py
```

Open `http://127.0.0.1:5000`.

Register a regular user using **Create an account**. Sign in with the administrator account to see the administrator dashboard. In **User accounts**, an administrator can add accounts, edit account details and access, reset a password, or deactivate/reactivate accounts. Deactivation prevents sign-in but preserves reports and claims. Administrator changes appear in the audit trail.

## 8. How login and role routing work
- `auth/routes.py` receives login and registration forms.
- Passwords are stored as secure password hashes, never plain text.
- `Flask-Login` keeps the authenticated session.
- `redirect_for_role()` sends regular users to `/student/dashboard`, moderators to `/moderator/queue`, and administrators to `/admin/overview`.
- Each blueprint checks the signed-in user's role before showing protected pages.
- Public registration always assigns `role="user"`.

## 9. Where to edit each design
Each screen has a dedicated CSS file:
- Login: `static/css/auth/login.css`
- Registration: `static/css/auth/register.css`
- Student campus board: `static/css/student/dashboard.css`
- Report form: `static/css/student/report_form.css`
- My reports: `static/css/student/my_reports.css`
- AI matches: `static/css/student/matches.css`
- Item detail: `static/css/student/item_detail.css`
- Claim form: `static/css/student/claim.css`
- Recovery tracker: `static/css/student/recovery.css`
- Moderator queue: `static/css/moderator/queue.css`
- Admin overview: `static/css/admin/overview.css`
- Admin users: `static/css/admin/users.css`
- Admin records: `static/css/admin/records.css`
- Audit trail: `static/css/admin/audit.css`

`static/css/base.css` contains shared typography, colors, buttons, sidebar, and responsive layout. Change a page-specific stylesheet for isolated design changes. Change base.css only when you intentionally want a shared change.

## 10. Backend file guide
- `models.py`: database tables and relationships.
- `auth/routes.py`: sign in, register, sign out.
- `student/routes.py`: campus board, reports, claims, matching, recovery.
- `moderator/routes.py`: report and claim review.
- `admin/routes.py`: overview, user roles, records, audit.
- `ai_engine/`: integration point for a real computer-vision model and improved matching.
- `database/seed_admin.py`: secure initial admin creation.

## 11. AI image suggestions
The report form can run a local pretrained YOLOv8 Nano model to detect common objects and suggest an item name and category. The first analysis downloads the `yolov8n.pt` weights unless `AI_MODEL_PATH` points to a local model. This generic model is not trained on OMSU items and may miss uncommon objects; users should check suggestions. It does not identify ownership, serial numbers, or prove that two images show the same item. Read `docs/FEATURES_AND_DEPLOYMENT.md` for feature behavior, privacy, and setup details.

## 12. Before public deployment
The app now includes CSRF protection, login/registration/AI rate limits, secure cookie flags, private upload storage, and baseline security headers. Before public launch, configure HTTPS, a shared Redis rate-limit store, production secrets and database credentials, backups, SMTP, retention/privacy policies, and a production Socket.IO-capable server. Email verification, password recovery, malware scanning, and deployment to a hosting provider are not included yet. Keep `.env`, uploaded private evidence, and model weights out of source control.
