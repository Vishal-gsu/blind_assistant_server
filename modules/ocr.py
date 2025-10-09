"""
OCR Service Module - Text extraction using RapidOCR
"""
import logging
import numpy as np
from typing import List, Dict
from rapidocr_onnxruntime import RapidOCR

logger = logging.getLogger(__name__)

class OCRReader:
    def __init__(self):
        self.ocr_engine = None
        self.is_initialized = False

    def load_model(self):
        if self.is_initialized:
            return
        try:
            logger.info("Initializing OCR Service with RapidOCR...")
            self.ocr_engine = RapidOCR(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
            self.is_initialized = True
            logger.info("OCR Service initialized successfully with RapidOCR")
        except Exception as e:
            logger.error(f"Error initializing OCR Service: {e}")
            self.is_initialized = False

    def read(self, image: np.ndarray) -> List[Dict]:
        if not self.is_initialized:
            return []
        
        try:
            result, _ = self.ocr_engine(image)
            if not result:
                return []

            text_results = []
            for item in result:
                text_results.append({
                    'text': item[1],
                    'confidence': float(item[2]),
                    'box': item[0]
                })
            return text_results
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return []
