from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    Application user model.

    Fields (for project requirements):
    - id
    - username
    - email
    - password_hash
    - role

    We also keep a legacy `password` and `is_admin` column to stay compatible
    with the existing code/database, but new code should use `password_hash`
    and `role`.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # New, explicit password hash field for security
    password_hash = db.Column(db.String(200), nullable=False)

    # Role: "user" (default) or "admin"
    role = db.Column(db.String(20), default="user", nullable=False)

    # Legacy fields kept for backward compatibility
    password = db.Column(db.String(200))  # previously used for password hash
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password: str) -> None:
        """Hash and store the password safely."""
        hashed = generate_password_hash(password)
        self.password_hash = hashed

        # Keep legacy column in sync so existing code/db continues to work
        self.password = hashed

    def check_password(self, password: str) -> bool:
        """
        Verify a plain-text password against the stored hash.
        Falls back to the legacy `password` column if needed.
        """
        if self.password_hash:
            return check_password_hash(self.password_hash, password)
        if self.password:
            return check_password_hash(self.password, password)
        return False

    @property
    def is_admin_user(self) -> bool:
        """Semantic helper for checking admin role."""
        return self.role == "admin" or bool(self.is_admin)

    def __repr__(self):
        return f"<User {self.username}>"

class Blacklist(db.Model):
    __tablename__ = "blacklist"

    id = db.Column(db.Integer, primary_key=True)
    plate_text = db.Column(db.String(20), unique=True, nullable=False)

    def __repr__(self):
        return f"<Blacklist {self.plate_text}>"

class Detection(db.Model):
    __tablename__ = "detections"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(20), nullable=False)
    ocr_conf = db.Column(db.Float, nullable=False)
    det_conf = db.Column(db.Float, nullable=False)
    box_x1 = db.Column(db.Integer, nullable=False)
    box_y1 = db.Column(db.Integer, nullable=False)
    box_x2 = db.Column(db.Integer, nullable=False)
    box_y2 = db.Column(db.Integer, nullable=False)
    image_name = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Detection {self.text}>"
