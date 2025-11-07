// static/js/app.js

/**
 * SnapPy Live Filters - Frontend JavaScript
 * Handles webcam capture, frame processing, and UI interactions
 */

class SnapPyApp {
    constructor() {
        this.video = document.getElementById('video');
        this.canvas = document.getElementById('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.fpsCounter = document.getElementById('fps-counter');
        this.statusEl = document.getElementById('status');
        
        this.currentFilter = null;
        this.isProcessing = false;
        this.stream = null;
        this.lastProcessedTime = 0;
        this.videoDisplayActive = true;
        
        // FPS tracking
        this.frameCount = 0;
        this.lastFpsTime = Date.now();
        this.currentFps = 0;
        
        // Frame processing interval (100ms = ~10 FPS to backend)
        this.processInterval = null;
        this.videoDisplayInterval = null;
        this.FRAME_INTERVAL_MS = 100;
        
        this.init();
    }
    
    /**
     * Initialize the application
     */
    async init() {
        this.setupEventListeners();
        await this.startCamera();
        this.startProcessing();
    }
    
    /**
     * Set up button click listeners
     */
    setupEventListeners() {
        // Filter buttons
        const filterButtons = document.querySelectorAll('.filter-btn');
        filterButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const filter = btn.dataset.filter;
                this.setFilter(filter === 'none' ? null : filter);
                
                // Update active state
                filterButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
        
        // Screenshot button
        document.getElementById('btn-screenshot').addEventListener('click', () => {
            this.captureScreenshot();
        });
    }
    
    /**
     * Start webcam stream
     */
    async startCamera() {
        try {
            this.updateStatus('Requesting camera access...');
            
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'user' // Front-facing camera
                }
            });
            
            this.video.srcObject = this.stream;
            await this.video.play();
            
            // Set canvas size to match video
            this.video.addEventListener('loadedmetadata', () => {
                this.canvas.width = this.video.videoWidth;
                this.canvas.height = this.video.videoHeight;
                this.updateStatus('Camera ready!');
                
                // Immediately draw video to canvas for visual feedback
                this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
            });
            
        } catch (error) {
            console.error('Error accessing camera:', error);
            this.updateStatus('Camera access denied. Please allow camera permissions.');
            alert('Unable to access camera. Please check permissions and refresh the page.');
        }
    }
    
    /**
     * Start the frame processing loop
     */
    startProcessing() {
        // Start displaying video directly on canvas continuously for immediate feedback
        this.startVideoDisplay();
        
        // Then start processing frames at regular intervals
        this.processInterval = setInterval(() => {
            if (!this.isProcessing && this.video.readyState === this.video.HAVE_ENOUGH_DATA) {
                this.processFrame();
            }
        }, this.FRAME_INTERVAL_MS);
    }
    
    /**
     * Continuously draw video to canvas for immediate visual feedback
     * This ensures video is always visible, even while processing
     */
    startVideoDisplay() {
        this.videoDisplayInterval = setInterval(() => {
            if (this.video.readyState === this.video.HAVE_ENOUGH_DATA && 
                this.canvas.width > 0 && 
                this.videoDisplayActive) {
                // Draw video directly - will be overridden by processed frames
                const timeSinceLastProcess = Date.now() - this.lastProcessedTime;
                // Only draw video if no processed frame was received recently (within 200ms)
                if (timeSinceLastProcess > 200) {
                    this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
                }
            }
        }, 33); // ~30 FPS for smooth video display
    }
    
    /**
     * Capture current frame and send to backend for processing
     */
    async processFrame() {
        if (this.isProcessing || !this.stream) return;
        
        this.isProcessing = true;
        
        try {
            // Capture current video frame directly (don't draw to canvas yet)
            // Create a temporary canvas to capture frame
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = this.video.videoWidth;
            tempCanvas.height = this.video.videoHeight;
            const tempCtx = tempCanvas.getContext('2d');
            tempCtx.drawImage(this.video, 0, 0, tempCanvas.width, tempCanvas.height);
            
            // Convert to base64
            const imageData = tempCanvas.toDataURL('image/jpeg', 0.8);
            
            // Send to backend
            const response = await fetch('/process_frame', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: imageData,
                    filter: this.currentFilter
                })
            });
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                console.error('Backend error:', data.error);
                this.isProcessing = false;
                return;
            }
            
            // Display processed image
            if (data.image) {
                const img = new Image();
                img.onload = () => {
                    // Temporarily disable video display to show processed frame
                    this.videoDisplayActive = false;
                    
                    // Clear and draw processed image
                    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                    this.ctx.drawImage(img, 0, 0, this.canvas.width, this.canvas.height);
                    
                    // Update timestamp for processed frame
                    this.lastProcessedTime = Date.now();
                    
                    // Re-enable video display after a short delay
                    setTimeout(() => {
                        this.videoDisplayActive = true;
                    }, 150);
                    
                    // Update FPS
                    this.updateFPS();
                    
                    // Update status if landmarks detected
                    if (data.landmarks_detected) {
                        const numFaces = data.num_faces || 1;
                        if (numFaces > 1) {
                            this.updateStatus(`${numFaces} faces detected`);
                        } else {
                            this.updateStatus('Face detected');
                        }
                    } else {
                        this.updateStatus('No face detected');
                    }
                    
                    this.isProcessing = false;
                };
                img.onerror = () => {
                    console.error('Failed to load processed image');
                    // Keep showing video on error
                    this.videoDisplayActive = true;
                    this.isProcessing = false;
                };
                img.src = 'data:image/jpeg;base64,' + data.image;
            } else {
                // No processed image, keep showing video
                this.videoDisplayActive = true;
                this.isProcessing = false;
            }
            
        } catch (error) {
            console.error('Error processing frame:', error);
            this.isProcessing = false;
            this.updateStatus('Processing error');
        }
    }
    
    /**
     * Set the active filter
     */
    setFilter(filterName) {
        this.currentFilter = filterName;
        console.log('Filter changed to:', filterName || 'none');
    }
    
    /**
     * Update FPS counter
     */
    updateFPS() {
        this.frameCount++;
        const now = Date.now();
        const elapsed = now - this.lastFpsTime;
        
        if (elapsed >= 1000) {
            this.currentFps = (this.frameCount * 1000) / elapsed;
            this.frameCount = 0;
            this.lastFpsTime = now;
            this.fpsCounter.textContent = `FPS: ${this.currentFps.toFixed(1)}`;
        }
    }
    
    /**
     * Update status message
     */
    updateStatus(message) {
        this.statusEl.textContent = message;
        
        // Add loading animation for certain messages
        if (message.includes('Processing') || message.includes('Requesting')) {
            this.statusEl.classList.add('loading');
        } else {
            this.statusEl.classList.remove('loading');
        }
    }
    
    /**
     * Capture and save a screenshot
     */
    async captureScreenshot() {
        try {
            this.updateStatus('Capturing screenshot...');
            
            // Get current canvas as PNG (highest quality)
            const imageData = this.canvas.toDataURL('image/png', 1.0);
            
            const response = await fetch('/screenshot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: imageData
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.updateStatus('Screenshot saved!');
                
                // Also trigger download in browser
                const link = document.createElement('a');
                link.download = data.filename || `screenshot_${Date.now()}.png`;
                link.href = imageData;
                link.click();
                
                setTimeout(() => {
                    if (this.currentFilter && this.video.readyState === this.video.HAVE_ENOUGH_DATA) {
                        this.updateStatus('Face detected');
                    } else {
                        this.updateStatus('Ready');
                    }
                }, 2000);
            } else {
                this.updateStatus('Screenshot failed: ' + (data.error || 'Unknown error'));
            }
            
        } catch (error) {
            console.error('Error capturing screenshot:', error);
            this.updateStatus('Screenshot error');
        }
    }
    
    /**
     * Cleanup on page unload
     */
    cleanup() {
        if (this.processInterval) {
            clearInterval(this.processInterval);
        }
        if (this.videoDisplayInterval) {
            clearInterval(this.videoDisplayInterval);
        }
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SnapPyApp();
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        if (window.app) {
            window.app.cleanup();
        }
    });
});

