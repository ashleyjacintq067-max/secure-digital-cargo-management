from flask_login import UserMixin
from werkzeug.security import check_password_hash
from db import get_db


class User(UserMixin):
    def __init__(self, row):
        self.id = str(row["user_id"])
        self.user_id = row["user_id"]
        self.username = row["username"]
        self.full_name = row["full_name"]
        self.role = row["role"]
        self._active = bool(row["is_active"])

    @property
    def is_active(self):
        return self._active

    @staticmethod
    def get(uid):
        r = get_db().execute(
            "SELECT * FROM users WHERE user_id=?", (uid,)
        ).fetchone()
        return User(r) if r else None

    @staticmethod
    def authenticate(username, password):
        r = get_db().execute(
            "SELECT * FROM users WHERE username=? AND is_active=1", (username,)
        ).fetchone()
        if r and check_password_hash(r["password_hash"], password):
            return User(r)
        return None