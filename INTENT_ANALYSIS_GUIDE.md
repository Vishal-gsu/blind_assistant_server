# 🧠 Intent Analysis Structure for Blind Assistive System

## 📋 Complete Function Capabilities

Based on the codebase analysis, here are ALL the functions your system can perform that should be included in your app's intent analysis:

## 🎯 Core Intent Categories

### 1. **VISION & SCENE ANALYSIS**
```json
{
  "intent": "describe_scene",
  "api_task": "describe_scene",
  "requires": ["image"],
  "description": "Generate detailed description of surroundings",
  "examples": [
    "What do you see?",
    "Describe the scene",
    "What's in front of me?",
    "Tell me about my surroundings",
    "What's happening around me?"
  ],
  "response_type": "text_description"
}
```

### 2. **TEXT RECOGNITION (OCR)**
```json
{
  "intent": "read_text",
  "api_task": "read_text", 
  "requires": ["image"],
  "description": "Read text from images, documents, signs",
  "examples": [
    "Read this text",
    "What does this say?",
    "Read the document",
    "What's written here?",
    "Read the sign",
    "Read the menu",
    "What does this paper say?"
  ],
  "response_type": "extracted_text"
}
```

### 3. **OBJECT DETECTION & SEARCH**
```json
{
  "intent": "find_object",
  "api_task": "find_object",
  "requires": ["image", "query_text"],
  "description": "Find specific objects in the environment",
  "examples": [
    "Find my keys",
    "Where is the cup?",
    "Look for a chair",
    "Is there a door?",
    "Find the remote control",
    "Where's my phone?",
    "Look for a person"
  ],
  "response_type": "object_location_with_coordinates"
}
```

### 4. **VISUAL QUESTION ANSWERING**
```json
{
  "intent": "answer_question",
  "api_task": "answer_question",
  "requires": ["image", "query_text"],
  "description": "Answer specific questions about what's visible",
  "examples": [
    "How many people are in the room?",
    "What color is the car?",
    "Is the door open?",
    "What's on the table?",
    "Are there any animals?",
    "What time does the clock show?",
    "Is it sunny outside?"
  ],
  "response_type": "specific_answer"
}
```

### 5. **FACE RECOGNITION**
```json
{
  "intent": "face_detect",
  "api_task": "face_detect",
  "requires": ["image"],
  "description": "Recognize known people from saved faces",
  "examples": [
    "Who is this person?",
    "Who do you see?",
    "Recognize this face",
    "Who's in front of me?",
    "Is this John?",
    "Do you know this person?"
  ],
  "response_type": "person_names_list"
}
```

### 6. **FACE MANAGEMENT**
```json
{
  "intent": "save_face",
  "api_task": "save_face",  
  "requires": ["image", "person_name"],
  "description": "Save/register new faces for future recognition",
  "examples": [
    "Save this person as John",
    "Remember this face",
    "Add this person to database",
    "Register this face as Mom",
    "Learn this person",
    "Store this face"
  ],
  "response_type": "confirmation_message",
  "note": "Requires implementation of save face endpoint"
}
```

### 7. **TIME & DATE**
```json
{
  "intent": "time",
  "api_task": "time",
  "requires": [],
  "description": "Get current time and date",
  "examples": [
    "What time is it?",
    "Tell me the time",
    "What's the current time?",
    "Time please",
    "What time do you have?"
  ],
  "response_type": "time_announcement"
}
```

### 8. **WEATHER INFORMATION**
```json
{
  "intent": "weather",
  "api_task": "weather",
  "requires": ["city_optional"],
  "description": "Get weather information for specified or default city",
  "examples": [
    "What's the weather?",
    "Weather in New York",
    "Is it raining?",
    "Temperature today",
    "Weather forecast",
    "How's the weather in London?"
  ],
  "response_type": "weather_description",
  "note": "Uses LLM module, not main API"
}
```

### 9. **LOCATION SETTINGS**
```json
{
  "intent": "set_city",
  "api_task": "set_location",
  "requires": ["city_name"],
  "description": "Set default city for weather and location-based services",
  "examples": [
    "Set my location to Boston",
    "Change city to Paris",
    "My location is Mumbai",
    "Set default city",
    "Change my city"
  ],
  "response_type": "confirmation_message",
  "note": "Uses LLM module"
}
```

### 10. **CONVERSATIONAL AI**
```json
{
  "intent": "general_conversation",
  "api_task": "answer_question",
  "requires": ["query_text", "conversation_history_optional"],
  "description": "General conversation and assistance",
  "examples": [
    "How are you?",
    "Tell me a joke",
    "What can you help me with?",
    "Good morning",
    "Thank you",
    "Help me understand this"
  ],
  "response_type": "conversational_response"
}
```

## 🔧 Additional Technical Capabilities

### **Object Detection with YOLO**
- Real-time object detection using YOLOv8
- 80+ object classes supported
- Confidence scoring and bounding boxes

### **OCR Engines**
- EasyOCR for natural scene text
- Tesseract for document text
- Preprocessing for better accuracy

### **Face Recognition Features**
- Face encoding and storage
- Multiple face detection in single image
- Center-focused face selection for saving

### **Audio Processing**
- Text-to-speech (pyttsx3)
- Voice command recognition
- Wake word detection capability

## 📱 Recommended Intent Flow for Mobile App

### **Primary Intent Categories for UI:**
1. **👁️ Visual Analysis**
   - Scene Description
   - Object Finding
   - Visual Q&A

2. **📖 Text Reading**
   - Document Reading
   - Sign Reading
   - Menu Reading

3. **👤 People Recognition**
   - Face Recognition
   - Save New Person
   - Face Management

4. **🌤️ Information Services**
   - Time/Date
   - Weather
   - Location Settings

5. **💬 Conversation**
   - General Questions
   - Help & Assistance

### **Intent Processing Logic:**
```javascript
function processIntent(userInput, imageData = null) {
  const intent = classifyIntent(userInput);
  
  const apiRequest = {
    task: mapIntentToAPI(intent),
    image_data: imageData,
    query_text: extractQuery(userInput, intent),
    conversation_history: getRecentHistory()
  };
  
  return sendToAPI(apiRequest);
}
```

### **Required API Endpoints to Implement:**

**Already Available:**
- `POST /process_data` - Main processing endpoint

**Suggested Additional Endpoints:**
- `POST /save_face` - For face registration
- `GET /known_faces` - List saved faces
- `DELETE /face/{name}` - Remove saved face
- `POST /weather` - Weather information
- `POST /set_location` - Location management

## 🎯 Intent Classification Keywords

### **High Confidence Keywords:**
- **Vision:** "see", "look", "describe", "what", "scene"
- **Text:** "read", "text", "document", "sign", "menu", "says"
- **Objects:** "find", "where", "locate", "search", "is there"
- **People:** "who", "person", "face", "recognize", "save"
- **Time:** "time", "clock", "date", "when"
- **Weather:** "weather", "temperature", "rain", "sunny", "forecast"

### **Context Clues:**
- Image presence indicates visual tasks
- Location mentions suggest weather/navigation
- Person names suggest face operations
- Question format suggests Q&A mode

This structure provides a comprehensive framework for implementing intent analysis in your mobile app! 🚀