import collections
import os
import threading
import multiprocessing
import queue
import time
import pyttsx3
import cv2
from modules import object_detection, ocr
from modules.face import FaceManager
from modules.llm import get_intent, get_response, set_default_city
from modules.listening import VoiceCommandManager

class BlindAssistiveSystem:
    def __init__(self):
        self.shutdown_event = multiprocessing.Event()
        self.frame_to_process_queue = multiprocessing.Queue(maxsize=1)
        self.results_from_process_queue = multiprocessing.Queue()
        self.command_queue = queue.Queue()
        self.speak_queue = queue.Queue()
        self.conversation_state = None
        self.last_detected_objects = {}
        self.last_announced_objects = {}
        self.detection_interval = 7  # seconds
        self.last_detection_time = 0
        self.last_face_recognition_time = 0
        self.last_seen_persons = {}
        self.face_recognition_interval = 60  # 1 minute
        self.voice_manager = VoiceCommandManager(self.shutdown_event, self.command_queue, self.speak_queue)
        self.face_manager = FaceManager()
        self.object_detection_process = multiprocessing.Process(
            target=object_detection.detect_objects_worker,
            args=(self.shutdown_event, self.frame_to_process_queue, self.results_from_process_queue)
        )
        self.voice_command_thread = threading.Thread(target=self.voice_manager.run, daemon=True)
        self.speaking_thread = threading.Thread(target=self.run_speaking)

    def run_speaking(self):
        engine = pyttsx3.init()
        while not self.shutdown_event.is_set():
            try:
                text = self.speak_queue.get(timeout=1)
                print(f"[Speak]: {text}")
                engine.say(text)
                engine.runAndWait()
            except queue.Empty:
                continue
        print("Speaking thread stopped.")

    def start(self):
        if not os.getenv("GROQ_API_KEY"):
            print("GROQ_API_KEY not set. Please create a .env file.")
            self.speak_queue.put("GROQ API key is not set. Please configure the application.")
            return
        
        if not os.getenv("WEATHER_API_KEY"):
            print("WEATHER_API_KEY not set. Weather feature will be disabled.")
            self.speak_queue.put("Weather API key is not set. Weather feature will be disabled.")

        self.object_detection_process.start()
        self.voice_command_thread.start()
        self.speaking_thread.start()

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.speak_queue.put("Critical Error: Could not open camera.")
            self.shutdown_event.set()

        last_announcement_time = 0

        try:
            while not self.shutdown_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    self.speak_queue.put("Error reading camera frame.")
                    time.sleep(1)
                    continue

                current_time = time.time()
                if current_time - self.last_detection_time >= self.detection_interval:
                    if self.frame_to_process_queue.empty():
                        self.frame_to_process_queue.put(frame)
                        self.last_detection_time = current_time

                try:
                    detected_objects_list = self.results_from_process_queue.get_nowait()
                    self.last_detected_objects = collections.Counter(detected_objects_list)
                    
                    if self.last_detected_objects != self.last_announced_objects:
                        announcement = "I see: "
                        items = []
                        for obj, count in self.last_detected_objects.items():
                            if count > 1:
                                items.append(f"{count} {obj}s")
                            else:
                                items.append(f"a {obj}")
                        announcement += ", ".join(items)
                        self.speak_queue.put(announcement)
                        self.last_announced_objects = self.last_detected_objects

                except queue.Empty:
                    pass

                # Continuous Face Recognition
                if current_time - self.last_face_recognition_time >= self.detection_interval:
                    recognized_persons = self.face_manager.recognize_person_in_frame(frame)
                    for name in recognized_persons:
                        last_seen = self.last_seen_persons.get(name)
                        if not last_seen or (current_time - last_seen) > self.face_recognition_interval:
                            self.speak_queue.put(f"I see {name}.")
                            self.last_seen_persons[name] = current_time
                    self.last_face_recognition_time = current_time

                try:
                    command = self.command_queue.get_nowait()
                    if self.conversation_state == "waiting_for_face_name":
                        self.conversation_state = None
                        response = self.face_manager.save_face(command, frame)
                        self.speak_queue.put(response)
                        continue
                    
                    intent = get_intent(command)
                    
                    intent_handlers = {
                        "exit": self.handle_exit,
                        "save_face": self.handle_save_face,
                        "face_recognition": self.handle_recognize_face,
                        "ocr": self.handle_read_text,
                        "object_detection": self.handle_object_detection,
                        "weather": self.handle_weather,
                        "set_city": self.handle_set_city,
                        "unknown": self.handle_unknown
                    }
                    
                    handler = intent_handlers.get(intent)
                    if handler:
                        handler(command, frame)
                    else:
                        self.handle_unknown(command)
                        
                except queue.Empty:
                    pass
                
        except KeyboardInterrupt:
            self.shutdown_event.set()

        print("Shutdown signal received! Waiting for processes to terminate...")
        cap.release()
        self.object_detection_process.join(timeout=5)
        self.speaking_thread.join(timeout=2)
        
        if self.object_detection_process.is_alive():
            self.object_detection_process.terminate()
        print("Application stopped.")

    def handle_exit(self, command=None, frame=None):
        self.speak_queue.put("Goodbye!")
        self.shutdown_event.set()

    def handle_save_face(self, command=None, frame=None):
        recognized_persons = self.face_manager.recognize_person_in_frame(frame)
        if recognized_persons:
            self.speak_queue.put(f"I already know this person as {', '.join(recognized_persons)}.")
            return
            
        self.speak_queue.put("What is the name of the person?")
        self.conversation_state = "waiting_for_face_name"

    def handle_recognize_face(self, command=None, frame=None):
        names = self.face_manager.recognize_person_in_frame(frame)
        if names:
            self.speak_queue.put(f"I see {', '.join(names)}.")
        else:
            self.speak_queue.put("I don't recognize anyone.")

    def handle_read_text(self, command=None, frame=None):
        self.speak_queue.put("Starting text recognition.")
        text = ocr.read_text_from_frame(frame)
        if text:
            self.speak_queue.put(f"I read: {text}")
        else:
            self.speak_queue.put("I couldn't read any text.")

    def handle_object_detection(self, command=None, frame=None):
        if self.frame_to_process_queue.empty():
            self.frame_to_process_queue.put(frame)
            self.last_detection_time = time.time()
        
        if self.last_detected_objects:
            announcement = "I currently see: "
            items = []
            for obj, count in self.last_detected_objects.items():
                if count > 1:
                    items.append(f"{count} {obj}s")
                else:
                    items.append(f"a {obj}")
            announcement += ", ".join(items)
            self.speak_queue.put(announcement)
        else:
            self.speak_queue.put("I don't see any objects right now.")

    def handle_llm_request(self, command, intent):
        try:
            reply, city = get_response(command, intent)
            if intent == "set_city" and city:
                set_default_city(city)
                self.speak_queue.put(f"Location set to {city}.")
            else:
                self.speak_queue.put(reply)
        except Exception as e:
            print(f"Error in LLM request: {e}")
            self.speak_queue.put("Sorry, I am having trouble with that request.")

    def handle_weather(self, command, frame=None):
        if not os.getenv("WEATHER_API_KEY"):
            self.speak_queue.put("The weather feature is disabled. Please set the WEATHER_API_KEY.")
            return
        threading.Thread(target=self.handle_llm_request, args=(command, "weather")).start()

    def handle_set_city(self, command, frame=None):
        if not os.getenv("WEATHER_API_KEY"):
            self.speak_queue.put("The weather feature is disabled. Please set the WEATHER_API_KEY.")
            return
        threading.Thread(target=self.handle_llm_request, args=(command, "set_city")).start()

    def handle_unknown(self, command, frame=None):
        threading.Thread(target=self.handle_llm_request, args=(command, "unknown")).start()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = BlindAssistiveSystem()
    app.start()