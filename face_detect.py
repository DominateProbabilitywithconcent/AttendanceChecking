# face_detect.py

# === STANDARD LIB IMPORTS ===
import os

# === IMAGE HANDLING IMPORTS ===
import cv2
import numpy as np
import face_recognition
from deepface import DeepFace

# === LOCAL IMPORTS ===
import config
import attendance

# === LOAD KNOWN FACES ON STARTUP ===
class_data = {}  # { class_name: { name: encoding } }
known_encodings = []
known_names = []
current_class = None

def load_class_data():
    global class_data, known_encodings, known_names
    class_data.clear()
    known_encodings.clear()
    known_names.clear()
    
    print("[!] Loading class data...")  # Debug print
    
    # Get all class folders
    for class_name in os.listdir("known_faces"):
        class_path = os.path.join("known_faces", class_name)
        if os.path.isdir(class_path):
            class_data[class_name] = {}
            print(f"[ ] Loading class: {class_name}")  # Debug print
            # Load student images for this class
            for file in os.listdir(class_path):
                if file.lower().endswith((".jpg", ".png")):
                    try:
                        image = face_recognition.load_image_file(os.path.join(class_path, file))
                        encoding = face_recognition.face_encodings(image)[0]
                        student_name = os.path.splitext(file)[0]
                        class_data[class_name][student_name] = encoding
                        print(f"[✓] Loaded student: {student_name}")  # Debug print
                    except Exception as e:
                        if config.DEBUG: print(f"[!] Error loading {file}: {e}")
    
    print(f"[✓] Loaded {len(class_data)} classes")  # Debug print

def set_current_class(class_name):
    global current_class, known_encodings, known_names
    if class_name in class_data:
        current_class = class_name
        known_encodings.clear()
        known_names.clear()
        for student_name, encoding in class_data[class_name].items():
            known_encodings.append(encoding)
            known_names.append(f"{class_name}/{student_name}")
        return True
    return False

def get_available_classes():
    return list(class_data.keys())

def get_class_students(class_name):
    if class_name in class_data:
        return list(class_data[class_name].keys())
    return []

# === FACE DETECTION ===
scale_factor = 2    # Downscale image to reduce processing time

def get_face_locations(frame):  # Detect face locations in frame (resized for performance)
    small_frame = cv2.resize(frame, (0, 0), fx=1/scale_factor, fy=1/scale_factor) # Downscale for performance
    locations = face_recognition.face_locations(small_frame, model="hog")
    return [(top * scale_factor, right * scale_factor, bottom * scale_factor, left * scale_factor) 
            for top, right, bottom, left in locations]   # Rescale to original size

def extract_faces(frame, face_locations):   # Extract face encodings for each face location
    encodings = []
    for loc in face_locations:
        encoding = face_recognition.face_encodings(frame, [loc])
        if encoding:
            encodings.append(encoding[0])
        else:
            if config.DEBUG: print(f"[!] No encoding found for face at {loc}")
    return encodings

# === FACE RECOGNITION ===
def recognize_faces(encodings): # Match encodings against known encodings to identify names
    recognized = []
    for encoding in encodings:
        name = "Unknown"
        face_distances = face_recognition.face_distance(known_encodings, encoding)
        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if face_distances[best_match_index] < 0.6:
                name = known_names[best_match_index]
        recognized.append(name)
    return recognized

# === EMOTION ANALYSIS ===
def analyze_emotions(frame, face_locations):    # Analyze emotion of each detected face using DeepFace
    emotions = []
    for (top, right, bottom, left) in face_locations:
        face_img = frame[top:bottom, left:right]
        try:
            analysis = DeepFace.analyze(face_img, actions=['emotion'], enforce_detection=False)
            emotions.append(analysis[0]['dominant_emotion'])
        except:
            emotions.append("N/A")
    return emotions

# === COMBINE RESULTS & HANDLE ATTENDANCE ===
def combine_results(locations, names, emotions):    # Combine name, emotion, location, and check attendance logging
    result = []
    for (loc, name, emotion) in zip(locations, names, emotions):
        if name != "Unknown":
            class_name, student_name = name.split("/")
            name_display = student_name.replace("_", " ")
            just_logged = attendance.add(class_name, student_name)
            result.append((*loc, name_display, emotion, just_logged))
            if config.DEBUG: print(f"[!] Recognized: {name_display} ({class_name}), emotion: {emotion}")
        else:
            result.append((*loc, "Unknown", emotion, False))
    return result

# === MAIN FUNCTION CALLED BY GUI ===
def process_frame(frame):   # Full pipeline: detect faces → extract → recognize → analyze emotion → combine
    if current_class is None:
        return []
        
    face_locations = get_face_locations(frame)
    
    try:
        face_encodings = extract_faces(frame, face_locations)
    except IndexError as e:
        if config.DEBUG: print(f"[!] Encoding error: {e}")
        return []

    names = recognize_faces(face_encodings)
    emotions = analyze_emotions(frame, face_locations)
    results = combine_results(face_locations, names, emotions)
    return results

# Initialize class data on startup
load_class_data()
