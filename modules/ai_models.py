from transformers import pipeline
from PIL import Image
import easyocr
import torch
import gc
import os
import numpy as np

# Global variables to hold the models
captioner = None
ocr_reader = None
object_detector = None
vqa_pipeline = None

def clear_gpu_memory():
    """Clear GPU memory cache."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()

def get_device_info():
    """Get device information and memory status."""
    if torch.cuda.is_available():
        device = torch.cuda.current_device()
        memory_allocated = torch.cuda.memory_allocated(device) / 1024**3  # GB
        memory_cached = torch.cuda.memory_reserved(device) / 1024**3  # GB
        total_memory = torch.cuda.get_device_properties(device).total_memory / 1024**3  # GB
        
        print(f"GPU Memory - Allocated: {memory_allocated:.2f}GB, Cached: {memory_cached:.2f}GB, Total: {total_memory:.2f}GB")
        return memory_allocated, memory_cached, total_memory
    return 0, 0, 0

def load_models():
    """Load all the AI models into memory with memory management."""
    global captioner, ocr_reader, object_detector, vqa_pipeline
    
    print("Loading models...")
    
    # Set environment variable for memory optimization
    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
    
    # Clear GPU memory before loading
    clear_gpu_memory()
    
    # Check available memory
    if torch.cuda.is_available():
        total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"Total GPU Memory: {total_memory:.2f}GB")
        
        # Use CPU for OCR if GPU memory is limited (< 6GB)
        if total_memory < 3.8: # Lowered threshold to allow GPU usage on 4GB cards
            print("Limited GPU memory detected. Using CPU for OCR operations.")
            device = "cpu"  # Use CPU for transformers models
            ocr_device = "cpu"  # Force CPU for OCR
        else:
            device = "cuda"
            ocr_device = "cuda"
    else:
        device = "cpu"
        ocr_device = "cpu"
    
    try:
        # Check for GPU and get total memory
        print("Loading image captioning model...")
        captioner = pipeline("image-to-text", 
                               model="microsoft/git-base",
                               torch_dtype=torch.float16,
                               device=device)
        print("Loading visual question answering model...")
        vqa_pipeline = pipeline("visual-question-answering", 
                                model="Salesforce/blip-vqa-base", # Changed to a compatible and smaller model
                                torch_dtype=torch.float16, 
                                device=device)
        print("Loading object detection model...")
        object_detector = pipeline("zero-shot-object-detection", 
                                     model="google/owlvit-base-patch32", 
                                     device=device,
                                     torch_dtype=torch.float16 if device == "cuda" else torch.float32)
        print("Loading OCR model...")
        ocr_reader = easyocr.Reader(['en'], gpu=(ocr_device == 'cuda'))

    except Exception as e:
        print(f"Error loading models: {e}")
        print("\nFalling back to CPU-only mode...")
        # Clear any partial models from GPU
        clear_gpu_memory()
        # Fallback to CPU-only mode
        if not captioner:
            # Load models on CPU
            print("Loading image captioning model...")
            captioner = pipeline("image-to-text", model="microsoft/git-base", device="cpu")
        if not ocr_reader:
            ocr_reader = easyocr.Reader(['en'], gpu=False)
        if not vqa_pipeline:
            print("Loading visual question answering model...")
            vqa_pipeline = pipeline("visual-question-answering", model="microsoft/git-base-vqav2", device="cpu")
        if not object_detector:
            print("Loading object detection model...")
            object_detector = pipeline("zero-shot-object-detection", model="google/owlvit-base-patch32", device="cpu")
            
    # Clear memory after loading
    clear_gpu_memory()
    get_device_info()
    print("Models loaded.")

def describe_scene(image: Image.Image) -> str:
    """Generate a caption for the image with memory management."""
    if not captioner:
        raise RuntimeError("Captioning model not loaded.")
    
    try:
        # Clear memory before processing
        clear_gpu_memory()
        
        # Resize image if too large to save memory
        max_size = 512
        if max(image.size) > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        results = captioner(image)
        
        # Clear memory after processing
        clear_gpu_memory()
        
        return results[0]['generated_text']
    except torch.cuda.OutOfMemoryError as e:
        print(f"GPU memory error in describe_scene: {e}")
        clear_gpu_memory()
        raise RuntimeError("GPU out of memory. Try reducing image size or switching to CPU mode.")
    except Exception as e:
        print(f"Error in describe_scene: {e}")
        clear_gpu_memory()
        raise

def read_text(image: Image.Image) -> str:
    """Read text from the image with memory management."""
    global ocr_reader
    if not ocr_reader:
        raise RuntimeError("OCR model not loaded.")
    
    try:
        # Clear memory before processing
        clear_gpu_memory()
        
        # Resize image if too large to save memory
        max_size = 1024  # OCR needs higher resolution
        if max(image.size) > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convert to numpy array
        image_np = np.array(image)
        
        # Process with OCR
        results = ocr_reader.readtext(image_np)
        
        # Clear memory after processing
        clear_gpu_memory()
        
        # Extract text from results
        text_results = [res[1] for res in results if len(res) > 1]
        return " ".join(text_results) if text_results else "No text found in the image."
        
    except torch.cuda.OutOfMemoryError as e:
        print(f"GPU memory error in read_text: {e}")
        clear_gpu_memory()
        # Try with CPU fallback
        try:
            print("Switching OCR to CPU mode...")
            ocr_reader = easyocr.Reader(['en'], gpu=False)
            image_np = np.array(image)
            results = ocr_reader.readtext(image_np)
            text_results = [res[1] for res in results if len(res) > 1]
            return " ".join(text_results) if text_results else "No text found in the image."
        except Exception as fallback_error:
            raise RuntimeError(f"OCR failed on both GPU and CPU: {fallback_error}")
    except Exception as e:
        print(f"Error in read_text: {e}")
        clear_gpu_memory()
        raise

def find_object(image: Image.Image, query: str) -> dict:
    """Find a specific object in the image with memory management."""
    if not object_detector:
        return {
            "result_text": "Object detection is not available due to memory constraints.",
            "structured_data": {"error": "model_not_loaded"}
        }
    
    try:
        # Clear memory before processing
        clear_gpu_memory()
        
        # Resize image if too large to save memory
        max_size = 512
        if max(image.size) > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        results = object_detector(image, candidate_labels=[query])
        
        # Clear memory after processing
        clear_gpu_memory()
        
        if results:
            # Return the best match
            found_object = results[0]
            confidence = found_object.get('score', 0)
            if confidence > 0.1:  # Minimum confidence threshold
                return {
                    "result_text": f"I found a {found_object['label']} with {confidence:.1%} confidence.",
                    "structured_data": {
                        "box": found_object['box'], 
                        "score": confidence,
                        "label": found_object['label']
                    }
                }
        
        return {
            "result_text": f"I could not find a {query} in the image.",
            "structured_data": {"query": query, "found": False}
        }
        
    except torch.cuda.OutOfMemoryError as e:
        print(f"GPU memory error in find_object: {e}")
        clear_gpu_memory()
        return {
            "result_text": "Object detection failed due to memory constraints.",
            "structured_data": {"error": "gpu_memory_error"}
        }
    except Exception as e:
        print(f"Error in find_object: {e}")
        clear_gpu_memory()
        return {
            "result_text": f"Error detecting objects: {str(e)}",
            "structured_data": {"error": str(e)}
        }

def answer_question(image: Image.Image, question: str) -> str:
    """Answer a question about the image with memory management."""
    if not vqa_pipeline:
        raise RuntimeError("VQA model not loaded.")
    
    try:
        # Clear memory before processing
        clear_gpu_memory()
        
        # Resize image if too large to save memory
        max_size = 512
        if max(image.size) > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        results = vqa_pipeline(image, question=question)
        
        # Clear memory after processing
        clear_gpu_memory()
        
        return results[0]['answer'] if results else "I couldn't answer that question."
        
    except torch.cuda.OutOfMemoryError as e:
        print(f"GPU memory error in answer_question: {e}")
        clear_gpu_memory()
        raise RuntimeError("GPU out of memory. Try reducing image size or switching to CPU mode.")
    except Exception as e:
        print(f"Error in answer_question: {e}")
        clear_gpu_memory()
        raise
