from flask import Blueprint,render_template
from flask_login import login_required
from db import get_db
from security import roles_required
bp=Blueprint("audit",__name__,url_prefix="/audit")
@bp.route("/")
@login_required
@roles_required("admin","auditor")
def index():
    rows=get_db().execute("SELECT a.*,u.username FROM audit_logs a LEFT JOIN users u ON u.user_id=a.user_id ORDER BY a.created_at DESC LIMIT 250").fetchall()
    return render_template("audit/index.html",rows=rows)
