# detect_and_ocr.py
import argparse
import cv2
import numpy as np
from ultralytics import YOLO
import easyocr
import torch
import sys
import json

def detect_and_ocr(
    model_path: str,
    image_path: str,
    conf_thresh: float = 0.35,
    allowlist: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789- ",
    resize_for_ocr: bool = True,
    ocr_langs: list = ['en'],
    imgsz: int = 1280
):
    """
    Detect plates with YOLO, crop in-memory, run EasyOCR and print results.
    Returns list of dicts: {"crop_idx", "det_conf","ocr_text","ocr_conf","box":[x1,y1,x2,y2]}
    """
    # 1) read image
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")
    img_h, img_w = img_bgr.shape[:2]

    # 2) load YOLO model
    model = YOLO(model_path)
    model.overrides = {"conf": conf_thresh}

    # 3) inference
    results = model(img_bgr, imgsz=imgsz)  # single-image call
    if len(results) == 0:
        print("No results returned by model.")
        return []

    res = results[0]

    # 4) parse boxes and confidences robustly
    boxes = []
    confs = []
    try:
        if hasattr(res, "boxes") and res.boxes is not None:
            # prefer xyxy attribute
            if hasattr(res.boxes, "xyxy"):
                raw = res.boxes.xyxy.cpu().numpy()
                if raw.size == 0:
                    raw = np.empty((0,4))
                if raw.ndim == 2 and raw.shape[1] >= 4:
                    # If conf included
                    if raw.shape[1] >= 5:
                        boxes = raw[:, :4].astype(int).tolist()
                        confs = raw[:, 4].astype(float).tolist()
                    else:
                        boxes = raw[:, :4].astype(int).tolist()
                        try:
                            confs = res.boxes.conf.cpu().numpy().astype(float).tolist()
                        except Exception:
                            confs = [1.0] * len(boxes)
            else:
                # fallback to boxes.data
                raw = res.boxes.data.cpu().numpy()
                if raw.size > 0:
                    boxes = raw[:, :4].astype(int).tolist()
                    confs = raw[:, 4].astype(float).tolist() if raw.shape[1] >= 5 else [1.0]*len(boxes)
    except Exception as e:
        print("Error parsing detection results:", e)
        return []

    # 5) filter by conf_thresh and clamp boxes
    valid = []
    for i, b in enumerate(boxes):
        det_conf = float(confs[i]) if i < len(confs) else 1.0
        if det_conf >= conf_thresh:
            x1, y1, x2, y2 = b
            x1, y1 = max(0, int(x1)), max(0, int(y1))
            x2, y2 = min(img_w - 1, int(x2)), min(img_h - 1, int(y2))
            if x2 > x1 and y2 > y1:
                valid.append((i, (x1, y1, x2, y2), det_conf))

    if len(valid) == 0:
        print("No detections above confidence threshold.")
        return []

    # 6) EasyOCR reader (gpu if available)
    use_gpu = torch.cuda.is_available()
    reader = easyocr.Reader(ocr_langs, gpu=use_gpu)
    # NOTE: first run may download models (one-time).

    results_list = []
    for crop_idx, (orig_idx, (x1, y1, x2, y2), det_conf) in enumerate(valid):
        crop_bgr = img_bgr[y1:y2, x1:x2]
        if crop_bgr.size == 0:
            print(f"[Crop {crop_idx}] Empty crop; skipping.")
            results_list.append({
                "crop_idx": crop_idx, "det_conf": det_conf, "ocr_text": "", "ocr_conf": 0.0, "box": [x1,y1,x2,y2]
            })
            continue

        # upscale small crops for better OCR
        if resize_for_ocr:
            ch, cw = crop_bgr.shape[:2]
            if max(ch, cw) < 150:
                scale = int(max(2, 150/max(ch, cw)))
                crop_bgr = cv2.resize(crop_bgr, (int(cw*scale), int(ch*scale)), interpolation=cv2.INTER_CUBIC)

        crop_rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)

        # run EasyOCR
        try:
            if allowlist:
                raw = reader.readtext(crop_rgb, detail=1, allowlist=allowlist)
            else:
                raw = reader.readtext(crop_rgb, detail=1)
        except Exception as e:
            print(f"[Crop {crop_idx}] OCR error: {e}")
            raw = []

        # pick best text by OCR confidence
        best_text = ""
        best_conf = 0.0
        for bbox, text, oconf in raw:
            if float(oconf) > best_conf:
                best_conf = float(oconf)
                best_text = text

        if best_text:
            print(f"[Crop {crop_idx}] DetConf={det_conf:.3f}  OCR='{best_text}'  OCR_conf={best_conf:.3f}")
        else:
            print(f"[Crop {crop_idx}] DetConf={det_conf:.3f}  OCR=<no text>")

        results_list.append({
            "crop_idx": crop_idx,
            "det_conf": det_conf,
            "ocr_text": best_text,
            "ocr_conf": best_conf,
            "box": [int(x1), int(y1), int(x2), int(y2)]
        })

    return results_list

def main():
    parser = argparse.ArgumentParser(description="YOLO -> In-memory crop -> EasyOCR (no disk writes)")
    parser.add_argument("--model", "-m", required=True, help="Path to YOLO .pt model")
    parser.add_argument("--image", "-i", required=True, help="Path to input image")
    parser.add_argument("--conf", type=float, default=0.35, help="Detector confidence threshold")
    parser.add_argument("--allowlist", type=str, default="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789- ",
                        help="Characters allowed for OCR (use quotes)")
    parser.add_argument("--lang", type=str, default="en", help="EasyOCR language code (comma-separated if many)")
    parser.add_argument("--imgsz", type=int, default=1280, help="YOLO imgsz for inference (reduce for speed)")
    args = parser.parse_args()

    ocr_langs = [s.strip() for s in args.lang.split(",") if s.strip()]

    try:
        results = detect_and_ocr(
            model_path=args.model,
            image_path=args.image,
            conf_thresh=args.conf,
            allowlist=args.allowlist,
            resize_for_ocr=True,
            ocr_langs=ocr_langs,
            imgsz=args.imgsz
        )
    except Exception as e:
        print("ERROR:", e)
        sys.exit(1)

    print("\nFINAL RESULTS:")
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
