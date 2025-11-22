# SnapPy Live Filters - Testing Guide

## Week 3: Development Phase 2 and Testing

This guide helps verify that all Week 3 deliverables are working correctly.

## Prerequisites

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Generate filter images (if not already present):
   ```bash
   python generate_filters.py
   ```

3. Ensure filter images exist in `static/filters/`:
   - sunglasses.png
   - hat.png
   - crown.png
   - mask.png
   - spiderman.png
   - full_face_mask.png

## Testing Steps

### 1. Start the Flask Server

```bash
python app.py
```

The server should start on `http://localhost:5000`

### 2. Open in Browser

Navigate to `http://localhost:5000` in a modern browser (Chrome/Firefox recommended).

### 3. Test Webcam Capture

- ✅ Allow camera permissions when prompted
- ✅ Video should appear in the canvas
- ✅ Status should show "Camera ready!" or "Face detected"
- ✅ FPS counter should appear in top-right corner

### 4. Test Filter Switching

Test each filter button:
- ✅ None (no filter)
- ✅ Sunglasses 🕶️
- ✅ Hat 🎩
- ✅ Crown 👑
- ✅ Mask 😷
- ✅ Spiderman 🕷️
- ✅ Full Face 🎭

**Expected behavior:**
- Filter buttons should highlight when clicked
- Filters should appear on detected faces
- Filters should track face movement
- Status should update to show face detection

### 5. Test Multi-Face Detection

- ✅ Position 2-5 people in front of camera
- ✅ Apply a filter
- ✅ Status should show "X faces detected ✨"
- ✅ Filter should apply to all detected faces

### 6. Test Screenshot Feature

- ✅ Click the "Screenshot" button
- ✅ Status should show "Screenshot saved! 📷"
- ✅ Image should download automatically
- ✅ Check `static/screenshots/` folder for saved image

### 7. Performance Testing

**Target: ~10 FPS**

- ✅ Check FPS counter in top-right corner
- ✅ FPS should be around 8-12 FPS
- ✅ Video should be smooth without stuttering
- ✅ Filter application should be responsive

**Performance Tips:**
- Lower camera resolution if FPS is too low
- Close other applications using the camera
- Ensure good lighting for better face detection

### 8. Test Error Handling

- ✅ Cover camera - should show "No face detected"
- ✅ Stop server - should show timeout/error message
- ✅ Switch filters rapidly - should handle gracefully

## Integration Test Script

Run the automated test script (requires `requests` package):

```bash
pip install requests
python test_integration.py
```

This will test:
- All filter endpoints
- Screenshot functionality
- Performance metrics
- Error handling

## Troubleshooting

### Camera Not Working
- Check browser permissions
- Ensure no other app is using the camera
- Try a different browser

### Low FPS
- Reduce camera resolution in `app.js` (line 76-77)
- Increase `FRAME_INTERVAL_MS` in `app.js` (line 30)
- Check server CPU usage

### Filters Not Appearing
- Ensure face is well-lit and fully visible
- Check browser console for errors
- Verify filter PNG files exist in `static/filters/`

### Backend Errors
- Check Flask console for error messages
- Verify MediaPipe is installed correctly
- Ensure OpenCV can decode images

## Week 3 Deliverables Checklist

- ✅ Frontend (index.html, app.js) with webcam capture and UI
- ✅ Flask backend integration with JavaScript via fetch requests
- ✅ Multi-face detection (up to 5 faces)
- ✅ Filter accuracy and tracking
- ✅ Performance optimization (~10 FPS)
- ✅ Screenshot feature
- ✅ Error handling and user feedback
- ✅ Responsive UI with status indicators

## Next Steps (Week 4)

- Further UI/UX polish
- Additional filter types
- Performance monitoring dashboard
- Documentation finalization

