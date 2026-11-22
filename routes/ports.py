from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from db import get_db
from security import roles_required

bp = Blueprint("ports", __name__, url_prefix="/ports")


@bp.route("/")
@login_required
def listing():
    rows = get_db().execute(
        "SELECT rowid AS pid, * FROM ports ORDER BY country, port_name"
    ).fetchall()
    return render_template("ports/list.html", rows=rows)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def new():
    if request.method == "POST":
        f = request.form
        d = get_db()
        try:
            cur = d.execute(
                "INSERT INTO ports(port_name,country,region,code) VALUES(?,?,?,?)",
                (f.get("port_name", "").strip(), f.get("country", "").strip(),
                 f.get("region", ""), f.get("code", "") or None),
            )
            d.execute(
                "INSERT INTO audit_logs(user_id,action,entity_type,entity_id,details) VALUES(?,?,?,?,?)",
                (current_user.user_id, "CREATE", "port", cur.lastrowid, "Created port"),
            )
            d.commit()
            flash("Port added.", "success")
            return redirect(url_for("ports.listing"))
        except Exception:
            d.rollback()
            flash("Could not add port; check required fields and unique code.", "danger")
    return render_template("ports/form.html")


@bp.route("/<int:pid>/edit", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def edit(pid):
    d = get_db()
    port = d.execute(
        "SELECT rowid AS pid, * FROM ports WHERE rowid=?", (pid,)
    ).fetchone()
    if not port:
        abort(404)

    if request.method == "POST":
        f = request.form
        try:
            d.execute(
                "UPDATE ports SET port_name=?, country=?, region=?, code=? WHERE rowid=?",
                (f.get("port_name", "").strip(), f.get("country", "").strip(),
                 f.get("region", ""), f.get("code", "") or None, pid),
            )
            d.execute(
                "INSERT INTO audit_logs(user_id,action,entity_type,entity_id,details) VALUES(?,?,?,?,?)",
                (current_user.user_id, "UPDATE", "port", pid, "Updated port"),
            )
            d.commit()
            flash("Port updated.", "success")
            return redirect(url_for("ports.listing"))
        except Exception:
            d.rollback()
            flash("Could not update port; check required fields and unique code.", "danger")

    return render_template("ports/form.html", port=port)