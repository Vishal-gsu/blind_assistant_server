"""
Face Recognition Module - InsightFace Buffalo Model
"""
import os
import pickle
import numpy as np
import logging
from typing import List, Dict, Any
from insightface.app import FaceAnalysis
from config import INSIGHTFACE_MODEL

logger = logging.getLogger(__name__)

class FaceRecognizer:
    def __init__(self, db_path="modules/known_faces.pkl"):
        self.app = None
        self.known_embeddings = []
        self.known_names = []
        self.db_path = db_path
        self.is_initialized = False

    def load_model(self):
        if self.is_initialized:
            return
        try:
            logger.info("Initializing InsightFace with Buffalo model...")
            self.app = FaceAnalysis(name=INSIGHTFACE_MODEL, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
            self.app.prepare(ctx_id=0, det_size=(640, 640))
            self._load_database()
            self.is_initialized = True
            logger.info("InsightFace model initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing InsightFace: {e}")
            self.is_initialized = False

    def _load_database(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, 'rb') as f:
                data = pickle.load(f)
                self.known_names = data.get('names', [])
                self.known_embeddings = data.get('embeddings', [])
            logger.info(f"Loaded {len(self.known_names)} known faces from database.")
        else:
            logger.info("No existing face database found.")

    def _save_database(self):
        with open(self.db_path, 'wb') as f:
            pickle.dump({'names': self.known_names, 'embeddings': self.known_embeddings}, f)
        logger.info("Face database saved.")

    def recognize(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        if not self.is_initialized:
            return []
        
        faces = self.app.get(frame)
        recognized_faces = []
        
        if not self.known_embeddings:
            for face in faces:
                 recognized_faces.append({"name": "Unknown", "confidence": 0.0, "box": face.bbox.astype(int).tolist()})
            return recognized_faces

        for face in faces:
            embedding = face.embedding
            # Using cosine similarity
            sims = np.dot(self.known_embeddings, embedding) / (np.linalg.norm(self.known_embeddings, axis=1) * np.linalg.norm(embedding))
            best_match_idx = np.argmax(sims)
            confidence = sims[best_match_idx]

            if confidence > 0.6: # Recognition threshold
                name = self.known_names[best_match_idx]
            else:
                name = "Unknown"
            
            recognized_faces.append({
                "name": name,
                "confidence": float(confidence),
                "box": face.bbox.astype(int).tolist()
            })
        return recognized_faces

    def save_face(self, name: str, frame: np.ndarray) -> bool:
        if not self.is_initialized:
            return False
        
        faces = self.app.get(frame)
        if not faces:
            logger.warning("No face detected in frame to save.")
            return False
        
        # Use the largest face found in the frame
        largest_face = max(faces, key=lambda face: (face.bbox[2] - face.bbox[0]) * (face.bbox[3] - face.bbox[1]))
        embedding = largest_face.embedding
        
        # Normalize name
        clean_name = name.strip().title()
        
        self.known_embeddings.append(embedding)
        self.known_names.append(clean_name)
        self._save_database()
        logger.info(f"Successfully saved face for {clean_name}.")
        return True
