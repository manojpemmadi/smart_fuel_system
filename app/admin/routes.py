from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import User, Blacklist, Detection, db
from app.auth import admin_required
admin_bp = Blueprint("admin", __name__, template_folder="templates")

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"], is_admin=True).first()
        if user and user.check_password(request.form["password"]):
            login_user(user)
            return redirect(url_for("admin.dashboard"))
        flash("Invalid credentials")
    return render_template("admin_login.html")

@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    return render_template(
        "admin_dashboard.html",
        detections=Detection.query.count(),
        blacklist=Blacklist.query.count()
    )

@admin_bp.route("/blacklist", methods=["GET", "POST"])
@login_required
@admin_required
def blacklist():
    if request.method == "POST":
        db.session.add(Blacklist(plate_text=request.form["plate"].upper()))
        db.session.commit()
    return render_template("admin_blacklist.html", items=Blacklist.query.all())

@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("user.index"))

@admin_bp.route("/blacklist/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_blacklist(id):
    item = Blacklist.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("admin.blacklist"))
