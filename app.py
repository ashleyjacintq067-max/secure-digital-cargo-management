import os
from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from config import Config
from db import close_db, init_db
from models import User
login_manager=LoginManager(); login_manager.login_view="auth.login"
csrf=CSRFProtect()
def create_app():
    app=Flask(__name__); app.config.from_object(Config)
    login_manager.init_app(app); csrf.init_app(app); app.teardown_appcontext(close_db)
    @login_manager.user_loader
    def load_user(uid): return User.get(uid)
    from routes.auth import bp as auth
    from routes.dashboard import bp as dashboard
    from routes.cargo import bp as cargo
    from routes.ports import bp as ports
    from routes.vessels import bp as vessels
    from routes.reports import bp as reports
    from routes.audit import bp as audit
    for b in (auth,dashboard,cargo,ports,vessels,reports,audit): app.register_blueprint(b)
    @app.route("/")
    def home(): return redirect(url_for("dashboard.index") if current_user.is_authenticated else url_for("auth.login"))
    @app.errorhandler(403)
    def forbidden(e): return render_template("errors/403.html"),403
    @app.errorhandler(404)
    def missing(e): return render_template("errors/404.html"),404
    @app.cli.command("init-db")
    def init_command(): init_db(); print("Database initialized.")
    @app.cli.command("create-admin")
    def create_admin():
        from getpass import getpass
        from werkzeug.security import generate_password_hash
        from db import get_db
        u=input("Admin username: ").strip(); n=input("Full name: ").strip(); p=getpass("Password (8+ characters): ")
        if len(p)<8: print("Password too short."); return
        d=get_db()
        try:
            d.execute("INSERT INTO users(username,full_name,password_hash,role) VALUES(?,?,?,?)",(u,n,generate_password_hash(p),"admin")); d.commit(); print("Admin created.")
        except Exception as e: d.rollback(); print("Could not create admin:",e)
    return app
app=create_app()
if __name__=="__main__": app.run(debug=os.environ.get("FLASK_DEBUG")=="1")
