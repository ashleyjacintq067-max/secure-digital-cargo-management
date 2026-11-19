from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required,current_user
from db import get_db
from security import roles_required
bp=Blueprint("ports",__name__,url_prefix="/ports")
@bp.route("/")
@login_required
def listing(): return render_template("ports/list.html",rows=get_db().execute("SELECT * FROM ports ORDER BY country,port_name").fetchall())
@bp.route("/new",methods=["GET","POST"])
@login_required
@roles_required("admin")
def new():
    if request.method=="POST":
        f=request.form; d=get_db()
        try:
            cur=d.execute("INSERT INTO ports(port_name,country,region,code) VALUES(?,?,?,?)",(f.get("port_name","").strip(),f.get("country","").strip(),f.get("region",""),f.get("code","") or None))
            d.execute("INSERT INTO audit_logs(user_id,action,entity_type,entity_id,details) VALUES(?,?,?,?,?)",(current_user.user_id,"CREATE","port",cur.lastrowid,"Created port")); d.commit(); flash("Port added.","success"); return redirect(url_for("ports.listing"))
        except Exception: d.rollback(); flash("Could not add port; check required fields and unique code.","danger")
    return render_template("ports/form.html")
