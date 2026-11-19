from flask import Blueprint,render_template,request,redirect,url_for,flash,abort
from flask_login import login_required,current_user
from db import get_db
from security import roles_required
bp=Blueprint("cargo",__name__,url_prefix="/cargo")
STATUSES=["recorded","inspected","in_transit","at_port","delivered","on_hold"]
def audit(d,action,cid,details): d.execute("INSERT INTO audit_logs(user_id,action,entity_type,entity_id,details) VALUES(?,?,?,?,?)",(current_user.user_id,action,"cargo",cid,details))
@bp.route("/")
@login_required
def listing():
    d=get_db(); q=request.args.get("q","").strip(); s=request.args.get("status","")
    sql="SELECT c.*,o.port_name origin,dst.port_name destination,v.vessel_name FROM cargo_records c LEFT JOIN ports o ON o.port_id=c.origin_port_id LEFT JOIN ports dst ON dst.port_id=c.destination_port_id LEFT JOIN vessels v ON v.vessel_id=c.vessel_id WHERE (c.cargo_reference LIKE ? OR c.description LIKE ?)"
    args=[f"%{q}%",f"%{q}%"]
    if s in STATUSES: sql+=" AND c.current_status=?"; args.append(s)
    rows=d.execute(sql+" ORDER BY c.recorded_at DESC",args).fetchall()
    return render_template("cargo/list.html",rows=rows,q=q,status=s,statuses=STATUSES)
@bp.route("/new",methods=["GET","POST"])
@login_required
@roles_required("admin","port_officer")
def new():
    d=get_db()
    if request.method=="POST":
        f=request.form
        try: qty=float(f.get("quantity","")); assert qty>=0
        except Exception: qty=-1
        if not f.get("cargo_reference","").strip() or not f.get("description","").strip() or qty<0:
            flash("Enter a reference, description and valid quantity.","danger")
        else:
            try:
                c=d.execute("INSERT INTO cargo_records(cargo_reference,description,cargo_type,quantity,unit_of_measure,origin_port_id,destination_port_id,vessel_id,recorded_by,current_status,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (f["cargo_reference"].strip(),f["description"].strip(),f.get("cargo_type",""),qty,f.get("unit_of_measure","units"),f.get("origin_port_id") or None,f.get("destination_port_id") or None,f.get("vessel_id") or None,current_user.user_id,f.get("current_status","recorded"),f.get("notes","")))
                cid=c.lastrowid
                d.execute("INSERT INTO cargo_events(cargo_id,port_id,event_type,details,recorded_by) VALUES(?,?,?,?,?)",(cid,f.get("origin_port_id") or None,"cargo_recorded","Initial cargo record created",current_user.user_id))
                audit(d,"CREATE",cid,"Created cargo "+f["cargo_reference"]); d.commit(); flash("Cargo record saved.","success"); return redirect(url_for("cargo.listing"))
            except Exception: d.rollback(); flash("Could not save record. Check unique reference and selected values.","danger")
    return render_template("cargo/form.html",record=None,ports=d.execute("SELECT * FROM ports").fetchall(),vessels=d.execute("SELECT * FROM vessels").fetchall(),statuses=STATUSES)
@bp.route("/<int:cid>")
@login_required
def detail(cid):
    d=get_db(); r=d.execute("SELECT c.*,o.port_name origin,dst.port_name destination,v.vessel_name FROM cargo_records c LEFT JOIN ports o ON o.port_id=c.origin_port_id LEFT JOIN ports dst ON dst.port_id=c.destination_port_id LEFT JOIN vessels v ON v.vessel_id=c.vessel_id WHERE c.cargo_id=?",(cid,)).fetchone()
    if not r: abort(404)
    ev=d.execute("SELECT e.*,p.port_name,u.username FROM cargo_events e LEFT JOIN ports p ON p.port_id=e.port_id LEFT JOIN users u ON u.user_id=e.recorded_by WHERE e.cargo_id=? ORDER BY e.event_time DESC",(cid,)).fetchall()
    return render_template("cargo/detail.html",r=r,events=ev,ports=d.execute("SELECT * FROM ports").fetchall())
@bp.route("/<int:cid>/edit",methods=["GET","POST"])
@login_required
@roles_required("admin","port_officer")
def edit(cid):
    d=get_db(); r=d.execute("SELECT * FROM cargo_records WHERE cargo_id=?",(cid,)).fetchone()
    if not r: abort(404)
    if request.method=="POST":
        f=request.form
        try:
            qty=float(f.get("quantity","")); assert qty>=0
            d.execute("UPDATE cargo_records SET description=?,cargo_type=?,quantity=?,unit_of_measure=?,origin_port_id=?,destination_port_id=?,vessel_id=?,current_status=?,notes=?,updated_at=CURRENT_TIMESTAMP WHERE cargo_id=?",(f["description"].strip(),f.get("cargo_type",""),qty,f.get("unit_of_measure","units"),f.get("origin_port_id") or None,f.get("destination_port_id") or None,f.get("vessel_id") or None,f.get("current_status","recorded"),f.get("notes",""),cid))
            audit(d,"UPDATE",cid,"Updated cargo record"); d.commit(); flash("Cargo updated.","success"); return redirect(url_for("cargo.detail",cid=cid))
        except Exception: d.rollback(); flash("Invalid quantity or record values.","danger")
    return render_template("cargo/form.html",record=r,ports=d.execute("SELECT * FROM ports").fetchall(),vessels=d.execute("SELECT * FROM vessels").fetchall(),statuses=STATUSES)
@bp.post("/<int:cid>/events")
@login_required
@roles_required("admin","port_officer")
def add_event(cid):
    d=get_db()
    if not d.execute("SELECT cargo_id FROM cargo_records WHERE cargo_id=?",(cid,)).fetchone(): abort(404)
    f=request.form; typ=f.get("event_type","").strip()
    if not typ: flash("Event type is required.","danger")
    else:
        d.execute("INSERT INTO cargo_events(cargo_id,port_id,event_type,details,recorded_by) VALUES(?,?,?,?,?)",(cid,f.get("port_id") or None,typ,f.get("details",""),current_user.user_id)); audit(d,"ADD_EVENT",cid,"Added event "+typ); d.commit(); flash("Event added.","success")
    return redirect(url_for("cargo.detail",cid=cid))
@bp.post("/<int:cid>/delete")
@login_required
@roles_required("admin")
def delete(cid):
    d=get_db(); r=d.execute("SELECT cargo_reference FROM cargo_records WHERE cargo_id=?",(cid,)).fetchone()
    if r: audit(d,"DELETE",cid,"Deleted "+r["cargo_reference"]); d.execute("DELETE FROM cargo_records WHERE cargo_id=?",(cid,)); d.commit(); flash("Cargo deleted.","success")
    return redirect(url_for("cargo.listing"))
