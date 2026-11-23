"""Loads demo data when the database has no cargo records.
Render's free plan resets the database on every restart, so this refills it.
The five demo users always use the current DEMO_PASSWORD."""
import os
from werkzeug.security import generate_password_hash

USERS = [
    ("grace.wanjiku", "Grace Wanjiku", "port_officer"),
    ("brian.otieno", "Brian Otieno", "port_officer"),
    ("amina.hassan", "Amina Hassan", "auditor"),
    ("david.kimani", "David Kimani", "viewer"),
    ("faith.achieng", "Faith Achieng", "viewer"),
]

PORTS = [
    ("Mombasa", "Kenya", "Coast", "KEMBA"),
    ("Dar es Salaam", "Tanzania", "Coast", "TZDAR"),
    ("Djibouti", "Djibouti", "Horn of Africa", "DJJIB"),
    ("Berbera", "Somalia", "Horn of Africa", "SOBBO"),
    ("Beira", "Mozambique", "Sofala", "MZBEW"),
]

VESSELS = [
    ("MV Pwani Star", "DEMO-001", "Kenya"),
    ("MV Indian Ocean Trader", "DEMO-002", "Tanzania"),
    ("MV Horn Express", "DEMO-003", "Panama"),
    ("MV Red Sea Carrier", "DEMO-004", "Liberia"),
    ("MV Sofala Pride", "DEMO-005", "Mozambique"),
]

# reference, description, type, quantity, unit, origin code, destination code,
# vessel identifier, status, notes
CARGO = [
    ("CRG-101", "Tea, bagged for export", "Food", 120, "tons", "KEMBA", "DJJIB",
     "DEMO-001", "recorded", "Export-grade tea, bagged and palletised. Handle with care."),
    ("CRG-102", "Construction steel bars", "Construction", 300, "tons", "TZDAR", "KEMBA",
     "DEMO-002", "in_transit", "Heavy load. Crane required at the destination port."),
    ("CRG-103", "Medical supplies", "Medical", 45, "pallets", "DJJIB", "KEMBA",
     "DEMO-003", "at_port", "Keep dry and shaded. Priority clearance."),
    ("CRG-104", "Cooking oil in drums", "Food", 800, "drums", "SOBBO", "TZDAR",
     "DEMO-004", "inspected", "Check drums for leaks before loading."),
    ("CRG-105", "Vehicle spare parts", "Machinery", 60, "crates", "MZBEW", "KEMBA",
     "DEMO-005", "delivered", "Fragile crates. Do not stack more than two high."),
]

# cargo reference, port code, event type, details
EVENTS = [
    ("CRG-101", "KEMBA", "cargo_registered", "Cargo registered at origin port."),
    ("CRG-102", "TZDAR", "loaded_on_vessel", "Steel bars loaded onto MV Indian Ocean Trader."),
    ("CRG-102", "TZDAR", "departed_port", "Vessel departed for Mombasa."),
    ("CRG-103", "KEMBA", "arrived_at_port", "Medical supplies arrived and awaiting clearance."),
    ("CRG-104", "SOBBO", "inspection_completed", "Drums inspected, no leaks found."),
    ("CRG-105", "KEMBA", "delivered", "Delivered to consignee."),
]


def seed_demo(db):
    password = os.environ.get("DEMO_PASSWORD", "")
    if len(password) < 12:
        return "skipped: DEMO_PASSWORD not set (12+ characters needed)"

    pw_hash = generate_password_hash(password)

    # Always make sure existing demo accounts use the current DEMO_PASSWORD
    reset = 0
    for username, _name, _role in USERS:
        cur = db.execute(
            "UPDATE users SET password_hash=?, is_active=1 WHERE username=?",
            (pw_hash, username),
        )
        reset += cur.rowcount
    db.commit()

    if db.execute("SELECT COUNT(*) FROM cargo_records").fetchone()[0] > 0:
        return "skipped: data already present (demo passwords reset: %d)" % reset

    for username, full_name, role in USERS:
        db.execute(
            "INSERT OR IGNORE INTO users(username, full_name, password_hash, role) "
            "VALUES(?,?,?,?)",
            (username, full_name, pw_hash, role),
        )

    for row in PORTS:
        db.execute(
            "INSERT OR IGNORE INTO ports(port_name, country, region, code) "
            "VALUES(?,?,?,?)",
            row,
        )

    for row in VESSELS:
        db.execute(
            "INSERT OR IGNORE INTO vessels(vessel_name, vessel_identifier, flag_country) "
            "VALUES(?,?,?)",
            row,
        )

    def one(sql, params):
        r = db.execute(sql, params).fetchone()
        return r[0] if r else None

    def port_id(code):
        return one("SELECT port_id FROM ports WHERE code=?", (code,))

    def vessel_id(ident):
        return one("SELECT vessel_id FROM vessels WHERE vessel_identifier=?", (ident,))

    officer = one("SELECT user_id FROM users WHERE username=?", ("grace.wanjiku",))

    new_refs = set()
    for ref, desc, ctype, qty, unit, o_code, d_code, v_ident, status, notes in CARGO:
        cur = db.execute(
            "INSERT OR IGNORE INTO cargo_records("
            "cargo_reference, description, cargo_type, quantity, unit_of_measure, "
            "origin_port_id, destination_port_id, vessel_id, recorded_by, "
            "current_status, notes) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (
                ref, desc, ctype, qty, unit,
                port_id(o_code), port_id(d_code), vessel_id(v_ident),
                officer, status, notes,
            ),
        )
        if cur.rowcount == 1:
            new_refs.add(ref)

    for ref, code, etype, details in EVENTS:
        if ref in new_refs:
            cid = one(
                "SELECT cargo_id FROM cargo_records WHERE cargo_reference=?",
                (ref,),
            )
            db.execute(
                "INSERT INTO cargo_events("
                "cargo_id, port_id, event_type, details, recorded_by) "
                "VALUES(?,?,?,?,?)",
                (cid, port_id(code), etype, details, officer),
            )

    if new_refs:
        db.execute(
            "INSERT INTO audit_logs(user_id, action, entity_type, details) "
            "VALUES(NULL, 'SEED', 'system', 'Demo data loaded')"
        )

    db.commit()
    return "demo data loaded"
