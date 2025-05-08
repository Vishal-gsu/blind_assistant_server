
import threading
import speech_recognition as sr
import pyttsx3
import time
import sys
from modules import object_detection
from modules import face as fr
from modules import weather_command

# Initialize speech recognition and text-to-speech engines
recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    """Speak the given text."""
    print(f"[Speak]: {text}")
    engine.say(text)
    engine.runAndWait()

def listen(prompt=None, timeout=5):
    """Listen for voice input with timeout."""
    if prompt:
        speak(prompt)
    
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening...")
            audio = recognizer.listen(source, timeout=timeout)
            command = recognizer.recognize_google(audio)
            print(f"[Heard]: {command}")
            return command.lower()
    except:
        return ""

# Global variable to control application state
class AppState:
    def __init__(self):
        self.is_listening = False
        self.stop_app = False

app_state = AppState()

def main():
    global app_state
    
    speak("System is active. Starting object detection.")
    
    # Start with object detection
    object_detection.detect_objects()
    
    while not app_state.stop_app:
        # Listen for wake word
        command = listen("Say 'hey alex' to access features.", timeout=5)
        
        if not command:
            continue
        
        if "hey alex" in command:
            speak("How can I help you?")
            
            # Listen for specific command
            sub_command = listen(timeout=10)
            
            if not sub_command:
                speak("No command detected. Resuming object detection.")
                object_detection.detect_objects()
                continue
            
            if "face recognition" in sub_command:
                speak("Starting face recognition. Say 'stop' to return.")
                fr.main()
                speak("Face recognition stopped. Resuming object detection.")
                object_detection.detect_objects()
            
            elif "weather" in sub_command:
                speak("Checking weather information.")
                weather_command.weather_report()
                speak("Weather report completed. Resuming object detection.")
                object_detection.detect_objects()
            
            elif "stop" in sub_command or "quit" in sub_command:
                speak("Exiting application.")
                app_state.stop_app = True
            
            else:
                speak("Unknown command. Please say: face recognition, weather, or quit to exit.")
                object_detection.detect_objects()
    
    speak("Goodbye!")

if __name__ == "__main__":
    main()