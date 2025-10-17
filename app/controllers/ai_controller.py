import cv2
import pytesseract
import numpy as np
from ultralytics import YOLO

# Set path to your Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load your trained YOLO model once
model = YOLO(r"C:\Users\manoj\OneDrive\Documents\smart_fuel_system\app\model\last.pt")

def detect_and_read_plate(image):
    """
    Detects a number plate using YOLO and extracts text using Tesseract OCR.
    Args:
        image (str or file-like): Path to image or Flask uploaded file.
    Returns:
        str or None: Detected plate text or None if no plate is found.
    """
    # Step 1: Read image (Flask file or path)
    if hasattr(image, "read"):  # handle Flask uploaded file
        img_array = np.frombuffer(image.read(), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    else:
        img = cv2.imread(image)
        if img is None:
            raise FileNotFoundError(f"Image not found: {image}")

    # Step 2: Run YOLO detection
    results = model.predict(source=img, conf=0.5, verbose=False)

    # Step 3: Extract bounding box from results
    for result in results:
        boxes = result.boxes.xyxy  # x1, y1, x2, y2
        if len(boxes) == 0:
            return None  # No plate detected
        x1, y1, x2, y2 = boxes[0].int().tolist()

        # Step 4: Crop the detected plate
        cropped_plate = img[y1:y2, x1:x2]

        # Step 5: Preprocess for OCR
        gray = cv2.cvtColor(cropped_plate, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # Step 6: OCR Extraction
        text = pytesseract.image_to_string(thresh, config='--psm 8')
        text = ''.join(filter(str.isalnum, text))  # clean unwanted characters

        return text  # return the detected plate text

    return None
