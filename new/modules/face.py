

import cv2
import face_recognition
import pickle
import pyttsx3
import speech_recognition as sr
import os
import time

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    """Speak the given text."""
    print(f"[Speak]: {text}")
    engine.say(text)
    engine.runAndWait()

def listen(prompt=None, timeout=5):
    """Listen for voice input with timeout."""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    if prompt:
        speak(prompt)
    
    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening...")
            audio = recognizer.listen(source, timeout=timeout)
            command = recognizer.recognize_google(audio)
            print(f"[Heard]: {command}")
            return command.lower()
    except:
        return ""

def load_known_faces():
    """Load known faces from file."""
    if os.path.exists("known_faces.pkl"):
        with open("known_faces.pkl", "rb") as f:
            return pickle.load(f)
    return {}

def save_known_faces(faces):
    """Save known faces to file."""
    with open("known_faces.pkl", "wb") as f:
        pickle.dump(faces, f)

def save_face(name):
    """Save a new face to the database."""
    cap = cv2.VideoCapture(0)
    faces = load_known_faces()
    
    try:
        ret, frame = cap.read()
        if ret:
            face_encodings = face_recognition.face_encodings(frame)
            if face_encodings:
                faces[name] = face_encodings[0]
                save_known_faces(faces)
                speak(f"Face of {name} saved successfully.")
                return True
    finally:
        cap.release()
    speak("Failed to save face. No face detected.")
    return False

def delete_face(name):
    """Delete a face from the database."""
    faces = load_known_faces()
    if name in faces:
        del faces[name]
        save_known_faces(faces)
        speak(f"Face of {name} deleted successfully.")
        return True
    speak(f"No record of {name} found.")
    return False

def recognize_face():
    """Recognize face from camera."""
    cap = cv2.VideoCapture(0)
    faces = load_known_faces()
    
    try:
        ret, frame = cap.read()
        if ret:
            face_encodings = face_recognition.face_encodings(frame)
            for encoding in face_encodings:
                for name, known_encoding in faces.items():
                    match = face_recognition.compare_faces([known_encoding], encoding)
                    if match[0]:
                        speak(f"I see {name}.")
                        return name
            speak("Unknown person detected.")
            return "Unknown"
    finally:
        cap.release()

def main():
    speak("Face recognition system is active. Say your command.")
    
    while True:
        command = listen(timeout=5)
        
        if not command:
            speak("No response detected. Exiting.")
            break
        
        if "stop" in command or "quit" in command:
            speak("Exiting system.")
            break
        
        elif "save this person as" in command:
            name = command.replace("save this person as", "").strip()
            if name:
                save_face(name)
            else:
                speak("Please specify a name.")
        
        elif "delete this person" in command:
            name = command.replace("delete this person", "").strip()
            if name:
                delete_face(name)
            else:
                speak("Please specify a name.")
        
        elif "who is this" in command:
            recognize_face()
        
        else:
            speak("Unknown command. Please say: save this person as [name], delete this person [name], who is this, or stop to quit.")

if __name__ == "__main__":
    main()