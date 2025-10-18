from ultralytics import YOLO

# Load your trained YOLO model
model = YOLO(r"C:\Users\manoj\OneDrive\Documents\smart_fuel_system\app\model\last.pt")

# Print model info
model.info()  # shows layers, parameters, anchors, etc.
