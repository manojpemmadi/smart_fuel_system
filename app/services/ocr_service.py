# app/services/ocr_service.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from detect_and_ocr import detect_and_ocr

def run_ocr(image_path, model_path=None, conf_thresh=0.35):
    """
    Wrapper function for OCR processing
    """
    if model_path is None:
        # Default model path
        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "best.pt")

    results = detect_and_ocr(
        model_path=model_path,
        image_path=image_path,
        conf_thresh=conf_thresh
    )

    # Transform results to match expected format
    formatted_results = []
    for result in results:
        formatted_results.append({
            "text": result["ocr_text"],
            "ocr_conf": result["ocr_conf"],
            "det_conf": result["det_conf"],
            "box": result["box"]
        })

    return formatted_results