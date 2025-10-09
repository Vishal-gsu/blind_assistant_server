# Blind Assistive System v2.0 🚀

A comprehensive, high-performance, self-contained AI assistive system designed to help visually impaired users navigate and interact with their environment. This version uses state-of-the-art models for object detection, depth estimation, face recognition, and OCR, all running on a local server to ensure privacy and offline functionality.

## 🌟 Core Features

- **Advanced Scene Understanding**: Get detailed descriptions of surroundings and ask specific questions about what you see.
- **High-Performance Object & Depth Detection**: Uses **YOLOv9c** to identify 80 different classes of objects and **MiDaS** to estimate their distance, providing a rich understanding of the scene.
- **Fast Face Recognition**: Recognizes known faces using **InsightFace** and allows saving new faces with a name.
- **Accurate Text Recognition (OCR)**: Reads text from documents, signs, and objects aloud using **RapidOCR**.
- **RESTful API**: A robust FastAPI server for seamless integration with mobile or other client applications.

## 🏗️ System Architecture: Modular & Scalable

The system is built as a modular local web server. This design separates the heavy AI processing from the user-facing client application and allows individual AI capabilities to be updated independently.

1.  **Uvicorn Web Server (`start_server.py`):** The entry point. It launches the FastAPI application.
2.  **FastAPI Application (`main.py`):** The API layer. It defines endpoints, handles incoming requests (e.g., image uploads), and routes tasks to the appropriate AI service. All models are loaded at startup for maximum performance.
3.  **AI Services (`modules/`):** Each core AI task is handled by a dedicated service module:
    - `vision.py`: Handles image captioning and visual question answering.
    - `object_detection.py`: Manages object detection (YOLOv9c) and depth estimation (MiDaS).
    - `face_recognition.py`: Manages face recognition and storage (InsightFace).
    - `ocr.py`: Handles text recognition (RapidOCR).

## 🤖 Core AI Models & Processing

All AI processing is done **locally**. Models are downloaded once and saved to a local cache. The system is optimized to use a **CUDA-enabled GPU** for all models, including PyTorch and ONNX runtimes.

| Feature | Model/Library Used | Backend |
| :--- | :--- | :--- |
| **Describe Scene** | `microsoft/git-base` | PyTorch |
| **Ask about Image** | `Salesforce/blip-vqa-base` | PyTorch |
| **Detect Objects** | `yolov9c.pt` (YOLOv9c) | PyTorch |
| **Estimate Depth** | `dpt_large` (MiDaS) | PyTorch |
| **Recognize/Save Faces** | `buffalo_l` (InsightFace) | ONNX |
| **Read Text** | `RapidOCR` | ONNX |

## 🚀 Quick Start: Installation Guide

### Prerequisites

- **Conda**: The environment is managed with Conda to handle complex dependencies.
- **NVIDIA GPU**: A CUDA-compatible GPU with drivers installed is required for performance.
- **Python 3.10**

### Installation Steps

1.  **Clone the repository**
    ```bash
    git clone https://github.com/SudipSaud/Blind_Assistive_system.git
    cd Blind_Assistive_system
    ```

2.  **Create and activate the Conda environment**
    This command creates a new environment named `blind` with Python 3.10.
    ```bash
    conda create -n blind python=3.10 -y
    conda activate blind
    ```

3.  **Install PyTorch with CUDA**
    Install the correct PyTorch version for your system's CUDA toolkit. The following command is for **CUDA 12.1**.
    *Verify your CUDA version with `nvidia-smi` and get the correct command from the [PyTorch website](https://pytorch.org/get-started/locally/).*
    ```bash
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    ```

4.  **Install ONNX Runtime for GPU**
    Install the GPU-enabled ONNX Runtime from the trusted `conda-forge` channel. This is crucial for GPU acceleration of face recognition and OCR.
    ```bash
    conda install -c conda-forge onnxruntime -y
    ```

5.  **Install remaining dependencies**
    Install all other required Python packages using `pip`.
    ```bash
    pip install -r requirements.txt
    ```

### Running the Server

Use the optimized startup script. The server will load all models into GPU memory before becoming available.
```bash
python start_server.py
```
The server will start on `http://localhost:8000`. You can access the interactive API documentation at `http://localhost:8000/docs`.

## 📡 API Endpoints

### POST `/process_data`

The main endpoint for all tasks.

**Request Body:**
```json
{
  "task": "describe_scene | read_text | find_object | answer_question | time | recognize_face | save_face",
  "image_data": "base64_encoded_image_string",
  "query_text": "Optional: For 'answer_question' (the question) or 'save_face' (the name)"
}
```

**Task Details:**
- `describe_scene`: Describes the image.
- `read_text`: Performs OCR on the image.
- `find_object`: Detects objects and their depth. `query_text` is not needed.
- `answer_question`: Answers the question in `query_text` about the image.
- `time`: Returns the current server time.
- `recognize_face`: Identifies known faces in the image.
- `save_face`: Saves a new face from the image using the name provided in `query_text`.


**Response:**
```json
{
  "result_text": "The AI-generated response.",
  "structured_data": { "additional_info": "if_applicable" }
}
```

## 📝 Project Roadmap & Issues

### High-Level Goals
- **Personalization**: Train models on user-specific data.
- **Performance**: Optimize models for speed and accuracy.
- **Robustness**: Improve error handling and configuration.

### Current Issues & Refactoring Tasks
- [ ] **Security**: Remove hardcoded path in `face.py` and use a relative or configured path.
- [ ] **Configuration**: Improve `.env` handling and rename `env_template.txt` to `.env.example`.
- [ ] **Dependencies**: Ensure all necessary packages are in `requirements.txt`.
- [ ] **Git**: Untrack `__pycache__` directories.
- [ ] **Error Handling**: Implement more specific API error responses.

### Planned Feature: Personalized Object Detection
- **Phase 1**: Create a `/learn_object` API endpoint to collect user-labeled images.
- **Phase 2**: Develop a script to fine-tune a lightweight model (e.g., YOLOv8-Nano) on the collected data.
- **Phase 3**: Integrate the personalized model into the `find_object` task, with a fallback to the general model.

## 🤝 Contributing

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/my-new-feature`).
3.  Commit your changes (`git commit -m 'Add some feature'`).
4.  Push to the branch (`git push origin feature/my-new-feature`).
5.  Open a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Hugging Face for the amazing `transformers` library and model hosting.
- The creators of FastAPI, PyTorch, and the other open-source libraries used in this project.