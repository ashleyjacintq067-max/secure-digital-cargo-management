# Secure Digital Cargo Management System

A Flask/SQLite academic web application scaffold for regional port cargo records, cargo event history, port and vessel directories, reporting, and audit logs.

## Included
- Login/logout with Werkzeug password hashing and Flask-Login
- Role-based access: admin, port_officer, auditor, viewer
- Cargo create, search/filter, details, edit, event history, admin delete
- Port and vessel directories
- Dashboard totals and recent events
- Cargo summary and CSV export
- Audit log
- SQLite schema, CSRF protection, responsive HTML/CSS and JavaScript

## Run on Windows (VS Code)
1. Extract the ZIP and open the folder in VS Code.
2. `python -m venv .venv`
3. PowerShell: ` .\\.venv\\Scripts\\Activate.ps1 `; if blocked, use Command Prompt and run `.venv\\Scripts\\activate.bat`.
4. `python -m pip install -r requirements.txt`
5. `flask --app app init-db`
6. `flask --app app create-admin` (create a unique username and password of at least 8 
\characters).
7. `python app.py`
8. Open http://127.0.0.1:5000/

After login, add ports and vessels, then create cargo records. Cargo detail pages let authorized users add events.

## Roles
- admin: cargo and port administration, delete cargo, audit access
- port_officer: cargo and vessel operations
- auditor: read-only pages and audit log
- viewer: read-only pages

## Deployment warning
This is a functional academic/demo foundation, not a certified production port platform. Before real use, configure a strong SECRET_KEY via environment variables, enable HTTPS and COOKIE_SECURE=1, run with a production WSGI server, add account-management/password-reset/rate-limiting workflows, test authorization and backups, and arrange security review. Do not use real operational or sensitive cargo data until authorized and reviewed.
