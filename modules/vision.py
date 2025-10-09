"""
Vision Module for Scene Description and VQA
"""
import logging
from PIL import Image
from transformers import pipeline
import torch

logger = logging.getLogger(__name__)

class VisionModule:
    def __init__(self):
        self.captioner = None
        self.vqa_pipeline = None
        self.is_initialized = False

    def load_model(self):
        if self.is_initialized:
            return
        try:
            logger.info("Loading vision models (Captioner and VQA)...")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            self.captioner = pipeline("image-to-text", 
                                      model="microsoft/git-base",
                                      device=device)
            
            self.vqa_pipeline = pipeline("visual-question-answering", 
                                         model="Salesforce/blip-vqa-base",
                                         device=device)
            self.is_initialized = True
            logger.info("Vision models loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading vision models: {e}")
            self.is_initialized = False

    def describe_scene(self, image: Image.Image) -> str:
        if not self.is_initialized or not self.captioner:
            return "Vision model not ready."
        
        results = self.captioner(image)
        return results[0]['generated_text']

    def answer_question(self, image: Image.Image, question: str) -> str:
        if not self.is_initialized or not self.vqa_pipeline:
            return "VQA model not ready."
            
        results = self.vqa_pipeline(image, question=question)
        return results[0]['answer']
