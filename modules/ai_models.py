
from transformers import pipeline
from PIL import Image
import easyocr
import torch

# Global variables to hold the models
captioner = None
ocr_reader = None
object_detector = None
vqa_pipeline = None

def load_models():
    """Load all the AI models into memory."""
    global captioner, ocr_reader, object_detector, vqa_pipeline
    
    print("Loading models...")
    device = "cuda" if torch.cuda.is_available() else "cpu"

    if not captioner:
        captioner = pipeline("image-to-text", model="Salesforce/blip-image-captioning-large", device=device)
    if not ocr_reader:
        ocr_reader = easyocr.Reader(['en'])
    if not object_detector:
        object_detector = pipeline("zero-shot-object-detection", model="google/owlvit-base-patch32", device=device)
    if not vqa_pipeline:
        vqa_pipeline = pipeline("visual-question-answering", model="Salesforce/blip-vqa-base", device=device)
    print("Models loaded.")

def describe_scene(image: Image.Image) -> str:
    """Generate a caption for the image."""
    if not captioner:
        raise RuntimeError("Captioning model not loaded.")
    results = captioner(image)
    return results[0]['generated_text']

def read_text(image: Image.Image) -> str:
    """Read text from the image."""
    if not ocr_reader:
        raise RuntimeError("OCR model not loaded.")
    # EasyOCR works with numpy arrays
    import numpy as np
    image_np = np.array(image)
    results = ocr_reader.readtext(image_np)
    return " ".join([res[1] for res in results])

def find_object(image: Image.Image, query: str) -> dict:
    """Find a specific object in the image."""
    if not object_detector:
        raise RuntimeError("Object detection model not loaded.")
    results = object_detector(image, candidate_labels=[query])
    if results:
        # For simplicity, returning the first found object's info
        found_object = results[0]
        return {
            "result_text": f"I found the {found_object['label']} here.",
            "structured_data": {"box": found_object['box'], "score": found_object['score']}
        }
    return {"result_text": f"I could not find a {query}."}

def answer_question(image: Image.Image, question: str) -> str:
    """Answer a question about the image."""
    if not vqa_pipeline:
        raise RuntimeError("VQA model not loaded.")
    results = vqa_pipeline(image, question=question)
    return results[0]['answer']
