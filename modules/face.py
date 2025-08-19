import cv2
import face_recognition
import pickle
import os
import time


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

# Modified save_face: now accepts a frame directly
def save_face(name, frame, speak):
    """Save a new face to the database from a provided frame."""
    faces = load_known_faces()

    face_encodings = face_recognition.face_encodings(frame)
    if face_encodings:
        faces[name] = face_encodings[0]
        save_known_faces(faces)
        speak(f"Face of {name} saved successfully.")
        return True
    else:
        speak("No face detected in the provided image. Could not save.")
        return False



def recognize_person_in_frame(frame):
    """Recognize face from a single frame."""
    faces = load_known_faces()
    known_face_encodings = list(faces.values())
    known_face_names = list(faces.keys())

    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        return name
    return "Unknown"
