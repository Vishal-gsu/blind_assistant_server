from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Literal
import base64
from PIL import Image
import io
import uvicorn
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import datetime
import numpy as np
import cv2

# Import the new modular services
from modules.vision import VisionModule
from modules.object_detection import ObjectDetector
from modules.face_recognition import FaceRecognizer
from modules.ocr import OCRReader

# --- Global instances of our services ---
vision_service = VisionModule()
object_service = ObjectDetector()
face_service = FaceRecognizer()
ocr_service = OCRReader()
# The old face_manager is replaced by face_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load all AI models on startup
    print("Loading all AI models...")
    vision_service.load_model()
    object_service.load_model()
    face_service.load_model()
    ocr_service.load_model()
    print("All models loaded.")
    yield
    # No cleanup needed for now

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConversationTurn(BaseModel):
    role: str
    content: str

class ProcessRequest(BaseModel):
    task: Literal[
        'describe_scene', 
        'read_text', 
        'find_object', # This will now use the new object detector
        'answer_question', 
        'time', 
        'recognize_face', # Renamed from face_detect for clarity
        'save_face'       # New task
    ]
    image_data: Optional[str] = None
    query_text: Optional[str] = None # Used for VQA, find_object, and save_face
    conversation_history: Optional[List[ConversationTurn]] = None

class ProcessResponse(BaseModel):
    result_text: str
    structured_data: Optional[dict] = None

@app.post("/process_data", response_model=ProcessResponse)
async def process_data(request: ProcessRequest):
    """
    Processes a request containing an image and a task using the new modular services.
    """
    print(f"Received task: {request.task}")

    image = None
    if request.image_data:
        try:
            image_bytes = base64.b64decode(request.image_data)
            # Convert to numpy array for OpenCV compatibility
            nparr = np.frombuffer(image_bytes, np.uint8)
            cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            # Convert to PIL Image for vision models
            image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image data: {e}")

    result_text = ""
    structured_data = None

    try:
        if request.task == 'describe_scene':
            if not image:
                raise HTTPException(status_code=400, detail="Image data is required for describe_scene")
            result_text = vision_service.describe_scene(image)

        elif request.task == 'read_text':
            if not image:
                raise HTTPException(status_code=400, detail="Image data is required for read_text")
            ocr_results = ocr_service.read(np.array(image))
            result_text = " ".join([res['text'] for res in ocr_results]) if ocr_results else "No text found."
            structured_data = {"ocr_results": ocr_results}

        elif request.task == 'find_object':
            if not image:
                raise HTTPException(status_code=400, detail="Image data is required for find_object")
            # The new object detector doesn't need a query text, it finds all objects
            detected_objects = object_service.detect(np.array(image))
            if detected_objects:
                # Create a summary string
                summary = []
                for obj in detected_objects[:5]: # Report top 5
                    summary.append(f"{obj['name']} at {obj['depth_m']:.1f} meters")
                result_text = "I see: " + ", ".join(summary)
            else:
                result_text = "I could not detect any objects."
            structured_data = {"objects": detected_objects}

        elif request.task == 'answer_question':
            if not image or not request.query_text:
                raise HTTPException(status_code=400, detail="Image data and query_text are required")
            result_text = vision_service.answer_question(image, request.query_text)

        elif request.task == 'time':
            now = datetime.datetime.now()
            result_text = f"The current time is {now.strftime('%H:%M')}"

        elif request.task == 'recognize_face':
            if not image:
                raise HTTPException(status_code=400, detail="Image data is required for recognize_face")
            recognized_persons = face_service.recognize(np.array(image))
            if recognized_persons:
                known_persons = [p['name'] for p in recognized_persons if p['name'] != 'Unknown']
                if known_persons:
                    result_text = f"Detected persons: {', '.join(known_persons)}"
                else:
                    result_text = "I see a face, but I don't recognize them."
            else:
                result_text = "No faces detected."
            structured_data = {"faces": recognized_persons}

        elif request.task == 'save_face':
            if not image or not request.query_text:
                raise HTTPException(status_code=400, detail="Image and a name (in query_text) are required to save a face.")
            success = face_service.save_face(request.query_text, np.array(image))
            if success:
                result_text = f"Successfully saved face for {request.query_text}."
            else:
                result_text = f"Could not save face for {request.query_text}. Make sure a face is clearly visible."

        else:
            raise HTTPException(status_code=400, detail="Invalid task")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    if not result_text:
        result_text = "I'm sorry, I couldn't process the request."

    return ProcessResponse(result_text=result_text, structured_data=structured_data)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
