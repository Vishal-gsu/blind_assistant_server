# import cv2
# import numpy as np
# import tensorflow as tf
# from tensorflow.keras.applications import MobileNetV2
# from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions

# # Load pre-trained MobileNetV2 model
# model = MobileNetV2(weights='imagenet')

# # Initialize the camera
# cap = cv2.VideoCapture(0)

# # Function to detect objects
# def detect_objects(frame):
#     # Resize the frame to the input size of the model
#     input_frame = cv2.resize(frame, (224, 224))
#     input_frame = np.expand_dims(input_frame, axis=0)
#     input_frame = preprocess_input(input_frame)

#     # Predict the objects in the frame
#     predictions = model.predict(input_frame)
#     results = decode_predictions(predictions, top=1)[0]

#     # Get the object name and confidence
#     object_name = results[0][1]
#     confidence = results[0][2]

#     return object_name, confidence

# # Function to speak the detected object
# def speak(text):
#     import pyttsx3
#     engine = pyttsx3.init()
#     engine.say(text)
#     engine.runAndWait()

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     object_name, confidence = detect_objects(frame)
#     confidence = confidence * 100

#     # Display the detected object and confidence on the frame
#     cv2.putText(frame, f"{object_name} ({confidence:.2f}%)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

#     # Speak the detected object
#     speak(f"I detected a {object_name} with {confidence:.2f}% confidence")

#     # Display the frame
#     cv2.imshow('Object Detection', frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()

import cv2
from ultralytics import YOLO
import pyttsx3
import time

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    """Speak the given text."""
    engine.say(text)
    engine.runAndWait()

# Load YOLOv8 model
model = YOLO("yolov8n.pt")  # Make sure the file is present

def detect_objects():
    cap = cv2.VideoCapture(0)
    last_announcement_time = 0
    last_detected = set()

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    speak("YOLO object detection started. Press Q to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image.")
            break

        # Perform detection
        results = model(frame)
        detected_objects = set()

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                detected_objects.add(class_name)

        # Throttle voice output to every 3 seconds
        current_time = time.time()
        if detected_objects and (current_time - last_announcement_time > 3):
            if detected_objects != last_detected:  # Avoid repeating same output
                objects_text = ", ".join(detected_objects)
                print("Detected:", objects_text)
                speak(f"I see: {objects_text}")
                last_announcement_time = current_time
                last_detected = detected_objects.copy()

        # Show annotated frame
        annotated_frame = results[0].plot()
        cv2.imshow("YOLO Object Detection", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    speak("Exiting object detection.")
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_objects()

