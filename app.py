import os

from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash

from config import Config
from db import close_db, init_db, get_db
from models import User


login_manager = LoginManager()
login_manager.login_view = "auth.login"

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    login_manager.init_app(app)
    csrf.init_app(app)
    app.teardown_appcontext(close_db)

    @login_manager.user_loader
    def load_user(uid):
        return User.get(uid)

    from routes.auth import bp as auth
    from routes.dashboard import bp as dashboard
    from routes.cargo import bp as cargo
    from routes.ports import bp as ports
    from routes.vessels import bp as vessels
    from routes.reports import bp as reports
    from routes.audit import bp as audit
    from routes.users import bp as users

    for b in (auth, dashboard, cargo, ports, vessels, reports, audit, users):
        app.register_blueprint(b)

    @app.route("/")
    def home():
        return redirect(
            url_for("dashboard.index")
            if current_user.is_authenticated
            else url_for("auth.login")
        )

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def missing(e):
        return render_template("errors/404.html"), 404

    @app.cli.command("init-db")
    def init_command():
        init_db()
        print("Database initialized.")

    @app.cli.command("create-admin")
    def create_admin():
        from getpass import getpass

        u = input("Admin username: ").strip()
        n = input("Full name: ").strip()
        p = getpass("Password (8+ characters): ")

        if len(p) < 8:
            print("Password too short.")
            return

        d = get_db()

        try:
            d.execute(
                """INSERT INTO users
                (username, full_name, password_hash, role)
                VALUES (?, ?, ?, ?)""",
                (u, n, generate_password_hash(p), "admin")
            )
            d.commit()
            print("Admin created.")
        except Exception:
            d.rollback()
            print("Could not create admin. Check whether the username already exists.")

    @app.cli.command("create-admin-from-env")
    def create_admin_from_env():
        username = os.environ.get("ADMIN_USERNAME", "").strip()
        full_name = os.environ.get("ADMIN_FULL_NAME", "").strip()
        password = os.environ.get("ADMIN_PASSWORD", "")

        if not username or not full_name or not password:
            raise RuntimeError(
                "Set ADMIN_USERNAME, ADMIN_FULL_NAME and ADMIN_PASSWORD."
            )

        if len(password) < 12:
            raise RuntimeError("ADMIN_PASSWORD must be at least 12 characters.")

        d = get_db()

        existing = d.execute(
            "SELECT user_id FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if existing:
            print("Administrator already exists. No changes made.")
            return

        try:
            d.execute(
                """INSERT INTO users
                (username, full_name, password_hash, role)
                VALUES (?, ?, ?, ?)""",
                (
                    username,
                    full_name,
                    generate_password_hash(password),
                    "admin"
                )
            )
            d.commit()
            print("Administrator account created successfully.")

        except Exception:
            d.rollback()
            raise RuntimeError("Administrator account creation failed.")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")