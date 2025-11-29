"""
SnapPy Live Filters - Backend Server
=====================================

A Flask-based web application that processes webcam frames in real-time,
applies face filters using MediaPipe FaceMesh and OpenCV, and returns
processed frames to the frontend.

Features:
- Real-time face detection (up to 5 faces)
- Multiple filter types (sunglasses, hat, crown, mask, etc.)
- Filter image caching for performance
- RESTful API endpoints for frame processing and screenshots

Author: Team SnapPy
"""

# app.py
from flask import Flask, render_template, request, jsonify
import os
import base64
import cv2
import numpy as np
import mediapipe as mp

app = Flask(__name__)

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh

# Initialize Face Mesh with multi-face detection (max 5 faces)
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=5,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Available filters mapping
available_filters = {
    "sunglasses": "sunglasses.png",
    "hat": "hat.png",
    "crown": "crown.png",
    "mask": "mask.png",
    "spiderman": "spiderman.png",
    "full_face_mask": "full_face_mask.png"
}

# Filter directory
FILTERS_DIR = os.path.join('static', 'filters')

# Filter image cache to avoid reloading from disk on every request
filter_cache = {}

# MediaPipe Face Mesh landmark indices (468 landmarks)
# Key landmarks for filter placement
LANDMARKS = {
    # Face contour
    "chin": 18,
    "jaw_left": 172,
    "jaw_right": 397,
    
    # Eyes
    "left_eye_left": 33,
    "left_eye_right": 133,
    "left_eye_top": 159,
    "left_eye_bottom": 145,
    "left_eye_center": 468,  # Will calculate from left_eye landmarks
    
    "right_eye_left": 362,
    "right_eye_right": 263,
    "right_eye_top": 386,
    "right_eye_bottom": 374,
    "right_eye_center": 469,  # Will calculate from right_eye landmarks
    
    # Nose
    "nose_tip": 1,
    "nose_bridge_top": 6,
    "nose_left": 131,
    "nose_right": 360,
    
    # Mouth
    "mouth_left": 61,
    "mouth_right": 291,
    "mouth_top": 13,
    "mouth_bottom": 14,
    "mouth_center_top": 13,
    "mouth_center_bottom": 14,
    
    # Forehead
    "forehead": 10,
    
    # Ears
    "left_ear": 234,
    "right_ear": 454,
    
    # Head top
    "head_top": 10
}

def calculate_distance(point1, point2):
    """Calculate Euclidean distance between two points."""
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def calculate_angle(point1, point2):
    """Calculate angle between two points in degrees."""
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    angle = np.degrees(np.arctan2(dy, dx))
    return angle

def get_landmark_point(landmarks, idx):
    """Get landmark point coordinates."""
    if idx >= len(landmarks.landmark):
        return None
    landmark = landmarks.landmark[idx]
    return (landmark.x, landmark.y)

def load_filter_image(filter_name):
    """
    Load filter image with caching to improve performance.
    
    Args:
        filter_name: Name of the filter (key in available_filters)
    
    Returns:
        Filter image (BGRA) or None if not found
    """
    if filter_name not in available_filters:
        return None
    
    # Check cache first
    if filter_name in filter_cache:
        return filter_cache[filter_name]
    
    # Load from disk
    filter_path = os.path.join(FILTERS_DIR, available_filters[filter_name])
    if os.path.exists(filter_path):
        filter_img = cv2.imread(filter_path, cv2.IMREAD_UNCHANGED)
        if filter_img is not None:
            # Cache the image
            filter_cache[filter_name] = filter_img
            return filter_img
    
    return None

def overlay_filter(frame, filter_img, x, y, width, height, angle=0, alpha=1.0):
    """
    Overlay a filter image on the frame with scaling, rotation, and alpha blending.
    
    Args:
        frame: Background image (BGR)
        filter_img: Filter image with alpha channel (BGRA)
        x, y: Center position for overlay
        width, height: Desired size of filter
        angle: Rotation angle in degrees
        alpha: Transparency factor (0.0 to 1.0)
    
    Returns:
        Frame with filter overlaid
    """
    h, w = frame.shape[:2]
    
    # Resize filter to desired size
    filter_resized = cv2.resize(filter_img, (int(width), int(height)), interpolation=cv2.INTER_LINEAR)
    
    # Rotate filter if angle is not zero
    if angle != 0:
        center = (filter_resized.shape[1] // 2, filter_resized.shape[0] // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        filter_resized = cv2.warpAffine(filter_resized, rotation_matrix, 
                                        (filter_resized.shape[1], filter_resized.shape[0]),
                                        flags=cv2.INTER_LINEAR,
                                        borderMode=cv2.BORDER_TRANSPARENT)
    
    # Calculate position (center-based)
    x1 = int(x - width // 2)
    y1 = int(y - height // 2)
    x2 = int(x1 + width)
    y2 = int(y1 + height)
    
    # Check boundaries
    if x2 <= 0 or y2 <= 0 or x1 >= w or y1 >= h:
        return frame
    
    # Calculate intersection region
    frame_x1 = max(0, x1)
    frame_y1 = max(0, y1)
    frame_x2 = min(w, x2)
    frame_y2 = min(h, y2)
    
    filter_x1 = max(0, -x1)
    filter_y1 = max(0, -y1)
    filter_x2 = filter_x1 + (frame_x2 - frame_x1)
    filter_y2 = filter_y1 + (frame_y2 - frame_y1)
    
    # Extract filter region
    filter_region = filter_resized[filter_y1:filter_y2, filter_x1:filter_x2]
    frame_region = frame[frame_y1:frame_y2, frame_x1:frame_x2]
    
    # Handle alpha channel
    if filter_region.shape[2] == 4:
        # Split filter into BGR and alpha
        filter_bgr = filter_region[:, :, :3]
        filter_alpha = filter_region[:, :, 3:4] / 255.0 * alpha
        
        # Blend using alpha channel
        blended = (frame_region * (1 - filter_alpha) + filter_bgr * filter_alpha).astype(np.uint8)
    else:
        # No alpha channel, use alpha parameter for blending
        blended = cv2.addWeighted(frame_region, 1 - alpha, filter_region, alpha, 0)
    
    frame[frame_y1:frame_y2, frame_x1:frame_x2] = blended
    
    return frame

def apply_sunglasses(frame, landmarks, frame_width, frame_height):
    """Apply sunglasses filter based on eye landmarks."""
    # Get eye landmarks
    left_eye_left = get_landmark_point(landmarks, LANDMARKS["left_eye_left"])
    left_eye_right = get_landmark_point(landmarks, LANDMARKS["left_eye_right"])
    right_eye_left = get_landmark_point(landmarks, LANDMARKS["right_eye_left"])
    right_eye_right = get_landmark_point(landmarks, LANDMARKS["right_eye_right"])
    
    if not all([left_eye_left, left_eye_right, right_eye_left, right_eye_right]):
        return frame
    
    # Convert normalized coordinates to pixel coordinates
    left_eye_left = (int(left_eye_left[0] * frame_width), int(left_eye_left[1] * frame_height))
    left_eye_right = (int(left_eye_right[0] * frame_width), int(left_eye_right[1] * frame_height))
    right_eye_left = (int(right_eye_left[0] * frame_width), int(right_eye_left[1] * frame_height))
    right_eye_right = (int(right_eye_right[0] * frame_width), int(right_eye_right[1] * frame_height))
    
    # Calculate width (distance between outer eye corners)
    eye_width = calculate_distance(left_eye_left, right_eye_right)
    
    # Calculate center position (between eyes)
    center_x = (left_eye_left[0] + right_eye_right[0]) // 2
    center_y = (left_eye_left[1] + right_eye_right[1]) // 2
    
    # Calculate angle (tilt of face)
    angle = calculate_angle(left_eye_left, right_eye_right)
    
    # Load and apply filter (using cache)
    filter_img = load_filter_image("sunglasses")
    if filter_img is not None:
        # Scale filter to fit eye width with some padding
        filter_height = int(eye_width * 0.6)
        filter_width = int(eye_width * 2.2)
        frame = overlay_filter(frame, filter_img, center_x, center_y, 
                              filter_width, filter_height, angle, alpha=0.9)
    
    return frame

def apply_hat(frame, landmarks, frame_width, frame_height):
    """Apply hat filter based on forehead and ear landmarks."""
    forehead = get_landmark_point(landmarks, LANDMARKS["forehead"])
    left_ear = get_landmark_point(landmarks, LANDMARKS["left_ear"])
    right_ear = get_landmark_point(landmarks, LANDMARKS["right_ear"])
    
    if not all([forehead, left_ear, right_ear]):
        return frame
    
    # Convert to pixel coordinates
    forehead = (int(forehead[0] * frame_width), int(forehead[1] * frame_height))
    left_ear = (int(left_ear[0] * frame_width), int(left_ear[1] * frame_height))
    right_ear = (int(right_ear[0] * frame_width), int(right_ear[1] * frame_height))
    
    # Calculate width (distance between ears)
    head_width = calculate_distance(left_ear, right_ear)
    
    # Position above forehead
    center_x = forehead[0]
    center_y = int(forehead[1] - head_width * 0.3)
    
    # Calculate angle
    angle = calculate_angle(left_ear, right_ear)
    
    # Load and apply filter (using cache)
    filter_img = load_filter_image("hat")
    if filter_img is not None:
        filter_width = int(head_width * 1.8)
        filter_height = int(head_width * 1.2)
        frame = overlay_filter(frame, filter_img, center_x, center_y, 
                              filter_width, filter_height, angle, alpha=0.9)
    
    return frame

def apply_crown(frame, landmarks, frame_width, frame_height):
    """Apply crown filter based on forehead landmarks."""
    forehead = get_landmark_point(landmarks, LANDMARKS["forehead"])
    left_ear = get_landmark_point(landmarks, LANDMARKS["left_ear"])
    right_ear = get_landmark_point(landmarks, LANDMARKS["right_ear"])
    
    if not all([forehead, left_ear, right_ear]):
        return frame
    
    # Convert to pixel coordinates
    forehead = (int(forehead[0] * frame_width), int(forehead[1] * frame_height))
    left_ear = (int(left_ear[0] * frame_width), int(left_ear[1] * frame_height))
    right_ear = (int(right_ear[0] * frame_width), int(right_ear[1] * frame_height))
    
    # Calculate width
    head_width = calculate_distance(left_ear, right_ear)
    
    # Position above forehead
    center_x = forehead[0]
    center_y = int(forehead[1] - head_width * 0.4)
    
    # Calculate angle
    angle = calculate_angle(left_ear, right_ear)
    
    # Load and apply filter (using cache)
    filter_img = load_filter_image("crown")
    if filter_img is not None:
        filter_width = int(head_width * 1.5)
        filter_height = int(head_width * 1.0)
        frame = overlay_filter(frame, filter_img, center_x, center_y, 
                              filter_width, filter_height, angle, alpha=0.9)
    
    return frame

def apply_mask(frame, landmarks, frame_width, frame_height):
    """Apply mask filter using MediaPipe landmarks."""
    indices = {
        "nose_tip": 1,
        "chin": 152,
        "right_cheek": 234,
        "left_cheek": 454,
    }

    if any(idx >= len(landmarks.landmark) for idx in indices.values()):
        return frame

    def lm_to_px(idx):
        lm = landmarks.landmark[idx]
        return np.array([int(lm.x * frame_width), int(lm.y * frame_height)])

    nose_tip = lm_to_px(indices["nose_tip"])
    chin = lm_to_px(indices["chin"])
    right_cheek = lm_to_px(indices["right_cheek"])
    left_cheek = lm_to_px(indices["left_cheek"])

    face_width = np.linalg.norm(left_cheek - right_cheek)
    face_height = np.linalg.norm(nose_tip - chin)

    center_x = int((nose_tip[0] + chin[0]) / 2)
    # Slight upward shift so mask starts closer to nose
    center_y = int(nose_tip[1] +  face_height * .30)
    filter_img = load_filter_image("mask")
    if filter_img is None:
        return frame

    mask_width = int(face_width * 1.60)
    mask_height = int(face_height * 2)

    return overlay_filter(
        frame,
        filter_img,
        center_x,
        center_y,
        mask_width,
        mask_height,
        angle=0,
        alpha=0.95,
    )

def apply_spiderman(frame, landmarks, frame_width, frame_height):
    """Apply Spiderman mask filter covering the entire face."""
    indices = {
        "chin": 152,
        "forehead": 10,
        "left_side": 234,
        "right_side": 454,
    }

    if any(idx >= len(landmarks.landmark) for idx in indices.values()):
        return frame

    def lm_to_px(idx):
        lm = landmarks.landmark[idx]
        return np.array([int(lm.x * frame_width), int(lm.y * frame_height)])

    chin = lm_to_px(indices["chin"])
    forehead = lm_to_px(indices["forehead"])
    left_side = lm_to_px(indices["left_side"])
    right_side = lm_to_px(indices["right_side"])

    face_width = np.linalg.norm(right_side - left_side)
    face_height = np.linalg.norm(forehead - chin)

    center_x = int((left_side[0] + right_side[0]) / 2)
    center_y = int((forehead[1] + chin[1]) / 2) - int(face_height * 0.05)

    filter_img = load_filter_image("spiderman")
    if filter_img is None:
        return frame

    filter_width = int(face_width * 1.4)
    filter_height = int(face_height * 1.55)

    return overlay_filter(
        frame,
        filter_img,
        center_x,
        center_y,
        filter_width,
        filter_height,
        angle=0,
        alpha=0.95,
    )

def apply_full_face_mask(frame, landmarks, frame_width, frame_height):
    """Apply full face mask filter covering entire face."""
    # Similar to Spiderman but larger coverage
    chin = get_landmark_point(landmarks, LANDMARKS["chin"])
    forehead = get_landmark_point(landmarks, LANDMARKS["forehead"])
    left_ear = get_landmark_point(landmarks, LANDMARKS["left_ear"])
    right_ear = get_landmark_point(landmarks, LANDMARKS["right_ear"])
    
    if not all([chin, forehead, left_ear, right_ear]):
        return frame
    
    # Convert to pixel coordinates
    chin = (int(chin[0] * frame_width), int(chin[1] * frame_height))
    forehead = (int(forehead[0] * frame_width), int(forehead[1] * frame_height))
    left_ear = (int(left_ear[0] * frame_width), int(left_ear[1] * frame_height))
    right_ear = (int(right_ear[0] * frame_width), int(right_ear[1] * frame_height))
    
    # Calculate dimensions
    head_width = calculate_distance(left_ear, right_ear)
    head_height = calculate_distance(forehead, chin)
    
    # Center position
    center_x = (left_ear[0] + right_ear[0]) // 2
    center_y = int((forehead[1] + chin[1]) // 2)
    
    # Calculate angle
    angle = calculate_angle(left_ear, right_ear)
    
    # Load and apply filter (using cache)
    filter_img = load_filter_image("full_face_mask")
    if filter_img is not None:
        filter_width = int(head_width * 2.2)
        filter_height = int(head_height * 1.8)
        frame = overlay_filter(frame, filter_img, center_x, center_y, 
                              filter_width, filter_height, angle, alpha=0.9)
    
    return frame

def apply_filter_to_frame(frame, filter_name, faces):
    """Apply selected filter to all detected faces in the frame."""
    if filter_name is None or filter_name not in available_filters:
        return frame, 0
    
    frame_height, frame_width = frame.shape[:2]
    num_faces_detected = len(faces) if faces else 0
    
    # Convert BGR to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process with MediaPipe Face Mesh
    results = face_mesh.process(rgb_frame)
    
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Apply filter based on type
            if filter_name == "sunglasses":
                frame = apply_sunglasses(frame, face_landmarks, frame_width, frame_height)
            elif filter_name == "hat":
                frame = apply_hat(frame, face_landmarks, frame_width, frame_height)
            elif filter_name == "crown":
                frame = apply_crown(frame, face_landmarks, frame_width, frame_height)
            elif filter_name == "mask":
                frame = apply_mask(frame, face_landmarks, frame_width, frame_height)
            elif filter_name == "spiderman":
                frame = apply_spiderman(frame, face_landmarks, frame_width, frame_height)
            elif filter_name == "full_face_mask":
                frame = apply_full_face_mask(frame, face_landmarks, frame_width, frame_height)
        
        return frame, len(results.multi_face_landmarks)
    else:
        return frame, 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    try:
        data = request.get_json()
        image_data = data.get('image', None)
        filter_name = data.get('filter', None)

        if image_data is None:
            return jsonify({'error': 'No image received'}), 400

        # Decode base64 image
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({'error': 'Failed to decode image'}), 400

        # Apply filter if specified, or just detect faces for status
        landmarks_detected = False
        num_faces = 0
        
        if filter_name:
            frame, num_faces = apply_filter_to_frame(frame, filter_name, None)
            landmarks_detected = num_faces > 0
        else:
            # Still detect faces for status display even when no filter is selected
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)
            if results.multi_face_landmarks:
                num_faces = len(results.multi_face_landmarks)
                landmarks_detected = True

        # Encode processed frame to JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        encoded_image = base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            'image': encoded_image,
            'landmarks_detected': landmarks_detected,
            'num_faces': num_faces
        })

    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Error processing frame: {error_msg}")
        print(traceback.format_exc())
        # Return user-friendly error message (don't expose internal details)
        return jsonify({
            'error': 'Failed to process frame. Please try again.',
            'details': error_msg if app.debug else None
        }), 500

@app.route('/screenshot', methods=['POST'])
def screenshot():
    try:
        data = request.get_json()
        image_data = data.get('image', None)

        if image_data is None:
            return jsonify({'error': 'No image data provided'}), 400

        # Create screenshots directory if it doesn't exist
        path = os.path.join('static', 'screenshots')
        os.makedirs(path, exist_ok=True)

        # Generate filename with timestamp
        import time
        filename = f"screenshot_{int(time.time())}.png"
        file_path = os.path.join(path, filename)

        # Decode and save image
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        with open(file_path, 'wb') as f:
            f.write(image_bytes)

        return jsonify({'success': True, 'filename': filename})

    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Error saving screenshot: {error_msg}")
        print(traceback.format_exc())
        return jsonify({
            'error': 'Failed to save screenshot. Please try again.',
            'details': error_msg if app.debug else None
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
