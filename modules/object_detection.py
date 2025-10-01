# object_detection.py

import cv2 
from ultralytics import YOLO
import torch
import queue
import time
# REMOVED: time and face as fr are no longer needed here

ANNOUNCEMENT_COOLDOWN_SECONDS = 5

def detect_objects_worker(shutdown_event, frame_queue, results_queue):
    """
    A simple worker process that receives frames, runs detection, and returns results.
    It does NOT access any hardware.
    """
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"Object Detection Worker: Using device for YOLO: {device}")
    
    try:
        model = YOLO("yolov8n.pt").to(device)
    except Exception as e:
        print(f"Error loading YOLO model: {e}")
        return

    print("Object detection worker started.")

    try:
        while not shutdown_event.is_set():
            try:
                # Block until a frame is received from the main process
                frame = frame_queue.get(timeout=1)

                results = model(frame)
                detected_objects = set()

                for result in results:
                    for box in result.boxes:
                        if box.conf[0] > 0.6:
                            class_name = model.names[int(box.cls[0])]
                            detected_objects.add(class_name)
                
                # Send the results back to the main process
                if results_queue.empty():
                    results_queue.put(list(detected_objects))

            except queue.Empty:
                # This is normal, just means the main process hasn't sent a frame
                time.sleep(0.1) # prevent busy-waiting
                continue
            except Exception as e:
                print(f"Error in object detection worker: {e}")
    except KeyboardInterrupt:
        pass

    print("Object detection worker stopped.")