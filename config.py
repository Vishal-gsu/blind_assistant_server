"""
Configuration file for the Blind Assistive System
This file centralizes the model names and other settings.
"""

# Object Detection (YOLO)
# Path to the YOLO model file. Using the one from your friend's project.
YOLO_MODEL_PATH = "yolov9c.pt"

# Depth Estimation (MiDaS)
# Options: "DPT_Large", "DPT_Hybrid", "MiDaS_small"
MIDAS_MODEL_TYPE = "DPT_Large"

# Face Recognition (InsightFace)
# Options: "buffalo_l", "buffalo_s"
INSIGHTFACE_MODEL = "buffalo_l"
