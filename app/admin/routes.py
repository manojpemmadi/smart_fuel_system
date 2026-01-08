from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import User, Blacklist, Detection, Vehicle, db
from app.auth import admin_required
from datetime import datetime
admin_bp = Blueprint("admin", __name__, template_folder="templates")

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Admins can log in with username or email
        user = User.query.filter(
            ((User.username == username) | (User.email == username))
            & ((User.role == "admin") | (User.is_admin.is_(True)))
        ).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("admin.dashboard"))

        flash("Invalid admin credentials", "danger")
    return render_template("admin_login.html")

@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    return render_template(
        "admin_dashboard.html",
        detections=Detection.query.count(),
        blacklist=Blacklist.query.count(),
        vehicles=Vehicle.query.count()
    )

@admin_bp.route("/detections")
@login_required
@admin_required
def detections():
    """Display all detection history."""
    all_detections = Detection.query.order_by(Detection.timestamp.desc()).all()
    return render_template("admin_detections.html", data=all_detections)


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


# Vehicle Management Routes (CRUD)
@admin_bp.route("/vehicles")
@login_required
@admin_required
def vehicles():
    """Display all vehicles in a table."""
    all_vehicles = Vehicle.query.order_by(Vehicle.registration_number).all()
    return render_template("admin_vehicles.html", vehicles=all_vehicles)


@admin_bp.route("/vehicles/add", methods=["GET", "POST"])
@login_required
@admin_required
def vehicle_add():
    """Add a new vehicle to the database."""
    if request.method == "POST":
        try:
            # Get form data
            registration_number = request.form.get("registration_number", "").strip().upper().replace(" ", "").replace("-", "")
            owner_name = request.form.get("owner_name", "").strip()
            vehicle_type = request.form.get("vehicle_type", "").strip()
            brand = request.form.get("brand", "").strip()
            model = request.form.get("model", "").strip()
            registration_year = request.form.get("registration_year", "").strip()
            fuel_type = request.form.get("fuel_type", "").strip()
            vehicle_color = request.form.get("vehicle_color", "").strip()
            registration_state = request.form.get("registration_state", "").strip()
            insurance_status = request.form.get("insurance_status", "").strip()
            pollution_cert_status = request.form.get("pollution_cert_status", "").strip()
            blacklist_status = request.form.get("blacklist_status", "No").strip()

            # Validation
            if not registration_number:
                flash("Registration number is required", "error")
                return redirect(url_for("admin.vehicle_add"))
            
            # Check for duplicate registration number
            existing = Vehicle.query.filter_by(registration_number=registration_number).first()
            if existing:
                flash(f"Vehicle with registration number '{registration_number}' already exists", "error")
                return redirect(url_for("admin.vehicle_add"))

            if not all([owner_name, vehicle_type, brand, model, registration_year, fuel_type, vehicle_color, registration_state]):
                flash("All fields are required", "error")
                return redirect(url_for("admin.vehicle_add"))

            try:
                registration_year = int(registration_year)
                if registration_year < 1900 or registration_year > datetime.now().year:
                    flash("Invalid registration year", "error")
                    return redirect(url_for("admin.vehicle_add"))
            except ValueError:
                flash("Registration year must be a valid number", "error")
                return redirect(url_for("admin.vehicle_add"))

            # Create new vehicle
            new_vehicle = Vehicle(
                registration_number=registration_number,
                owner_name=owner_name,
                vehicle_type=vehicle_type,
                brand=brand,
                model=model,
                registration_year=registration_year,
                fuel_type=fuel_type,
                vehicle_color=vehicle_color,
                registration_state=registration_state,
                insurance_status=insurance_status,
                pollution_cert_status=pollution_cert_status,
                blacklist_status=blacklist_status
            )

            db.session.add(new_vehicle)
            db.session.commit()
            flash(f"Vehicle '{registration_number}' added successfully", "success")
            return redirect(url_for("admin.vehicles"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error adding vehicle: {str(e)}", "error")
            return redirect(url_for("admin.vehicle_add"))

    return render_template("admin_vehicle_add.html")


@admin_bp.route("/vehicles/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def vehicle_edit(id):
    """Edit an existing vehicle."""
    vehicle = Vehicle.query.get_or_404(id)

    if request.method == "POST":
        try:
            # Get form data
            registration_number = request.form.get("registration_number", "").strip().upper().replace(" ", "").replace("-", "")
            owner_name = request.form.get("owner_name", "").strip()
            vehicle_type = request.form.get("vehicle_type", "").strip()
            brand = request.form.get("brand", "").strip()
            model = request.form.get("model", "").strip()
            registration_year = request.form.get("registration_year", "").strip()
            fuel_type = request.form.get("fuel_type", "").strip()
            vehicle_color = request.form.get("vehicle_color", "").strip()
            registration_state = request.form.get("registration_state", "").strip()
            insurance_status = request.form.get("insurance_status", "").strip()
            pollution_cert_status = request.form.get("pollution_cert_status", "").strip()
            blacklist_status = request.form.get("blacklist_status", "No").strip()

            # Validation
            if not registration_number:
                flash("Registration number is required", "error")
                return redirect(url_for("admin.vehicle_edit", id=id))

            # Check for duplicate registration number (excluding current vehicle)
            existing = Vehicle.query.filter(
                Vehicle.registration_number == registration_number,
                Vehicle.id != id
            ).first()
            if existing:
                flash(f"Vehicle with registration number '{registration_number}' already exists", "error")
                return redirect(url_for("admin.vehicle_edit", id=id))

            if not all([owner_name, vehicle_type, brand, model, registration_year, fuel_type, vehicle_color, registration_state]):
                flash("All fields are required", "error")
                return redirect(url_for("admin.vehicle_edit", id=id))

            try:
                registration_year = int(registration_year)
                if registration_year < 1900 or registration_year > datetime.now().year:
                    flash("Invalid registration year", "error")
                    return redirect(url_for("admin.vehicle_edit", id=id))
            except ValueError:
                flash("Registration year must be a valid number", "error")
                return redirect(url_for("admin.vehicle_edit", id=id))

            # Update vehicle
            vehicle.registration_number = registration_number
            vehicle.owner_name = owner_name
            vehicle.vehicle_type = vehicle_type
            vehicle.brand = brand
            vehicle.model = model
            vehicle.registration_year = registration_year
            vehicle.fuel_type = fuel_type
            vehicle.vehicle_color = vehicle_color
            vehicle.registration_state = registration_state
            vehicle.insurance_status = insurance_status
            vehicle.pollution_cert_status = pollution_cert_status
            vehicle.blacklist_status = blacklist_status
            vehicle.updated_at = datetime.utcnow()

            db.session.commit()
            flash(f"Vehicle '{registration_number}' updated successfully", "success")
            return redirect(url_for("admin.vehicles"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating vehicle: {str(e)}", "error")
            return redirect(url_for("admin.vehicle_edit", id=id))

    return render_template("admin_vehicle_edit.html", vehicle=vehicle)


@admin_bp.route("/vehicles/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def vehicle_delete(id):
    """Delete a vehicle from the database."""
    vehicle = Vehicle.query.get_or_404(id)
    registration_number = vehicle.registration_number
    
    try:
        db.session.delete(vehicle)
        db.session.commit()
        flash(f"Vehicle '{registration_number}' deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting vehicle: {str(e)}", "error")
    
    return redirect(url_for("admin.vehicles"))
