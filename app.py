# app.py
from flask import Flask, render_template, request, jsonify
import os
import base64
import cv2
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    data = request.get_json()
    image_data = data.get('image', None)

    if image_data is None:
        return jsonify({'error': 'No image received'}), 400

    image_data = image_data.split(',')[1]
    image_bytes = base64.b64decode(image_data)
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    _, buffer = cv2.imencode('.jpg', frame)
    encoded_image = base64.b64encode(buffer).decode('utf-8')

    return jsonify({'image': encoded_image, 'landmarks_detected': False})

@app.route('/screenshot', methods=['POST'])
def screenshot():
    data = request.get_json()
    image_data = data.get('image', None)

    if image_data is None:
        return jsonify({'error': 'No image data provided'}), 400

    filename = f"screenshot_{int(cv2.getTickCount())}.png"
    path = os.path.join('static', 'screenshots')
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, filename)

    image_data = image_data.split(',')[1]
    image_bytes = base64.b64decode(image_data)
    with open(file_path, 'wb') as f:
        f.write(image_bytes)

    return jsonify({'success': True, 'filename': filename})

if __name__ == '__main__':
    app.run(debug=True)
