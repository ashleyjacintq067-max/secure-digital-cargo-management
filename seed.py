"""Loads demo data when the database is empty.
Render's free plan resets the database on every restart, so this refills it."""
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

    if db.execute("SELECT COUNT(*) FROM ports").fetchone()[0] > 0:
        return "skipped: data already present"

    pw_hash = generate_password_hash(password)

    for username, full_name, role in USERS:
        db.execute(
            "INSERT OR IGNORE INTO users(username, full_name, password_hash, role) "