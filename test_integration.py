"""
Integration Test Script for SnapPy Live Filters
Tests Flask backend endpoints and verifies filter functionality
"""

import requests
import base64
import cv2
import numpy as np
import json
import time

BASE_URL = "http://localhost:5000"

def create_test_image():
    """Create a simple test image with a face-like pattern"""
    # Create a simple colored image (in real usage, this would be a webcam frame)
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    img.fill(128)  # Gray background
    
    # Draw a simple face-like pattern
    cv2.circle(img, (320, 240), 100, (200, 180, 160), -1)  # Face
    cv2.circle(img, (290, 220), 10, (0, 0, 0), -1)  # Left eye
    cv2.circle(img, (350, 220), 10, (0, 0, 0), -1)  # Right eye
    cv2.ellipse(img, (320, 260), (30, 15), 0, 0, 180, (0, 0, 0), 2)  # Mouth
    
    # Encode to JPEG
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{img_base64}"

def test_process_frame(filter_name=None):
    """Test the /process_frame endpoint"""
    print(f"\n{'='*50}")
    print(f"Testing /process_frame with filter: {filter_name or 'none'}")
    print(f"{'='*50}")
    
    test_image = create_test_image()
    
    payload = {
        "image": test_image,
        "filter": filter_name
    }
    
    start_time = time.time()
    try:
        response = requests.post(
            f"{BASE_URL}/process_frame",
            json=payload,
            timeout=10
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Response time: {elapsed:.3f}s")
            print(f"   Landmarks detected: {data.get('landmarks_detected', False)}")
            print(f"   Number of faces: {data.get('num_faces', 0)}")
            print(f"   Image data length: {len(data.get('image', ''))} chars")
            return True
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def test_screenshot():
    """Test the /screenshot endpoint"""
    print(f"\n{'='*50}")
    print("Testing /screenshot endpoint")
    print(f"{'='*50}")
    
    test_image = create_test_image()
    
    payload = {
        "image": test_image
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/screenshot",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"   Filename: {data.get('filename', 'N/A')}")
            return True
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def test_performance():
    """Test performance with multiple requests"""
    print(f"\n{'='*50}")
    print("Performance Test (10 requests)")
    print(f"{'='*50}")
    
    test_image = create_test_image()
    payload = {"image": test_image, "filter": "sunglasses"}
    
    times = []
    successes = 0
    
    for i in range(10):
        start = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/process_frame",
                json=payload,
                timeout=5
            )
            elapsed = time.time() - start
            times.append(elapsed)
            if response.status_code == 200:
                successes += 1
        except:
            pass
    
    if times:
        avg_time = sum(times) / len(times)
        fps = 1.0 / avg_time if avg_time > 0 else 0
        print(f"✅ Completed {successes}/10 requests")
        print(f"   Average response time: {avg_time:.3f}s")
        print(f"   Estimated FPS: {fps:.1f}")
        print(f"   Target: ~10 FPS (100ms per frame)")
        
        if fps >= 8:
            print("   ✅ Performance target met!")
        else:
            print("   ⚠️  Performance below target")
    else:
        print("❌ No successful requests")

def main():
    """Run all tests"""
    print("\n" + "="*50)
    print("SnapPy Live Filters - Integration Tests")
    print("="*50)
    print(f"\nTesting server at: {BASE_URL}")
    print("Make sure the Flask server is running (python app.py)")
    
    # Test basic connectivity
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"\n✅ Server is reachable (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Cannot connect to server: {str(e)}")
        print("   Please start the Flask server first: python app.py")
        return
    
    # Test filters
    filters = [None, "sunglasses", "hat", "crown", "mask", "spiderman", "full_face_mask"]
    results = []
    
    for filter_name in filters:
        results.append(test_process_frame(filter_name))
        time.sleep(0.5)  # Small delay between requests
    
    # Test screenshot
    results.append(test_screenshot())
    
    # Performance test
    test_performance()
    
    # Summary
    print(f"\n{'='*50}")
    print("Test Summary")
    print(f"{'='*50}")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
    else:
        print("⚠️  Some tests failed")

if __name__ == "__main__":
    main()

