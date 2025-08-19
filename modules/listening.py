# listening.py

import speech_recognition as sr
import queue
import time

class VoiceCommandManager:
    # CHANGED: Takes a shutdown_event instead of app_state
    def __init__(self, shutdown_event, command_queue, speak_queue):
        self.shutdown_event = shutdown_event
        self.command_queue = command_queue
        self.speak_queue = speak_queue
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

    def _speak(self, text):
        self.speak_queue.put(text)

    def _listen_for_command(self, source):
        try:
            print("Active listening: Now listening for a command...")
            self._speak("I'm listening.")
            
            audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("Active listening: Processing audio...")
            command = self.recognizer.recognize_google(audio)
            print(f"[Heard Command]: {command}")
            if command:
                self.command_queue.put(command.lower())
                
        except sr.UnknownValueError:
            self._speak("Sorry, I didn't catch that.")
        except sr.WaitTimeoutError:
            self._speak("I didn't hear a command.")
        except sr.RequestError as e:
            self._speak("Sorry, my speech service is down.")
            print(f"Speech Recognition service error; {e}")

    def run(self):
        self._speak("System is active. Say 'Iris' to give a command.")
        
        with self.microphone as source:
            print("Background listener: Calibrating...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
            print("Background listener: Calibration complete. Listening for 'Iris'...")

            # CHANGED: Main loop checks the event
            try:
                while not self.shutdown_event.is_set():
                    try:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                        text = self.recognizer.recognize_google(audio, show_all=False, language="en-US")
                        
                        print(f"[Heard Background]: {text}")
                        if "iris" in text.lower():
                            print("Wake word 'Iris' detected!")
                            self._listen_for_command(source)
                            print("Background listener: Resuming listening for 'Iris'...")

                    except sr.WaitTimeoutError:
                        time.sleep(0.1) # prevent busy-waiting
                        pass
                    except sr.UnknownValueError:
                        pass
                    except sr.RequestError as e:
                        print(f"Could not request results; {e}")
                        time.sleep(2)
            except KeyboardInterrupt:
                pass

        print("Voice command manager stopped.")