from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import os
import face_recognition

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

user_face_encodings = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_reference', methods=['POST'])
def upload_reference():
    global user_face_encodings
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'reference.jpg')
        file.save(file_path)
        user_face_encoding = get_face_encoding(file_path)
        if user_face_encoding is not None and user_face_encoding.size > 0:
            user_face_encodings.append(user_face_encoding)
        return "Reference image uploaded and processed!"

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
        is_match = face_recognition_logic(file_path, user_face_encodings)
        results[file.filename] = is_match
    return render_template('uploaded_files.html', results=results)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def get_face_encoding(image_path):
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)
    if face_encodings:
        return face_encodings[0]
    else:
        return None

def face_recognition_logic(file_path, user_face_encodings, tolerance=0.5):
    if not user_face_encodings:
        return False
    image = face_recognition.load_image_file(file_path)
    face_encodings = face_recognition.face_encodings(image)
    for encoding in face_encodings:
        matches = face_recognition.compare_faces(user_face_encodings, encoding, tolerance=tolerance)
        if any(matches):
            return True
    return False

if __name__ == '__main__':
    app.run(debug=True)
