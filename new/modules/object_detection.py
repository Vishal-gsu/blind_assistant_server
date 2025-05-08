
import cv2
from ultralytics import YOLO
import pyttsx3
import time
import speech_recognition as sr

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    """Speak the given text."""
    engine.say(text)
    engine.runAndWait()

# Initialize speech recognition
recognizer = sr.Recognizer()

# Load YOLOv8 model
model = YOLO("yolov8n.pt")  # Make sure the file is present in the modules directory

def listen_for_command(timeout=5):
    """Listen for voice command with timeout."""
    try:
        with sr.Microphone() as source:
            print("Listening for command...")
            audio = recognizer.listen(source, timeout=timeout)
            command = recognizer.recognize_google(audio)
            print(f"[Heard]: {command}")
            return command.lower()
    except:
        return ""

def detect_objects():
    cap = cv2.VideoCapture(0)
    last_announcement_time = 0
    last_detected = set()

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    speak("YOLO object detection started. Say 'stop' to quit.")

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

        # Listen for command after announcement
        if last_detected:
            command = listen_for_command(timeout=5)
            if "stop" in command:
                break

        cv2.waitKey(1)

    speak("Exiting object detection.")
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_objects()