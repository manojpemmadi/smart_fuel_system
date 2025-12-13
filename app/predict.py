from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from detect_and_ocr import detect_and_ocr
from app.models import Detection, db
import os, time

predict_bp = Blueprint("predict", __name__)

@predict_bp.route("/predict", methods=["POST"])
def predict():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No image"}), 400

    filename = secure_filename(file.filename)
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

    return jsonify({
        "plates": plates,
        "inference_ms": int((time.time() - start) * 1000)
    })
