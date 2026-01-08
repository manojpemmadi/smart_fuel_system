from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, current_app, send_from_directory
)
from werkzeug.utils import secure_filename
from app.models import Detection, db
from app.services.ocr_service import run_ocr
from app.services.vehicle_service import check_vehicle_status
from config import Config
import os, time

user_bp = Blueprint(
    "user",
    __name__,
    template_folder="templates"
)

@user_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("image")

        if not file or file.filename == "":
            flash("No image selected", "error")
            return redirect(url_for("user.index"))

        if not allowed_file(file.filename):
            flash("Invalid file type", "error")
            return redirect(url_for("user.index"))

        filename = secure_filename(file.filename)
        upload_dir = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_dir, exist_ok=True)

        image_path = os.path.join(upload_dir, filename)
        file.save(image_path)

        start = time.time()
        results = run_ocr(image_path)

        plates = []
        vehicle_statuses = []
        
        for r in results:
            plates.append(r)

            db.session.add(Detection(
                text=r["text"],
                ocr_conf=r["ocr_conf"],
                det_conf=r["det_conf"],
                box_x1=r["box"][0],
                box_y1=r["box"][1],
                box_x2=r["box"][2],
                box_y2=r["box"][3],
                image_name=filename
            ))
            
            # Query vehicle database for each detected plate
            max_age = getattr(Config, 'MAX_VEHICLE_AGE_YEARS', 10)
            status = check_vehicle_status(r["text"], max_age_years=max_age)
            vehicle_statuses.append(status)

        db.session.commit()

        return render_template(
            "user_result.html",
            plates=plates,
            vehicle_statuses=vehicle_statuses,
            image_name=filename,
            inference_ms=int((time.time() - start) * 1000),
            max_age_years=getattr(Config, 'MAX_VEHICLE_AGE_YEARS', 10)
        )

    return render_template("user_index.html")


@user_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@user_bp.route('/vehicle/<registration_number>')
def vehicle_details(registration_number):
    """
    Display complete vehicle details page.
    """
    from app.services.vehicle_service import get_vehicle_by_plate
    
    vehicle = get_vehicle_by_plate(registration_number)
    
    if not vehicle:
        flash(f"Vehicle with registration number '{registration_number}' not found in database.", "error")
        return redirect(url_for("user.index"))
    
    max_age = getattr(Config, 'MAX_VEHICLE_AGE_YEARS', 10)
    vehicle_age = vehicle.calculate_age()
    is_old = vehicle.is_old_vehicle(max_age)
    is_blacklisted = vehicle.is_blacklisted()
    
    return render_template(
        "vehicle_details.html",
        vehicle=vehicle,
        vehicle_age=vehicle_age,
        is_old=is_old,
        is_blacklisted=is_blacklisted,
        max_age_years=max_age
    )


def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )
