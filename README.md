# AI-Based Vehicle Number Plate Detection & OCR System

A professional, end-to-end AI web application that detects vehicle number plates from images, extracts the text using OCR, stores results in a database, and presents everything in a modern, minimal, dark glassmorphism UI.

## Features

- **AI-Powered Detection**: Uses YOLO model for accurate number plate detection
- **OCR Extraction**: EasyOCR for reliable text extraction from detected plates
- **Modern UI**: Glassmorphism design with dark theme
- **Database Storage**: SQLite database for detections and blacklist
- **Admin Panel**: User management and detection history
- **Responsive Design**: Works on desktop and mobile

## Tech Stack

- **Backend**: Python Flask
- **AI/ML**: YOLO (Ultralytics), EasyOCR, PyTorch
- **Database**: SQLAlchemy with SQLite
- **Frontend**: HTML5, CSS3, minimal JavaScript
- **Styling**: Custom glassmorphism CSS

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Place your trained YOLO model (`best.pt`) in the root directory
4. Run the application:
   ```bash
   python app.py
   ```
5. Open http://127.0.0.1:5000/ in your browser

## Usage

1. **Upload Image**: Drag and drop or click to upload a vehicle image
2. **AI Processing**: The system detects number plates and extracts text
3. **View Results**: See detection confidence, OCR confidence, and extracted text
4. **Admin Access**: Login at /admin with username: admin, password: admin123

## Project Structure

```
├── app.py                 # Main application entry point
├── config.py              # Configuration settings
├── detect_and_ocr.py      # AI detection and OCR logic
├── requirements.txt       # Python dependencies
├── best.pt               # Trained YOLO model
├── app/
│   ├── __init__.py       # Flask app factory
│   ├── models.py         # Database models
│   ├── auth.py           # Authentication decorators
│   ├── user/
│   │   ├── routes.py     # User-facing routes
│   │   └── templates/    # User templates
│   ├── admin/
│   │   ├── routes.py     # Admin routes
│   │   └── templates/    # Admin templates
│   └── predict.py        # Prediction API
├── static/
│   ├── css/
│   └── js/
└── uploads/              # Uploaded images
```

## API Endpoints

- `GET /` - Landing page
- `POST /` - Upload and process image
- `GET /admin/login` - Admin login
- `GET /admin/dashboard` - Admin dashboard
- `POST /api/predict` - API for predictions

## Contributing

This project is designed for educational and portfolio purposes. Feel free to enhance the UI, add features, or optimize the AI models.

## License

MIT License