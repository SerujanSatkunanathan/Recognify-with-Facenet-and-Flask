from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import os
from deepface import DeepFace

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

user_reference_images = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_reference', methods=['POST'])
def upload_reference():
    global user_reference_images
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'reference.jpg')
        file.save(file_path)
        user_reference_images.append(file_path)
        return "Reference image uploaded and saved!"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    files = request.files.getlist('file')
    if not files:
        return redirect(request.url)
    results = {}
    for file in files:
        if file.filename == '':
            continue
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        is_match = deepface_recognition_logic(file_path, user_reference_images)
        results[file.filename] = is_match
    return render_template('uploaded_files.html', results=results)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def deepface_recognition_logic(file_path, user_reference_images, model_name='VGG-Face', distance_metric='cosine', threshold=0.4):
    if not user_reference_images:
        return False
    for reference_image in user_reference_images:
        result = DeepFace.verify(img1_path=reference_image, img2_path=file_path, model_name=model_name, distance_metric=distance_metric)
        if result["verified"]:
            return True
    return False

if __name__ == '__main__':
    app.run(debug=True)
