"""
Face Recognition Utility Module
- Load/save face encodings
- Recognize faces from frames
- Train encodings from dataset
"""

import os
import pickle
import cv2
import numpy as np

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("⚠️  face_recognition not installed. Recognition features disabled.")
    print("   Install with: pip install face_recognition dlib cmake")

ENCODINGS_PATH = os.path.join(os.path.dirname(__file__), "encodings.pkl")
DATASET_PATH = os.path.join(os.path.dirname(__file__), "dataset")


def load_encodings():
    """Load face encodings from pickle file."""
    if not os.path.exists(ENCODINGS_PATH):
        return {"names": [], "encodings": []}
    try:
        with open(ENCODINGS_PATH, "rb") as f:
            data = pickle.load(f)
        # Validate expected dict format
        if isinstance(data, dict) and "names" in data and "encodings" in data:
            return data
    except Exception:
        pass
    return {"names": [], "encodings": []}


def save_encodings(data):
    """Save face encodings to pickle file."""
    with open(ENCODINGS_PATH, "wb") as f:
        pickle.dump(data, f)


def recognize_faces(frame, tolerance=0.5):
    """
    Recognize faces in a BGR frame.
    Returns list of dicts: {name, location, confidence}
    """
    if not FACE_RECOGNITION_AVAILABLE:
        return []

    data = load_encodings()

    if not data["encodings"]:
        return []

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    locations = face_recognition.face_locations(rgb, model="hog")
    encodings = face_recognition.face_encodings(rgb, locations)

    results = []
    for encoding, location in zip(encodings, locations):
        distances = face_recognition.face_distance(data["encodings"], encoding)
        matches = face_recognition.compare_faces(
            data["encodings"], encoding, tolerance=tolerance
        )

        name = "Unknown"
        confidence = 0.0

        if True in matches:
            best_idx = np.argmin(distances)
            if matches[best_idx]:
                name = data["names"][best_idx]
                confidence = round(1.0 - distances[best_idx], 3)

        top, right, bottom, left = location
        results.append({
            "name": name,
            "location": {"top": top, "right": right, "bottom": bottom, "left": left},
            "confidence": confidence,
        })

    return results


def train_encodings():
    """
    Walk dataset/ directory, encode all faces, and save to encodings.pkl.
    Returns dict with stats: {total_people, total_images, errors}
    """
    if not FACE_RECOGNITION_AVAILABLE:
        return {"total_people": 0, "total_images": 0, "errors": ["face_recognition not installed"]}

    if not os.path.exists(DATASET_PATH):
        os.makedirs(DATASET_PATH, exist_ok=True)
        return {"total_people": 0, "total_images": 0, "errors": []}

    known_encodings = []
    known_names = []
    errors = []

    people = [
        d for d in os.listdir(DATASET_PATH)
        if os.path.isdir(os.path.join(DATASET_PATH, d))
    ]

    for person_name in people:
        person_dir = os.path.join(DATASET_PATH, person_name)
        images = [
            f for f in os.listdir(person_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]

        for img_file in images:
            img_path = os.path.join(person_dir, img_file)
            try:
                image = face_recognition.load_image_file(img_path)
                face_encs = face_recognition.face_encodings(image)
                if face_encs:
                    known_encodings.append(face_encs[0])
                    known_names.append(person_name)
                else:
                    errors.append(f"No face found in {img_path}")
            except Exception as e:
                errors.append(f"Error processing {img_path}: {str(e)}")

    data = {"names": known_names, "encodings": known_encodings}
    save_encodings(data)

    return {
        "total_people": len(people),
        "total_images": len(known_encodings),
        "errors": errors,
    }


def get_registered_people():
    """Return list of registered people with image counts."""
    if not os.path.exists(DATASET_PATH):
        return []

    people = []
    for name in sorted(os.listdir(DATASET_PATH)):
        person_dir = os.path.join(DATASET_PATH, name)
        if os.path.isdir(person_dir):
            images = [
                f for f in os.listdir(person_dir)
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))
            ]
            people.append({
                "name": name.replace("_", " "),
                "folder": name,
                "image_count": len(images),
            })
    return people
