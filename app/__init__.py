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
    from app.models import db, User

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create tables and ensure a default admin user exists
    with app.app_context():
        db.create_all()

        # Create default admin user if it doesn't exist yet
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                role="admin",
                is_admin=True,  # keep legacy flag true
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

        # Create sample vehicle for demonstration (SN66 XMZ)
        from app.models import Vehicle
        sample_vehicle = Vehicle.query.filter_by(registration_number="SN66XMZ").first()
        if not sample_vehicle:
            sample_vehicle = Vehicle(
                registration_number="SN66XMZ",
                owner_name="Ramesh Kumar",
                vehicle_type="Car",
                brand="Maruti Suzuki",
                model="Baleno",
                registration_year=2017,
                fuel_type="Petrol",
                vehicle_color="White",
                registration_state="Telangana",
                insurance_status="Valid",
                pollution_cert_status="Valid",
                blacklist_status="No"
            )
            db.session.add(sample_vehicle)
            db.session.commit()

    # Register blueprints
    from app.user.routes import user_bp
    from app.admin.routes import admin_bp
    from app.predict import predict_bp
    from app.auth import auth_bp

    app.register_blueprint(user_bp, url_prefix="/")
    app.register_blueprint(auth_bp, url_prefix="/")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(predict_bp, url_prefix="/api")

    return app
