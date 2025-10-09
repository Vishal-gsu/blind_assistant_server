# Tech Stack for the Blind Assistive System

This document outlines the technology stack used in the Blind Assistive System project. The system is built with a modular architecture, where each key feature is handled by a dedicated service.

## Core Technologies

- **Programming Language:** Python 3.10
- **Environment Management:** Conda

## Key Libraries and Frameworks

### 1. Voice Interaction

- **Voice Input (Speech-to-Text):**
    - **Library:** `faster-whisper`
    - **Model:** `base` model with INT8 quantization for CPU optimization.
    - **Description:** This library is used to transcribe spoken commands from the user into text. It's a reimplementation of OpenAI's Whisper model, optimized for speed.

- **Voice Output (Text-to-Speech):**
    - **Library:** `pyttsx3`
    - **Description:** This library is used to convert text responses from the system into spoken words, providing auditory feedback to the user.

### 2. Computer Vision

- **Object Detection:**
    - **Library:** `ultralytics`
    - **Model:** YOLOv9c
    - **Description:** Used to detect objects in the user's surroundings in real-time.

- **Depth Estimation:**
    - **Library:** `torch`, `timm`
    - **Model:** MiDaS (DPT_Large)
    - **Description:** Integrated with object detection to estimate the distance of detected objects, providing crucial information for obstacle avoidance.

- **Face Recognition:**
    - **Library:** `insightface`
    - **Model:** `buffalo_l`
    - **Description:** This service handles face detection and recognition. It can learn and identify known faces.

- **Optical Character Recognition (OCR):**
    - **Library:** `rapidocr-onnxruntime`
    - **Description:** This service is used to read and extract text from images, allowing the user to "read" documents, signs, and other written materials.

### 3. Services and APIs

- **Weather Service:**
    - **Library:** `requests`
    - **API:** OpenWeatherMap
    - **Description:** Fetches and provides real-time weather information for a specified location.

- **Navigation Service:**
    - **Library:** `requests`
    - **API:** OpenStreetMap (Nominatim for geocoding, OSRM for routing)
    - **Description:** Provides navigation assistance, including getting the current location and finding routes to a destination.

### 4. General Purpose Libraries

- **`opencv-python`:** For camera access and image processing.
- **`numpy`:** For numerical operations, especially with image data.
- **`pillow`:** For image manipulation.
- **`python-dotenv`:** For managing environment variables (like API keys).
- **`requests`:** For making HTTP requests to external APIs.

## Main Orchestrator (`main.py`)

The `main.py` file acts as the central orchestrator for the entire system. It initializes all the individual services and manages the main application loop, processing user commands and delegating tasks to the appropriate modules.
