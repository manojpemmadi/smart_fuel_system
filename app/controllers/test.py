import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controllers.ai_controller import detect_and_read_plate

plate_text = detect_and_read_plate(r"C:\Users\manoj\Downloads\test_2.jpg")
print("Detected Plate:", plate_text)
