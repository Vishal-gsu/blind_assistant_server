from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Literal
import base64
from PIL import Image
import io
import uvicorn
from modules import ai_models
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import datetime
from modules.face import FaceManager
import numpy as np

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the AI models on startup
    ai_models.load_models()
    yield
    # No cleanup needed

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

face_manager = FaceManager()

class ConversationTurn(BaseModel):
    role: str
    content: str

class ProcessRequest(BaseModel):
    task: Literal['describe_scene', 'read_text', 'find_object', 'answer_question', 'time', 'face_detect']
    image_data: Optional[str] = None  # Base64 encoded JPEG image, now optional
    query_text: Optional[str] = None
    conversation_history: Optional[List[ConversationTurn]] = None

class ProcessResponse(BaseModel):
    result_text: str
    structured_data: Optional[dict] = None

@app.post("/process_data", response_model=ProcessResponse)
async def process_data(request: ProcessRequest):
    """
    Processes a request containing an image and a task.
    """
    print(f"Received task: {request.task}")

    image = None
    if request.image_data:
        try:
            # Decode the base64 image
            image_bytes = base64.b64decode(request.image_data)
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image data: {e}")

    result_text = ""
    structured_data = None

    if request.task == 'describe_scene':
        if not image:
            raise HTTPException(status_code=400, detail="Image data is required for describe_scene task")
        result_text = ai_models.describe_scene(image)
    elif request.task == 'read_text':
        if not image:
            raise HTTPException(status_code=400, detail="Image data is required for read_text task")
        result_text = ai_models.read_text(image)
    elif request.task == 'find_object':
        if not image or not request.query_text:
            raise HTTPException(status_code=400, detail="Image data and query_text are required for find_object task")
        response = ai_models.find_object(image, request.query_text)
        result_text = response.get("result_text")
        structured_data = response.get("structured_data")
    elif request.task == 'answer_question':
        if not image or not request.query_text:
            raise HTTPException(status_code=400, detail="Image data and query_text are required for answer_question task")
        result_text = ai_models.answer_question(image, request.query_text)
    elif request.task == 'time':
        now = datetime.datetime.now()
        result_text = f"The current time is {now.strftime('%H:%M')}"
    elif request.task == 'face_detect':
        if not image:
            raise HTTPException(status_code=400, detail="Image data is required for face_detect task")
        # Convert PIL image to numpy array for face_recognition
        frame = np.array(image)
        recognized_persons = face_manager.recognize_person_in_frame(frame)
        if recognized_persons:
            result_text = f"Detected persons: {', '.join(recognized_persons)}"
        else:
            result_text = "No known persons detected."
    else:
        raise HTTPException(status_code=400, detail="Invalid task")

    if not result_text:
        result_text = "I'm sorry, I couldn't process the request."

    return ProcessResponse(result_text=result_text, structured_data=structured_data)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
