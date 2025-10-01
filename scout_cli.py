# main.py

import threading
import multiprocessing
import queue
import time
import pyttsx3
import cv2
from modules import object_detection, face as fr, ocr
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
        self.last_detected_objects = set()
        self.detection_interval = 5  # seconds
        self.last_detection_time = 0

        self.voice_manager = VoiceCommandManager(self.shutdown_event, self.command_queue, self.speak_queue)

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
                    detected_objects = self.results_from_process_queue.get_nowait()
                    self.last_detected_objects = set(detected_objects)
                    
                    if current_time - last_announcement_time > self.detection_interval:
                        if self.last_detected_objects:
                            self.speak_queue.put(f"I see: {', '.join(self.last_detected_objects)}")
                            last_announcement_time = current_time

                except queue.Empty:
                    pass

                try:
                    command = self.command_queue.get_nowait()
                    if self.conversation_state == "waiting_for_face_name":
                        self.conversation_state = None
                        if fr.recognize_person_in_frame(frame) != "Unknown":
                            fr.save_face(command, frame, lambda text: self.speak_queue.put(text))
                        else:
                            self.speak_queue.put("Sorry, I lost sight of the person. Please try again.")
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
        if fr.recognize_person_in_frame(frame) != "Unknown":
            self.speak_queue.put("I already know this person.")
            return
            
        self.speak_queue.put("What is the name of the person?")
        self.conversation_state = "waiting_for_face_name"

    def handle_recognize_face(self, command=None, frame=None):
        name = fr.recognize_person_in_frame(frame)
        self.speak_queue.put(f"I see {name}.")

    def handle_read_text(self, command=None, frame=None):
        ocr_thread = threading.Thread(target=self.run_ocr)
        ocr_thread.start()

    def handle_object_detection(self, command=None, frame=None):
        if self.frame_to_process_queue.empty():
            self.frame_to_process_queue.put(frame)
            self.last_detection_time = time.time()
        
        if self.last_detected_objects:
            self.speak_queue.put(f"I currently see: {', '.join(self.last_detected_objects)}")
        else:
            self.speak_queue.put("I don't see any objects right now.")

    def handle_weather(self, command, frame=None):
        reply, _ = get_response(command, "weather")
        self.speak_queue.put(reply)

    def handle_set_city(self, command, frame=None):
        reply, city = get_response(command, "set_city")
        if city:
            set_default_city(city)
            self.speak_queue.put(f"Location set to {city}.")
        else:
            self.speak_queue.put(reply)

    def handle_unknown(self, command, frame=None):
        reply, _ = get_response(command, "unknown")
        self.speak_queue.put(reply)

    def run_ocr(self):
        text = ocr.read_text_from_camera()
        if text:
            self.speak_queue.put(f"I read: {text}")
        else:
            self.speak_queue.put("I couldn't read any text.")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = BlindAssistiveSystem()
    app.start()
