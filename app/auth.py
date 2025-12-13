from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Admin login required", "warning")
            return redirect(url_for("admin.login"))
        if not current_user.is_admin:
            flash("Access denied", "danger")
            return redirect(url_for("user.index"))
        return func(*args, **kwargs)
    return wrapper
