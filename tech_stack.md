# Tech Stack: Blind Assistive System (Self-Contained)

This document outlines the technology stack, architecture, and core components of the current version of the Blind Assistive System.

## 1. Core Technologies

- **Programming Language**: Python 3.12
- **Web Framework**: FastAPI
- **AI/ML Libraries**:
  - **PyTorch**: The primary deep learning framework for model execution.
  - **Hugging Face Transformers**: For accessing and running pre-trained models locally.
  - **EasyOCR**: For Optical Character Recognition (OCR).
  - **face_recognition**: For face detection and recognition.
- **Server**: Uvicorn (an ASGI server for FastAPI).

## 2. System Architecture

The system is designed as a self-contained, local web server that exposes its AI capabilities through a RESTful API. This architecture ensures user privacy and allows for offline operation.

- **`start_server.py`**: The entry point of the application. It sets up the environment and starts the Uvicorn server, which runs the FastAPI app.
- **`main.py`**: The FastAPI application. It defines the API endpoints (primarily `/process_data`), handles incoming requests, and calls the appropriate AI functions.
- **`modules/`**: A directory containing the core AI logic.
  - **`ai_models.py`**: The central AI engine. It loads all models into memory at startup and contains the functions for scene description, VQA, object detection, and OCR.
  - **`face.py`**: Manages all face recognition logic, including loading/saving known faces and identifying people in an image.

## 3. AI Models and Modules

All models are run locally on the device, ensuring a private and self-contained system.

| Feature | Module | Model/Library | Description |
| :--- | :--- | :--- | :--- |
| **Scene Description** | `ai_models.py` | `microsoft/git-base` | Generates a textual description of an image. |
| **Visual Question Answering** | `ai_models.py` | `Salesforce/blip-vqa-base` | Answers questions about an image. |
| **Object Detection** | `ai_models.py` | `google/owlvit-base-patch32` | Finds objects in an image based on a text query. |
| **Text Recognition (OCR)** | `ai_models.py` | `easyocr` | Extracts text from an image. |
| **Face Recognition** | `face.py` | `face_recognition` | Recognizes known faces and provides an interface to save new ones. |

## 4. API and Server

- **FastAPI**: Used to create the API. The main endpoint, `/process_data`, accepts a `task` and base64-encoded `image_data`.
- **Uvicorn**: The high-performance ASGI server that runs the FastAPI application.
- **CORS Middleware**: Enabled to allow requests from any origin, simplifying integration with a mobile app client.

## 5. Environment and Dependencies

- **`requirements.txt`**: A file listing all the Python dependencies required to run the project.
- **`.env`**: Used to store environment variables (though currently, no external API keys are required for the core functionality).
- **`env_template.txt`**: A template for the `.env` file.
