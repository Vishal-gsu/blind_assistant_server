import cv2
import face_recognition
import pickle
import os

class FaceManager:
    def __init__(self, known_faces_file="modules/known_faces.pkl"):
        self.known_faces_file = known_faces_file
        self.known_faces = self.load_known_faces()

    def load_known_faces(self):
        if os.path.exists(self.known_faces_file):
            with open(self.known_faces_file, "rb") as f:
                return pickle.load(f)
        return {}

    def save_known_faces(self):
        with open(self.known_faces_file, "wb") as f:
            pickle.dump(self.known_faces, f)

    def save_face(self, name, frame):
        face_locations = face_recognition.face_locations(frame)
        if not face_locations:
            return "No face detected in the provided image. Could not save."

        selected_face_location = None
        if len(face_locations) > 1:
            frame_height, frame_width, _ = frame.shape
            center_x, center_y = frame_width // 2, frame_height // 2
            center_region_tolerance = 0.2  # 20% tolerance

            # Check for a face in the center
            for (top, right, bottom, left) in face_locations:
                face_center_x = (left + right) // 2
                face_center_y = (top + bottom) // 2
                if (
                    abs(face_center_x - center_x) < frame_width * center_region_tolerance and
                    abs(face_center_y - center_y) < frame_height * center_region_tolerance
                ):
                    selected_face_location = (top, right, bottom, left)
                    break
            
            # If no face in the center, find the largest one
            if not selected_face_location:
                max_area = 0
                for (top, right, bottom, left) in face_locations:
                    area = (bottom - top) * (right - left)
                    if area > max_area:
                        max_area = area
                        selected_face_location = (top, right, bottom, left)
            
            face_locations = [selected_face_location]

        face_encodings = face_recognition.face_encodings(frame, face_locations)
        if face_encodings:
            self.known_faces[name] = face_encodings[0]
            self.save_known_faces()
            return f"Face of {name} saved successfully."
        else:
            return "No face detected in the provided image. Could not save."

    def recognize_person_in_frame(self, frame):
        known_face_encodings = list(self.known_faces.values())
        known_face_names = list(self.known_faces.keys())

        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        recognized_persons = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
            
            if name != "Unknown":
                recognized_persons.append(name)

        return recognized_persons