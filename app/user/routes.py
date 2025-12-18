from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, current_app, send_from_directory
)
from werkzeug.utils import secure_filename
from app.models import Detection, db
from app.services.ocr_service import run_ocr
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

        db.session.commit()

        return render_template(
            "user_result.html",
            plates=plates,
            image_name=filename,
            inference_ms=int((time.time() - start) * 1000)
        )

    return render_template("user_index.html")


@user_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )
