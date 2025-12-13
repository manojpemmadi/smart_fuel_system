from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

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
