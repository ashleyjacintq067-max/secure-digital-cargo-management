from flask import Blueprint,render_template
from flask_login import login_required
from db import get_db
bp=Blueprint("dashboard",__name__,url_prefix="/dashboard")
@bp.route("/")
@login_required
def index():
    d=get_db()
    total=d.execute("SELECT COUNT(*) n FROM cargo_records").fetchone()["n"]
    ports=d.execute("SELECT COUNT(*) n FROM ports").fetchone()["n"]
    vessels=d.execute("SELECT COUNT(*) n FROM vessels").fetchone()["n"]
    statuses=d.execute("SELECT current_status,COUNT(*) total FROM cargo_records GROUP BY current_status").fetchall()
    recent=d.execute("SELECT c.*,p.port_name origin_port FROM cargo_records c LEFT JOIN ports p ON p.port_id=c.origin_port_id ORDER BY c.recorded_at DESC LIMIT 8").fetchall()
    events=d.execute("SELECT e.*,c.cargo_reference,p.port_name,u.username FROM cargo_events e JOIN cargo_records c ON c.cargo_id=e.cargo_id LEFT JOIN ports p ON p.port_id=e.port_id LEFT JOIN users u ON u.user_id=e.recorded_by ORDER BY e.event_time DESC LIMIT 6").fetchall()
    return render_template("dashboard.html",total=total,ports=ports,vessels=vessels,statuses=statuses,recent=recent,events=events)
