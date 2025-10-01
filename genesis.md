ject Genesis & API Specification: The "Professor" Server
## 1. Persona & Role
Act as a Senior Backend & AI Engineer. Your name is Taylor. You specialize in building robust, high-performance APIs for machine learning systems using Python and FastAPI. You prioritize clean code, clear API contracts, and efficient model serving. Your goal is to build a reliable and intelligent "brain" for the Scout application.

## 2. The "Professor & Scout" Analogy Explained
This analogy defines a client-server relationship optimized for an assistive application.

The Scout (The Mobile App)
Role: The "Eyes and Ears."

Responsibilities:

Data Gathering: Captures real-time data from the world (camera frames, sensor data).

User Interaction: Handles the wake word ("Iris"), listens to voice commands, and speaks results using Text-to-Speech (TTS).

Lightweight Processing: Selects the "best" camera frame to send.

Context Management: Keeps track of the conversation history.

Characteristics: Fast, responsive, resource-constrained (must be mindful of battery), and operates in potentially offline environments.

The Professor (The FastAPI Server)
Role: The "Brain."

Responsibilities:

Receiving Data: Accepts curated data packages (a clear image, a specific user task, and context) from the Scout.

Heavy-Duty Analysis: Runs large, powerful AI/ML models (e.g., image captioning, object detection) that are too big or slow for a mobile phone.

Returning Insights: Sends back a concise, actionable result in a structured format.

Characteristics: Powerful, computationally intensive, and stateless.

The Relationship: A Stateless API
The relationship is a classic, stateless REST API. The Professor does not remember any specific Scout. Every request from the Scout is a self-contained "report" that includes all the information the Professor needs to do its job. The "conversation" is driven by the Scout, which includes the recent chat history in each new report it sends.

## 3. Core Architectural Principles
Statelessness: Every API request MUST be independent. The server will not store user sessions or state between requests.

Clear Contracts: We MUST use Pydantic models to strictly define and validate all incoming requests and outgoing responses.

Efficiency: AI models MUST be loaded once on server startup, not on every API call, to ensure low latency.

Modularity: The API routing logic (FastAPI) SHALL be separate from the AI inference logic (the model-running functions).

## 4. API Functionality & Endpoint Specification
The server will expose a single, intelligent, multi-modal endpoint to handle all requests from the Scout.

Endpoint: POST /process_data

Description: The universal entry point for all tasks. The specific action to be performed is determined by the task field in the request body.

### Request Body
The request will be a JSON object defined by the following Pydantic model:

Python

from typing import List, Optional, Literal
from pydantic import BaseModel

class ConversationTurn(BaseModel):
    role: str  # "user" or "scout"
    content: str

class ProcessRequest(BaseModel):
    task: Literal['describe_scene', 'read_text', 'find_object', 'answer_question']
    image_data: str  # Base64 encoded JPEG image
    query_text: Optional[str] = None  # e.g., "my keys" for find_object, or a question for VQA
    conversation_history: Optional[List[ConversationTurn]] = None
### Response Body
The successful response will be a JSON object defined by this Pydantic model:

Python

class ProcessResponse(BaseModel):
    result_text: str  # The primary text to be spoken to the user.
    structured_data: Optional[dict] = None  # For extra data, e.g., bounding box coordinates.
## 5. Task Implementation Logic
This section defines the functionality for each task requested by the client.

task: 'describe_scene'

Purpose: Provide a general description of what is in the image.

AI Model: Use a powerful Image Captioning model (e.g., Salesforce/blip-image-captioning-large).

Logic: The image_data is the only required input. The model generates a sentence, which is returned in the result_text.

task: 'read_text'

Purpose: Read any and all text visible in the image.

AI Model: Use an Optical Character Recognition (OCR) library or model (e.g., EasyOCR, or a dedicated OCR model).

Logic: The model extracts all text from the image_data. The combined text is returned in result_text.

task: 'find_object'

Purpose: Locate a specific object mentioned by the user.

AI Model: Use a Zero-Shot Object Detection model (e.g., google/owlvit-base-patch32).

Logic: The model takes the image_data and the query_text (e.g., "a red bottle") and searches for it. If found, result_text will be "I found the [object] here," and structured_data will contain the bounding box coordinates. If not found, result_text will be "I could not find a [object]."

task: 'answer_question'

Purpose: Answer a specific question about the image.

AI Model: Use a Visual Question Answering (VQA) model (e.g., Salesforce/blip-vqa-base).

Logic: The model takes the image_data and the user's query_text (e.g., "what color is the car?") and generates a direct answer, which is returned in result_text.