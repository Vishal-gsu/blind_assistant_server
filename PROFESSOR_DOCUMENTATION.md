# Professor Server Documentation

## 1. Project Overview

This document outlines the technical details of the "Professor" server, the AI backend for the "Scout" assistive application. The project, named Blind Assistive System, follows a client-server architecture where the "Scout" (a client application) gathers real-world data and the "Professor" (this server) performs computationally intensive AI/ML analysis.

- **Architecture**: A stateless REST API where the client sends self-contained requests for processing.
- **Core Functionality**: The server accepts image and text data to perform tasks like scene description, text recognition (OCR), object detection, visual question answering, face detection, and providing the current time.

## 2. Core Technologies

- **Backend Framework**: FastAPI
- **Web Server**: Uvicorn
- **AI/ML**:
    - PyTorch
    - Hugging Face `transformers` for core models.
    - `easyocr` for Optical Character Recognition.
    - `ultralytics` for YOLO models (though used client-side, it's part of the project dependencies).
    - `face_recognition` for facial recognition tasks.
- **Language**: Python

## 3. Server Setup & Execution

Follow these steps to set up and run the Professor server.

### Step 1: Install Dependencies

All required Python packages are listed in `requirements.txt`. It is recommended to use a virtual environment.

```bash
# It is recommended to install PyTorch with CUDA support manually first
# e.g., pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

pip install -r requirements.txt
```

### Step 2: Run the Server

Execute the `main.py` script to start the server. The AI models will be loaded into memory on startup, which may take several minutes.

```bash
python main.py
```

Upon successful startup, you will see the following log message:
`INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)`

### Step 3: Configure Firewall (for Network Access)

To allow other devices on your local network (like a mobile phone running the Scout app) to connect to the server, you must add a firewall rule.

Open a Command Prompt or PowerShell **as Administrator** and run the following command:

```powershell
netsh advfirewall firewall add rule name="Allow FastAPI Port 8000" dir=in action=allow protocol=TCP localport=8000
```

## 4. API Specification

The server exposes a single universal endpoint for all tasks.

- **Endpoint**: `/process_data`
- **Method**: `POST`
- **URL**: `http://<SERVER_IP>:8000/process_data` (e.g., `http://192.168.1.4:8000/process_data`)
- **Content-Type**: `application/json`

### Request Body

```json
{
  "task": "string",
  "image_data": "string, optional",
  "query_text": "string, optional",
  "conversation_history": "array, optional"
}
```

- `task` (string, required): The specific task to perform. See "Available Tasks" below.
- `image_data` (string): A Base64 encoded string of the JPEG image to be processed. Required for all visual tasks.
- `query_text` (string, optional): Additional text required for certain tasks (e.g., the object to find, the question to answer).
- `conversation_history` (array, optional): Not currently implemented in the server logic, but available for future context-aware features.

### Response Body

```json
{
  "result_text": "string",
  "structured_data": "object, optional"
}
```

- `result_text` (string): The primary result to be spoken or displayed to the user.
- `structured_data` (object, optional): Supplementary data, such as bounding box coordinates for object detection.

## 5. Available Tasks

The `task` field in the request determines the action performed by the server.

| Task Name         | Description                                                  | `image_data` Required? | `query_text` Required? | AI Model Used                               |
|-------------------|--------------------------------------------------------------|:----------------------:|:----------------------:|---------------------------------------------|
| `describe_scene`  | Provides a general description of the image.                 |           Yes          |           No           | `Salesforce/blip-image-captioning-large`    |
| `read_text`       | Performs OCR to read all text in the image.                  |           Yes          |           No           | `easyocr`                                   |
| `find_object`     | Searches for a specific object in the image.                 |           Yes          |           Yes          | `google/owlvit-base-patch32`                |
| `answer_question` | Answers a direct question about the image.                   |           Yes          |           Yes          | `Salesforce/blip-vqa-base`                  |
| `face_detect`     | Detects and recognizes known faces in the image.             |           Yes          |           No           | `face_recognition` library                  |
| `time`            | Returns the current server time.                             |           No           |           No           | None (uses `datetime`)                      |

