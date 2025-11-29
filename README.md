# 👻 SnapPy Live Filters  

**Real-time AR Face Filters Web Application**

A fully functional web application that applies real-time face filters to webcam video using computer vision. Built with Flask, OpenCV, and MediaPipe FaceMesh for accurate face detection and filter overlay.

![Status](https://img.shields.io/badge/status-complete-success)
![Python](https://img.shields.io/badge/python-3.7+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🎯 Features

- 🎥 **Real-time Processing**: Live webcam feed with ~10 FPS processing
- 🕶️ **6 Unique Filters**: Sunglasses, Hat, Crown, Mask, Spiderman, Full Face Mask
- 👥 **Multi-Face Support**: Detects and applies filters to up to 5 faces simultaneously
- 📸 **Screenshot Capture**: Save filtered frames as PNG images
- ⚡ **Optimized Performance**: Filter image caching and efficient frame processing
- 🎨 **Modern UI**: Beautiful, responsive interface with real-time FPS counter
- 🔄 **Instant Filter Switching**: Change filters with a single click
- 📊 **Performance Monitoring**: Color-coded FPS indicator

---

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Webcam/camera
- Modern web browser (Chrome, Firefox, or Edge recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SnapPy-Live-Filters
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate filter images** (if not already present)
   ```bash
   python generate_filters.py
   ```

4. **Start the Flask server**
   ```bash
   python app.py
   ```

5. **Open in browser**
   - Navigate to: `http://localhost:5000`
   - Allow camera permissions when prompted

---

## 📖 Usage

### Basic Usage

1. **Start the application** (see Installation above)
2. **Allow camera access** when prompted by your browser
3. **Select a filter** by clicking one of the filter buttons
4. **Position yourself** in front of the camera
5. **Capture screenshots** using the screenshot button

### Available Filters

| Filter | Description | Icon |
|--------|-------------|------|
| **Sunglasses** | Classic sunglasses overlay on eyes | 🕶️ |
| **Hat** | Cap/hat positioned on forehead | 🎩 |
| **Crown** | Royal crown on top of head | 👑 |
| **Mask** | Face mask covering nose and mouth | 😷 |
| **Spiderman** | Spiderman-style full face mask | 🕷️ |
| **Full Face** | Complete face coverage mask | 🎭 |

### Performance Tips

- **For better FPS**: Ensure good lighting and position face fully in frame
- **For multi-face**: Position all faces clearly visible in camera view
- **For accuracy**: Maintain steady position and avoid rapid movements

---

## 🏗️ Project Structure

```
SnapPy-Live-Filters/
├── app.py                      # Flask backend server
├── generate_filters.py          # Script to create sample filter PNGs
├── test_integration.py          # Integration test script
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── TESTING_GUIDE.md           # Detailed testing instructions
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
    │   ├── crown.png
    │   ├── mask.png
    │   ├── spiderman.png
    │   └── full_face_mask.png
    └── screenshots/            # Saved screenshots (auto-created)
```

---

## 🔧 How It Works

### Architecture

1. **Frontend (JavaScript)**
   - Captures webcam frames using `getUserMedia` API
   - Sends frames to Flask backend every 100ms (~10 FPS)
   - Displays processed frames on HTML5 canvas
   - Handles user interactions (filter selection, screenshots)

2. **Backend (Flask + OpenCV + MediaPipe)**
   - Receives base64-encoded image frames
   - Detects faces using MediaPipe FaceMesh (468 landmarks per face)
   - Applies selected filter based on facial landmarks
   - Returns processed frame as base64 JPEG

3. **Filter Application**
   - Each filter uses specific landmark indices for placement
   - Automatically scales, rotates, and positions based on face geometry
   - Supports transparent PNG overlays with alpha blending
   - Filter images are cached in memory for performance

### Key Technologies

- **MediaPipe FaceMesh**: Detects up to 5 faces with 468 landmarks each
- **OpenCV**: Image processing, transformations, and blending
- **Flask**: RESTful API for frame processing
- **JavaScript**: Real-time webcam capture and UI management

---

## 📡 API Endpoints

### `POST /process_frame`

Processes a single frame and applies the selected filter.

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
  "landmarks_detected": true,
  "num_faces": 1
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

---

## 🧪 Testing

### Manual Testing

See `TESTING_GUIDE.md` for detailed testing instructions.

### Automated Testing

Run the integration test script:

```bash
pip install requests
python test_integration.py
```

This will test:
- All filter endpoints
- Screenshot functionality
- Performance metrics
- Error handling

---

## 🎨 Customization

### Adding Your Own Filters

1. **Create filter image**
   - Create a PNG file with transparency
   - Recommended size: 300x150 pixels
   - Place in `static/filters/`

2. **Add to backend** (`app.py`)
   ```python
   available_filters = {
       "your_filter": "your_filter.png",
       ...
   }
   ```

3. **Add filter function**
   ```python
   def apply_your_filter(frame, landmarks, frame_width, frame_height):
       # Your filter logic here
       filter_img = load_filter_image("your_filter")
       # Apply filter using overlay_filter()
       return frame
   ```

4. **Add to frontend** (`templates/index.html`)
   ```html
   <button class="filter-btn" data-filter="your_filter">
       <span class="icon">🎭</span>
       <span>Your Filter</span>
   </button>
   ```

### Adjusting Performance

**Frame Rate:**
- Edit `FRAME_INTERVAL_MS` in `static/js/app.js` (line 30)
- Lower values = higher FPS (more server load)

**Camera Resolution:**
- Edit video constraints in `static/js/app.js` (lines 76-77)
- Lower resolution = better performance

**JPEG Quality:**
- Processing: `app.js` line 175 (currently 0.7)
- Output: `app.py` line 471 (currently 85)

---

## 🐛 Troubleshooting

### Camera Not Working
- ✅ Ensure camera permissions are granted
- ✅ Check if another application is using the camera
- ✅ Try a different browser (Chrome/Firefox recommended)
- ✅ Verify camera is connected and working

### Low FPS
- ✅ Reduce camera resolution
- ✅ Increase `FRAME_INTERVAL_MS` (slower processing)
- ✅ Close other applications
- ✅ Check server CPU usage

### Filters Not Appearing
- ✅ Ensure face is well-lit and fully visible
- ✅ Check browser console for errors
- ✅ Verify filter PNG files exist in `static/filters/`
- ✅ Try a different filter to isolate the issue

### Backend Errors
- ✅ Check Flask console for error messages
- ✅ Verify all dependencies are installed
- ✅ Ensure MediaPipe is working correctly
- ✅ Check that filter images are valid PNG files

---

## 📊 Performance Metrics

**Target Performance:**
- Frame Rate: ~10 FPS
- Latency: <200ms per frame
- Filter Accuracy: >90% alignment
- Multi-face: Up to 5 faces simultaneously

**Optimization Features:**
- Filter image caching (loaded once, reused)
- Efficient frame encoding/decoding
- Optimized JPEG quality settings
- Hardware-accelerated canvas rendering

---

## 👥 Team Members

| Team Member | GitHub | Role |
|-------------|--------|------|
| **Youssef Mohammed Elkhyoty** | [@yossefelkhyoty](https://github.com/yossefelkhyoty) | Backend development, face tracking, filter logic |
| **Mrwan Mostafa Ragab** | [@mrwan-ragab](https://github.com/mrwan-ragab) | Frontend development, webcam integration |
| **Mossad Ahmed Mossad** | [@Sadoun90](https://github.com/Sadoun90) | Testing, debugging, documentation |

---

## 📅 Development Timeline

- **Week 1**: Planning and Setup
- **Week 2**: Backend Development (MediaPipe, filters, API)
- **Week 3**: Frontend Development and Integration
- **Week 4**: Optimization, Testing, and Documentation

---

## 🔮 Future Enhancements

- [ ] 3D filters and effects
- [ ] Custom filter upload
- [ ] Social media sharing
- [ ] Mobile app version
- [ ] Cloud deployment
- [ ] AI-generated filters
- [ ] Video recording feature
- [ ] Filter customization (size, position)

---

## 📝 License

MIT License - feel free to use this project for learning and development!

---

## 🙏 Acknowledgments

- **MediaPipe** team for the excellent face detection library
- **OpenCV** community for comprehensive computer vision tools
- **Flask** developers for the lightweight web framework

---

## 📧 Contact & Support

For issues, questions, or contributions, please open an issue on GitHub or contact the team members.

---

**Made with ❤️ for Computer Vision Education**
