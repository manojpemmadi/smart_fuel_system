from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from werkzeug.utils import secure_filename
from detect_and_ocr import detect_and_ocr
from app.models import Detection, db
import os, time

user_bp = Blueprint("user", __name__, template_folder="templates")

@user_bp.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@user_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("image")
        if not file or file.filename == "":
            flash("No image selected", "error")
            return redirect(url_for("user.index"))

        filename = secure_filename(file.filename)
        if not allowed_file(filename):
            flash("Invalid file type", "error")
            return redirect(url_for("user.index"))

        path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(path)

        start = time.time()
        results = detect_and_ocr(current_app.config["MODEL_PATH"], path)

        plates = []
        for r in results:
            plates.append({
                "text": r["ocr_text"],
                "ocr_conf": r["ocr_conf"],
                "det_conf": r["det_conf"],
                "box": r["box"]
            })

            db.session.add(Detection(
                text=r["ocr_text"],
                ocr_conf=r["ocr_conf"],
                det_conf=r["det_conf"],
                box_x1=r["box"][0],
                box_y1=r["box"][1],
                box_x2=r["box"][2],
                box_y2=r["box"][3],
                image_name=filename
            ))

        db.session.commit()

        return render_template("user_result.html", plates=plates, image_name=filename, inference_ms=int((time.time() - start) * 1000))

    return render_template("user_index.html")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]
