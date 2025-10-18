from flask import Flask, render_template, request, redirect, url_for, flash
import os
from controllers.ai_controller import detect_and_read_plate
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Upload folder and allowed extensions
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Home page - upload form
@app.route('/')
def index():
    return render_template('upload.html')

# Handle file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Run OCR + YOLO pipeline
        try:
            plate_text = detect_and_read_plate(filepath)
            if plate_text:
                return render_template('upload.html', plate_text=plate_text, filename=filename)
            else:
                return render_template('upload.html', plate_text="No plate detected.", filename=filename)
        except Exception as e:
            return render_template('upload.html', plate_text=f"Error: {str(e)}", filename=filename)
    
    else:
        flash('Allowed file types are png, jpg, jpeg, bmp, tiff')
        return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
