from functools import wraps

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
    flash,
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from app.models import User, db


auth_bp = Blueprint("auth", __name__, template_folder="templates")


def admin_required(func):
    """Decorator to protect admin-only views."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Admin login required", "warning")
            return redirect(url_for("admin.login"))
        # Use role or legacy flag for admin check
        if not (getattr(current_user, "role", None) == "admin" or getattr(current_user, "is_admin", False)):
            flash("Access denied", "danger")
            return redirect(url_for("user.index"))
        return func(*args, **kwargs)

    return wrapper


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    User registration page.

    - Checks for duplicate username/email.
    - Stores securely hashed password.
    - Sets default role as "user".
    """
    if current_user.is_authenticated:
        # Already logged in, no need to register again
        return redirect(url_for("user.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Basic validation
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html", username=username, email=email)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html", username=username, email=email)

        # Duplicate checks
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            if existing_user.username == username:
                flash("Username is already taken.", "danger")
            elif existing_user.email == email:
                flash("Email is already registered.", "danger")
            else:
                flash("User already exists.", "danger")
            return render_template("register.html", username=username, email=email)

        # Create new user
        user = User(
            username=username,
            email=email,
            role="user",
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    General user login page.

    - Verifies username/email + password.
    - Creates a Flask-Login session.
    """
    if current_user.is_authenticated:
        return redirect(url_for("user.index"))

    if request.method == "POST":
        identifier = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Allow login via username OR email for convenience
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if user and user.check_password(password):
            login_user(user)

            flash("Logged in successfully.", "success")

            # Redirect admins to admin dashboard, others to user index
            if getattr(user, "role", None) == "admin" or getattr(user, "is_admin", False):
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("user.index"))

        flash("Invalid username/email or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Log out current user and clear session."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("user.index"))
