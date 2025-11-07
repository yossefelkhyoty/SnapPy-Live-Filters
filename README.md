# SnapPy Live Filters

Real-time AR face filters web application using Flask, OpenCV, and MediaPipe FaceMesh.

## Features

- 🎥 **Live Webcam Processing**: Real-time face detection and filter overlay
- 🕶️ **Multiple Filters**: Sunglasses, Hat, Mustache, Dog Ears, Makeup
- ⚡ **Smooth Performance**: ~10 FPS processing with optimized frame capture
- 📸 **Screenshot Support**: Capture and save filtered frames
- 🎨 **Modern UI**: Beautiful, responsive interface
- 🔄 **Instant Filter Switching**: Change filters with a single click

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate Filter Images

If you don't have filter PNGs yet, generate sample ones:

```bash
python generate_filters.py
```

This will create placeholder PNG images in `static/filters/`.

### 3. Run the Application

```bash
python app.py
```

### 4. Open in Browser

Navigate to: **http://localhost:5000**

Allow camera permissions when prompted.

## Project Structure

```
SnapPy-Live-Filters/
├── app.py                      # Flask backend server
├── generate_filters.py          # Script to create sample filter PNGs
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── templates/
│   └── index.html             # Main HTML page
└── static/
    ├── css/
    │   └── style.css          # Styling
    ├── js/
    │   └── app.js             # Frontend JavaScript
    ├── filters/               # Filter PNG images
    │   ├── sunglasses.png
    │   ├── hat.png
    │   ├── mustache.png
    │   ├── dog_ears.png
    │   └── makeup.png
    └── screenshots/            # Saved screenshots (auto-created)
```

## How It Works

1. **Frontend (JavaScript)**:
   - Uses `getUserMedia` to access webcam
   - Captures frames every 100ms
   - Sends frame as base64 to Flask backend
   - Displays processed frame on canvas

2. **Backend (Flask)**:
   - Receives base64 image data
   - Decodes to OpenCV format
   - Detects face landmarks using MediaPipe FaceMesh (468 landmarks)
   - Applies selected filter based on landmark positions
   - Returns processed frame as base64 JPEG

3. **Filters**:
   - Each filter uses specific landmark indices for placement
   - Automatically scales, rotates, and positions based on face geometry
   - Supports transparent PNG overlays with alpha blending

## Available Filters

- **Sunglasses**: Uses eye landmarks (33, 263)
- **Hat**: Uses ear landmarks (234, 454) and forehead (10)
- **Mustache**: Uses mouth landmarks (61, 291) and nose tip (1)
- **Dog Ears**: Uses ear landmarks (234, 454) and head top (10)
- **Makeup**: Lip tint using mouth landmarks

## API Endpoints

### `POST /process_frame`
Processes a single frame and applies filter.

**Request:**
```json
{
  "image": "data:image/jpeg;base64,...",
  "filter": "sunglasses"
}
```

**Response:**
```json
{
  "image": "base64_encoded_jpeg",
  "landmarks_detected": true
}
```

### `POST /screenshot`
Saves current frame as PNG.

**Request:**
```json
{
  "image": "data:image/png;base64,..."
}
```

**Response:**
```json
{
  "success": true,
  "filename": "screenshot_1234567890.png"
}
```

## Customization

### Adding Your Own Filters

1. Place your PNG file (with transparency) in `static/filters/`
2. Add filter entry in `app.py`:
   ```python
   available_filters = {
       "your_filter": "your_filter.png",
       ...
   }
   ```
3. Add filter placement logic in `apply_filter()` function
4. Add button in `templates/index.html`

### Adjusting Frame Rate

Edit `FRAME_INTERVAL_MS` in `static/js/app.js`:
```javascript
this.FRAME_INTERVAL_MS = 100; // milliseconds between frames
```

Lower values = higher frame rate (more server load)

### Changing Camera Resolution

Edit video constraints in `static/js/app.js`:
```javascript
video: {
    width: { ideal: 1280 },
    height: { ideal: 720 }
}
```

## Troubleshooting

### Camera Not Working
- Ensure you've granted camera permissions in your browser
- Try a different browser (Chrome/Firefox recommended)
- Check if another app is using the camera

### Slow Performance
- Reduce frame interval (increase `FRAME_INTERVAL_MS`)
- Lower camera resolution
- Close other applications using the camera

### Filters Not Appearing
- Check browser console for errors
- Ensure filter PNG files exist in `static/filters/`
- Verify face is well-lit and fully visible

## Browser Compatibility

- ✅ Chrome/Edge (Chromium) - Recommended
- ✅ Firefox
- ⚠️ Safari - May require HTTPS
- ❌ Internet Explorer - Not supported

## Dependencies

- **Flask**: Web framework
- **OpenCV**: Image processing
- **MediaPipe**: Face detection and landmark tracking
- **NumPy**: Array operations

## License

MIT License

## Credits

Built with:
- MediaPipe FaceMesh for face landmark detection
- OpenCV for image processing
- Flask for backend API


