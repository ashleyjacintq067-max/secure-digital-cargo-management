import os
from pathlib import Path
BASE = Path(__file__).resolve().parent
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "local-development-key-change-before-deployment")
    DATABASE = os.environ.get("DATABASE_PATH", str(BASE / "instance" / "cargo.db"))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "0") == "1"
