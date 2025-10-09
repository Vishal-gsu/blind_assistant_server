"""
Object Detection Module - YOLOv9 + MIDAS Depth Estimation
"""
import cv2
import numpy as np
import torch
import logging
from typing import List, Dict, Any
from ultralytics import YOLO
from config import YOLO_MODEL_PATH, MIDAS_MODEL_TYPE

logger = logging.getLogger(__name__)

class ObjectDetector:
    def __init__(self):
        self.yolo_model = None
        self.midas_model = None
        self.midas_transform = None
        self.device = None
        self.is_initialized = False

    def load_model(self):
        """Initialize YOLOv9 and MIDAS models"""
        if self.is_initialized:
            return
        try:
            logger.info(f"Loading YOLO model from {YOLO_MODEL_PATH}...")
            self.yolo_model = YOLO(YOLO_MODEL_PATH)
            logger.info("YOLO model loaded successfully")

            logger.info(f"Loading MIDAS {MIDAS_MODEL_TYPE} model...")
            self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
            self.midas_model = torch.hub.load("intel-isl/MiDaS", MIDAS_MODEL_TYPE, trust_repo=True).to(self.device)
            self.midas_model.eval()

            midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms", trust_repo=True)
            self.midas_transform = midas_transforms.dpt_transform if MIDAS_MODEL_TYPE in ["DPT_Large", "DPT_Hybrid"] else midas_transforms.small_transform
            
            logger.info(f"MIDAS model loaded successfully on {self.device}")
            self.is_initialized = True
            logger.info("ObjectDetector initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ObjectDetector: {e}")
            self.is_initialized = False

    def calculate_object_depth(self, depth_map, box):
        """Calculate depth of a detected object."""
        try:
            x1, y1, x2, y2 = map(int, box)
            depth_region = depth_map[y1:y2, x1:x2]
            return np.mean(depth_region) if depth_region.size > 0 else 0
        except Exception as e:
            logger.error(f"Error calculating object depth: {e}")
            return 0

    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect objects with depth estimation."""
        if not self.is_initialized:
            return []
        
        try:
            # YOLOv9 object detection
            results = self.yolo_model(frame, imgsz=640, verbose=False)
            
            # MIDAS depth estimation
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            input_batch = self.midas_transform(img_rgb).to(self.device)
            
            with torch.no_grad():
                prediction = self.midas_model(input_batch)
                prediction = torch.nn.functional.interpolate(
                    prediction.unsqueeze(1),
                    size=img_rgb.shape[:2],
                    mode="bicubic",
                    align_corners=False,
                ).squeeze()
            depth_map = prediction.cpu().numpy()

            detected_objects = []
            boxes = results[0].boxes.xyxy.cpu().tolist()
            classes = results[0].boxes.cls.cpu().tolist()
            confidences = results[0].boxes.conf.cpu().tolist()
            names = results[0].names

            for box, cls, conf in zip(boxes, classes, confidences):
                if conf > 0.3:
                    depth = self.calculate_object_depth(depth_map, box)
                    detected_objects.append({
                        "name": names.get(cls, "Unknown"),
                        "confidence": conf,
                        "box": box,
                        "depth_m": float(depth) 
                    })
            
            return detected_objects
        except Exception as e:
            logger.error(f"Error in object detection: {e}")
            return []
