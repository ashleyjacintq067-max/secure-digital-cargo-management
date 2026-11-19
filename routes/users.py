
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from db import get_db
from security import roles_required

bp = Blueprint("users", __name__, url_prefix="/users")


# View all registered accounts
@bp.route("/")
@login_required
@roles_required("admin")
def listing():

    db = get_db()

    users = db.execute("""
        SELECT user_id, username, full_name, role,
               is_active, created_at
        FROM users
        ORDER BY created_at DESC
    """).fetchall()

    return render_template("users/list.html", users=users)


# Create a new account
@bp.route("/create", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def create():

    roles = ["admin", "port_officer", "auditor", "viewer"]

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        full_name = request.form.get("full_name", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        role = request.form.get("role", "")

        if not username or not full_name:
            flash("Please fill in all required fields.", "danger")

        elif role not in roles:
            flash("Invalid user role.", "danger")

        elif len(password) < 12:
            flash("Password must have at least 12 characters.", "danger")

        elif password != confirm_password:
            flash("Passwords do not match.", "danger")

        else:

            db = get_db()

            existing = db.execute(
                "SELECT user_id FROM users WHERE username = ?",
                (username,)
            ).fetchone()

            if existing:
                flash("Username already exists.", "danger")

            else:

                try:

                    password_hash = generate_password_hash(password)

                    cursor = db.execute("""
                        INSERT INTO users
                        (username, full_name, password_hash, role)
                        VALUES (?, ?, ?, ?)
                    """, (
                        username,
                        full_name,
                        password_hash,
                        role
                    ))

                    db.execute("""
                        INSERT INTO audit_logs
                        (user_id, action, entity_type, entity_id, details)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        current_user.user_id,
                        "ACCOUNT_CREATED",
                        "user",
                        cursor.lastrowid,
                        f"Created account for {username}"
                    ))

                    db.commit()

                    flash("User account created successfully!", "success")

                    return redirect(url_for("users.listing"))

                except Exception:
                    db.rollback()
                    flash("Unable to create account.", "danger")

    return render_template("users/create.html", roles=roles)


# Activate or deactivate accounts
@bp.route("/toggle/<int:user_id>", methods=["POST"])
@login_required
@roles_required("admin")
def toggle(user_id):

    if user_id == current_user.user_id:
        flash("You cannot deactivate your own account.", "danger")
        return redirect(url_for("users.listing"))

    db = get_db()

    user = db.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    if user:

        new_status = 0 if user["is_active"] else 1

        db.execute("""
            UPDATE users
            SET is_active = ?
            WHERE user_id = ?
        """, (new_status, user_id))

        db.commit()

        flash("Account status updated.", "success")

    return redirect(url_for("users.listing"))
