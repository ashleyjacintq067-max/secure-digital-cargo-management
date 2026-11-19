import csv,io
from flask import Blueprint,render_template,Response
from flask_login import login_required
from db import get_db
bp=Blueprint("reports",__name__,url_prefix="/reports")
@bp.route("/")
@login_required
def index():
    rows=get_db().execute("SELECT current_status,COUNT(*) total,SUM(quantity) quantity FROM cargo_records GROUP BY current_status").fetchall()
    return render_template("reports/index.html",rows=rows)
@bp.route("/cargo.csv")
@login_required
def export():
    rows=get_db().execute("SELECT cargo_reference,description,cargo_type,quantity,unit_of_measure,current_status,recorded_at FROM cargo_records ORDER BY recorded_at DESC").fetchall()
    out=io.StringIO(); w=csv.writer(out); w.writerow(["Reference","Description","Type","Quantity","Unit","Status","Recorded at"]); w.writerows([tuple(r) for r in rows])
    return Response("\ufeff"+out.getvalue(),mimetype="text/csv",headers={"Content-Disposition":"attachment; filename=cargo-report.csv"})
