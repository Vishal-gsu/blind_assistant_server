# import cv2
# import face_recognition
# import pickle
# import os
# import pyttsx3

# # === Constants ===
# FACE_DATA_FILE = "face_data.pkl"

# # === Initialize TTS engine ===
# engine = pyttsx3.init()

# def speak(text):
#     """Speak the given text."""
#     print(f"[Speak]: {text}")
#     engine.say(text)
#     engine.runAndWait()

# # === Load known faces ===
# if os.path.exists(FACE_DATA_FILE):
#     with open(FACE_DATA_FILE, "rb") as file:
#         known_faces = pickle.load(file)
#     speak(f"{len(known_faces)} known faces loaded.")
# else:
#     known_faces = {}
#     speak("No known faces found. Starting fresh.")

# # === Save Face ===
# def save_face(name, encoding):
#     """Save a new face to the database."""
#     known_faces[name] = encoding
#     with open(FACE_DATA_FILE, "wb") as file:
#         pickle.dump(known_faces, file)
#     speak(f"Face of {name} saved successfully.")
#     print(f"[INFO] Saved face for {name}")

# # === Delete Face ===
# def delete_face(name):
#     """Delete a face from the database."""
#     if name in known_faces:
#         del known_faces[name]
#         with open(FACE_DATA_FILE, "wb") as file:
#             pickle.dump(known_faces, file)
#         speak(f"Face of {name} deleted successfully.")
#         print(f"[INFO] Deleted face for {name}")
#     else:
#         speak(f"Face of {name} not found.")

# # === Main function ===
# def main():
#     cap = cv2.VideoCapture(0)

#     if not cap.isOpened():
#         speak("Error: Could not access the camera.")
#         return

#     speak("Face recognition system is active.")

#     already_spoken_names = set()

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("[ERROR] Failed to grab frame.")
#             break

#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         for face_encoding, face_location in zip(face_encodings, face_locations):
#             name = "Unknown"
#             min_distance = 0.6

#             for saved_name, saved_encoding in known_faces.items():
#                 matches = face_recognition.compare_faces([saved_encoding], face_encoding, tolerance=0.5)
#                 if matches[0]:
#                     face_distance = face_recognition.face_distance([saved_encoding], face_encoding)[0]
#                     if face_distance < min_distance:
#                         name = saved_name
#                         min_distance = face_distance

#             top, right, bottom, left = face_location
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
#             cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

#             if name != "Unknown" and name not in already_spoken_names:
#                 speak(f"{name} detected.")
#                 already_spoken_names.add(name)
#             elif name == "Unknown":
#                 speak("Unknown person detected.")

#         # Display frame
#         cv2.imshow("Face Recognition", frame)

#         # Check for user command via keyboard input
#         print("Waiting for command: 'save', 'delete', 'quit'")
#         command = input("Enter a command (save, delete, quit): ").lower()

#         if command:
#             if "save" in command:
#                 if face_encodings:
#                     name = input("Please type the name to save: ")
#                     if name:
#                         save_face(name, face_encodings[0])
#                         already_spoken_names.clear()
#                     else:
#                         speak("Name input failed.")
#                 else:
#                     speak("No face detected. Try again.")

#             elif "delete" in command:
#                 name = input("Please type the name to delete: ")
#                 if name:
#                     delete_face(name)
#                     already_spoken_names.clear()
#                 else:
#                     speak("Name input failed.")

#             elif "quit" in command or "exit" in command:
#                 speak("Exiting face recognition system.")
#                 break

#     cap.release()
#     cv2.destroyAllWindows()

# # === Entry Point ===
# if __name__ == "__main__":
#     main()


import cv2
import face_recognition
import pickle
import os
import pyttsx3
import speech_recognition as sr

# Fix OpenCV backend issues
os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'

# === Constants ===
FACE_DATA_FILE = "face_data.pkl"

# === Initialize TTS engine ===
engine = pyttsx3.init()

def speak(text):
    """Speak the given text."""
    print(f"[Speak]: {text}")
    engine.say(text)
    engine.runAndWait()

def listen(prompt=None, timeout=5, phrase_time_limit=4):
    """Try to capture voice input. Fallback to typed input on failure."""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    if prompt:
        speak(prompt)

    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening...")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            command = recognizer.recognize_google(audio)
            print(f"[Heard]: {command}")
            return command.lower()
    except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
        speak("Couldn't understand. Please type your response.")
        return input("Type your response: ").lower()

# === Load known faces ===
if os.path.exists(FACE_DATA_FILE):
    with open(FACE_DATA_FILE, "rb") as file:
        known_faces = pickle.load(file)
    speak(f"{len(known_faces)} known faces loaded.")
else:
    known_faces = {}
    speak("No known faces found. Starting fresh.")

# === Save Face ===
def save_face(name, encoding):
    """Save a new face to the database."""
    known_faces[name] = encoding
    with open(FACE_DATA_FILE, "wb") as file:
        pickle.dump(known_faces, file)
    speak(f"Face of {name} saved successfully.")
    print(f"[INFO] Saved face for {name}")

# === Delete Face ===
def delete_face(name):
    """Delete a face from the database."""
    if name in known_faces:
        del known_faces[name]
        with open(FACE_DATA_FILE, "wb") as file:
            pickle.dump(known_faces, file)
        speak(f"Face of {name} deleted successfully.")
        print(f"[INFO] Deleted face for {name}")
    else:
        speak(f"Face of {name} not found.")

# === Main Function ===
def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        speak("Error: Could not access the camera.")
        return

    speak("Face recognition system is active.")
    already_spoken_names = set()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] Failed to grab frame.")
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for face_encoding, face_location in zip(face_encodings, face_locations):
                name = "Unknown"
                min_distance = 0.6

                for saved_name, saved_encoding in known_faces.items():
                    matches = face_recognition.compare_faces([saved_encoding], face_encoding, tolerance=0.5)
                    if matches[0]:
                        face_distance = face_recognition.face_distance([saved_encoding], face_encoding)[0]
                        if face_distance < min_distance:
                            name = saved_name
                            min_distance = face_distance

                top, right, bottom, left = face_location
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                if name != "Unknown" and name not in already_spoken_names:
                    speak(f"{name} detected.")
                    already_spoken_names.add(name)
                elif name == "Unknown":
                    speak("Unknown person detected.")

            # Display frame with error handling
            try:
                cv2.imshow("Face Recognition", frame)
            except Exception as e:
                print(f"Display error: {e}")
                speak("Camera display error")
                break

            # Command options
            print("Waiting for command: '1' (save), '2' (delete), '3' (quit)")
            command = listen("Say 1 to save, 2 to delete, or 3 to quit.")

            if command:
                if "1" in command:
                    if face_encodings:
                        name = listen("Please say or type the name to save.")
                        if name:
                            save_face(name, face_encodings[0])
                            already_spoken_names.clear()
                        else:
                            speak("Name input failed.")
                    else:
                        speak("No face detected. Try again.")

                elif "2" in command:
                    name = listen("Please say or type the name to delete.")
                    if name:
                        delete_face(name)
                        already_spoken_names.clear()
                    else:
                        speak("Name input failed.")

                elif "3" in command:
                    speak("Exiting face recognition system.")
                    break

    finally:
        cap.release()
        cv2.destroyAllWindows()

# === Entry Point ===
if __name__ == "__main__":
    main()
