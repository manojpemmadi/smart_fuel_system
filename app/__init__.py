from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Import db from models
    from app.models import db

    db.init_app(app)
    login_manager.init_app(app)

    # Import models AFTER db init
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create tables
    with app.app_context():
        db.create_all()
        # Create default admin user
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", is_admin=True)
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

    # Register blueprints
    from app.user.routes import user_bp
    from app.admin.routes import admin_bp
    from app.predict import predict_bp

    app.register_blueprint(user_bp, url_prefix="/")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(predict_bp, url_prefix="/api")

    return app
