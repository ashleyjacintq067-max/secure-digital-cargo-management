from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_user,logout_user,login_required,current_user
from models import User
from db import get_db
bp=Blueprint("auth",__name__,url_prefix="/auth")
@bp.route("/login",methods=["GET","POST"])
def login():
    if current_user.is_authenticated:return redirect(url_for("dashboard.index"))
    if request.method=="POST":
        u=User.authenticate(request.form.get("username","").strip(),request.form.get("password",""))
        if u:
            login_user(u, fresh=True ); d=get_db(); d.execute("INSERT INTO audit_logs(user_id,action,entity_type,details) VALUES(?,?,?,?)",(u.user_id,"LOGIN","user","Successful login")); d.commit()
            return redirect(url_for("dashboard.index"))
        flash("Invalid username or password.","danger")
    return render_template("auth/login.html")
@bp.post("/logout")
@login_required
def logout():
    d=get_db(); d.execute("INSERT INTO audit_logs(user_id,action,entity_type,details) VALUES(?,?,?,?)",(current_user.user_id,"LOGOUT","user","User logged out")); d.commit()
    logout_user(); return redirect(url_for("auth.login"))
