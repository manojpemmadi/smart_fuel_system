import os

class Config:
    # Security
    SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-key-change-in-production")

    # Database (SQLite)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File upload settings
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024   # 10 MB
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "webp"}

    # YOLO model path (your best.pt stays in root folder)
    MODEL_PATH = os.environ.get("MODEL_PATH", os.path.join(BASE_DIR, "best.pt"))

    # Rate limiting (optional)
    RATELIMIT_DEFAULT = "20/minute"

    # Upload folder for temporary image saving if needed
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    # Vehicle age restrictions (for pollution control)
    MAX_VEHICLE_AGE_YEARS = int(os.environ.get("MAX_VEHICLE_AGE_YEARS", "10"))  # Default: 10 years
