from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required,current_user
from db import get_db
from security import roles_required
bp=Blueprint("vessels",__name__,url_prefix="/vessels")
@bp.route("/")
@login_required
def listing(): return render_template("vessels/list.html",rows=get_db().execute("SELECT * FROM vessels ORDER BY vessel_name").fetchall())
@bp.route("/new",methods=["GET","POST"])
@login_required
@roles_required("admin","port_officer")
def new():
    if request.method=="POST":
        f=request.form; d=get_db()
        try:
            cur=d.execute("INSERT INTO vessels(vessel_name,vessel_identifier,flag_country) VALUES(?,?,?)",(f.get("vessel_name","").strip(),f.get("vessel_identifier","") or None,f.get("flag_country","")))
            d.execute("INSERT INTO audit_logs(user_id,action,entity_type,entity_id,details) VALUES(?,?,?,?,?)",(current_user.user_id,"CREATE","vessel",cur.lastrowid,"Created vessel")); d.commit(); flash("Vessel added.","success"); return redirect(url_for("vessels.listing"))
        except Exception: d.rollback(); flash("Could not add vessel; check name and unique identifier.","danger")
    return render_template("vessels/form.html")
