# 👻 SnapPy Live Filters  
*Computer Vision Project Proposal*

---

## 🎯 Project Idea

### *Description*
This project develops an *interactive real-time AR face filters web application* controlled by webcam input.  
The app runs in the *browser (HTML/CSS/JavaScript)*, while **Python (Flask + OpenCV + MediaPipe FaceMesh)** handles *face detection and landmark tracking* through the webcam.  
The backend processes video frames, applies selected filters (e.g., sunglasses, hat, crown, mask, makeup, Spiderman, full-face mask) based on facial landmarks, and returns the filtered frames to the browser via Flask API endpoints.  

This project demonstrates how *computer vision* and *web technologies* can be combined for *fun, interactive AR experiences* similar to Snapchat filters.

*Target Users:*  
Casual users for entertainment, AR enthusiasts, web developers learning computer vision integration, and educators teaching MediaPipe and OpenCV.

*Expected Outcome:*  
A working web app where users can apply real-time face filters via webcam, switch filters instantly, capture screenshots, and experience smooth multi-face support (up to 5 faces).

---

## 🎯 Objectives
1. Implement real-time face detection and landmark tracking using Python (OpenCV + MediaPipe FaceMesh).  
2. Transmit processed frames to the browser using Flask API.  
3. Develop a responsive UI for filter selection and live display using JavaScript, HTML, and CSS.  
4. Ensure smooth performance (~10 FPS) with minimal latency.  
5. Demonstrate full integration between computer vision and web technologies.

---

## 📘 Scope

### *In Scope*
- Real-time face detection and multi-face support (up to 5 faces).  
- Browser-based UI for filter selection, live preview, and screenshot capture.  
- Filter application logic (scaling, rotation, and positioning).  
- Local testing, demo video, and placeholder filter image generation.  

### *Out of Scope*
- 3D filters or AI-generated effects.  
- Cloud deployment or mobile optimization.  
- User authentication or social media sharing.

---

## 👥 Team Members and Roles

| Team Member | GitHub Account | Responsibilities |
|--------------|----------------|------------------|
| **Youssef Mohammed Elkhyoty** | [https://github.com/yossefelkhyoty](https://github.com/yossefelkhyoty) | Implement face tracking, filter application logic, and backend API endpoints. |
| **Mrwan Mostafa Ragab** | [https://github.com/mrwan-ragab](https://github.com/mrwan-ragab) | Develop frontend UI, handle webcam capture, and integrate JavaScript with Flask. |
| **Mossad Ahmed Mossad** | [https://github.com/Sadoun90](https://github.com/Sadoun90) | Test system performance, debug issues, create sample filters, and write documentation. |

---

## 🧰 Tools and Usage

| Tool/Library | Purpose | Usage Details |
|---------------|----------|----------------|
| **Python** | Backend processing | Handles webcam frames, face detection, and filter overlay. |
| **OpenCV** | Image processing | Captures, decodes, resizes, rotates, and blends filters. |
| **MediaPipe FaceMesh** | Face tracking | Detects up to 5 faces with 468 landmarks for accurate filter placement. |
| **Flask** | Web server & API | Serves frontend, processes frames via `/process_frame`, and saves screenshots. |
| **JavaScript (HTML/CSS)** | Frontend | Captures webcam frames every 100ms, sends to Flask, and displays results. |
| **NumPy** | Array operations | Supports image transformations and blending operations. |

*Hardware/Environment:*  
- Laptop or PC with webcam.  
- Python 3.x with dependencies from `requirements.txt`.  
- Modern browser (Chrome/Firefox recommended).

---

## 📅 4-Week Plan

### *Week 1: Planning and Setup*
**Milestones:**  
- Finalize architecture (Flask backend + JS frontend).  
- Set up environment and generate sample filters (`generate_filters.py`).  
- Test webcam access and frame capture.  
**Deliverables:**  
- Working Flask server with index page and sample filters.  
**Assigned:**  Mrwan Mostafa Ragab.  

---

### *Week 2: Development Phase 1*
**Milestones:**  
- Implement MediaPipe FaceMesh (multi-face detection).  
- Add filter overlay functions (scaling, rotation, blending).  
- Set up Flask API endpoints (`/process_frame`, `/screenshot`).  
**Deliverables:**  
- Backend applies filters (sunglasses, hat, crown, mask, Spiderman).  
**Assigned:** Youssef Mohammed Elkhyoty.  

---

### *Week 3: Development Phase 2 and Testing*
**Milestones:**  
- Build frontend (`index.html`, `app.js`) with webcam capture and UI.  
- Integrate Flask backend with JavaScript via fetch requests.  
- Test multi-face detection, filter accuracy, and performance (~10 FPS).  
**Deliverables:**  
- Fully functional live AR filter app with screenshot feature.  
**Assigned:** Mossad Ahmed Mossad.  

---

### *Week 4: Finalization and Presentation*
**Milestones:**  
- Optimize UI (FPS counter, filter selection) and backend (caching, error handling).  
- finalize README/documentation.  
**Deliverables:**  
- Polished final project and presentation.  
**Assigned:** All members.  

---

## 🕓 Overall Timeline Notes
Frontend-backend integration begins in **Week 2**.  
Testing and optimization continue until **Week 4** to ensure smooth and accurate filter tracking.

---

## ✅ Checklist for Detailed Tasks
- [ ] Setup environment and install dependencies.  
- [ ] Generate sample filters (`generate_filters.py`).  
- [ ] Implement multi-face tracking with MediaPipe.  
- [ ] Add filter overlay functions (scaling, rotation, transparency).  
- [ ] Establish Flask ↔ JS communication.  
- [ ] Build responsive frontend (`index.html`, `app.js`).  
- [ ] Integrate, test, and optimize performance.  
- [ ] Document everything in `README.md`.  

---

## 📊 Evaluation Criteria

**Success Metrics:**  
- Real-time performance (~10 FPS) with <200ms latency.  
- Filter alignment accuracy >90%.  
- Multi-face support and responsive UI.  

**Feedback:**  
- Gathered from instructor and peers during demo.  

**Next Steps:**  
- Add more filter types or custom PNG upload.  
- Explore TensorFlow.js for browser-only CV processing.  
- Deploy to Heroku or local network for live access.  

---
