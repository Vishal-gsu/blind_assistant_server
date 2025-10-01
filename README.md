# Blind Assistive System 🦯

A comprehensive AI-powered assistive system designed to help visually impaired users navigate and interact with their environment through voice commands and computer vision.

## 🌟 Features

- **Scene Description**: Detailed descriptions of the user's surroundings using advanced computer vision
- **Text Recognition (OCR)**: Read text from images and documents aloud
- **Object Detection**: Identify and locate specific objects in the environment
- **Face Recognition**: Recognize known faces and manage face database
- **Voice Interaction**: Natural language processing for conversational AI assistance
- **Time Announcements**: Voice-activated time telling
- **RESTful API**: FastAPI-based server for integration with mobile applications

## 🏗️ Architecture

The system consists of several key modules:

- **FastAPI Server** (`main.py`): Core API server handling requests
- **AI Models** (`modules/ai_models.py`): Computer vision and NLP model management
- **Face Recognition** (`modules/face.py`): Face detection and recognition system
- **Object Detection** (`modules/object_detection.py`): YOLO-based object detection
- **OCR** (`modules/ocr.py`): Text extraction from images
- **LLM Integration** (`modules/llm.py`): Large language model for conversational AI
- **Voice Processing** (`modules/listening.py`): Audio processing capabilities

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- CUDA-compatible GPU (recommended for optimal performance)
- Webcam/Camera access
- Microphone access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Vishal-gsu/blind_assistant_server.git
   cd blind_assistant_server
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install PyTorch with CUDA support** (for GPU acceleration)
   ```bash
   # For CUDA 12.1 (adjust for your CUDA version)
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   ```bash
   cp env_template.txt .env
   # Edit .env file with your API keys and configurations
   ```

6. **Download required models**
   - The YOLOv8 model (`yolov8n.pt`) should be automatically downloaded
   - Face recognition models will be initialized on first run

### Running the Server

```bash
python main.py
```

The server will start on `http://localhost:8000` by default.

## 📡 API Endpoints

### POST `/process_data`

Main endpoint for processing various tasks:

```json
{
  "task": "describe_scene | read_text | find_object | answer_question | time | face_detect",
  "image_data": "base64_encoded_image",
  "query_text": "optional_text_query",
  "conversation_history": [
    {
      "role": "user",
      "content": "previous conversation"
    }
  ]
}
```

**Response:**
```json
{
  "result_text": "AI response text",
  "structured_data": {
    "additional_data": "if_applicable"
  }
}
```

## 🛠️ Configuration

### Environment Variables

Create a `.env` file based on `env_template.txt`:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key
HUGGINGFACE_API_TOKEN=your_huggingface_token

# Model Configuration
VISION_MODEL=gpt-4-vision-preview
LLM_MODEL=gpt-3.5-turbo

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

### Model Configuration

The system supports various AI models:
- **Vision Models**: OpenAI GPT-4 Vision, Hugging Face BLIP models
- **LLM Models**: OpenAI GPT models, local models via Hugging Face
- **Object Detection**: YOLOv8 (ultralytics)
- **OCR**: EasyOCR, Tesseract

## 📱 Mobile Integration

This server is designed to work with the Scout1 mobile application (React Native/Expo). The mobile app:

- Captures images and audio
- Sends requests to this server
- Provides voice feedback to users
- Manages wake word detection

## 🧪 Testing

Run the test suite:

```bash
python test.py
```

For specific module testing:
```bash
python -m pytest tests/
```

## 📁 Project Structure

```
blind_assistant_server/
├── main.py                 # FastAPI server
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
├── modules/
│   ├── ai_models.py       # AI model management
│   ├── face.py            # Face recognition
│   ├── object_detection.py # Object detection
│   ├── ocr.py             # Optical character recognition
│   ├── llm.py             # Language model integration
│   └── listening.py       # Audio processing
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── PROJECT_DOCUMENTATION.md
│   └── PROFESSOR_DOCUMENTATION.md
└── tests/
    └── test.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the `docs/` folder
- Review the API documentation for integration details

## 🙏 Acknowledgments

- OpenAI for GPT models
- Ultralytics for YOLOv8
- Hugging Face for transformer models
- EasyOCR team for text recognition
- FastAPI community

## 🔮 Future Enhancements

- [ ] Real-time video processing
- [ ] Multi-language support
- [ ] Offline model support
- [ ] Enhanced voice commands
- [ ] Gesture recognition
- [ ] Navigation assistance
- [ ] Shopping assistance features

---

**Built with ❤️ for accessibility and inclusion**