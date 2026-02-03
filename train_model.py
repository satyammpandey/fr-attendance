import face_recognition
import os
import pickle

DATASET_DIR = "dataset"
MODEL_FILE = "model.pkl"

known_encodings = []
known_names = []

print("[INFO] Training started...")

for person_name in os.listdir(DATASET_DIR):
    person_path = os.path.join(DATASET_DIR, person_name)

    if not os.path.isdir(person_path):
        continue

    print(f"[INFO] Processing: {person_name}")

    for img_name in os.listdir(person_path):
        img_path = os.path.join(person_path, img_name)

        image = face_recognition.load_image_file(img_path)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) == 0:
            print(f"[WARNING] No face found in {img_name}")
            continue

        known_encodings.append(encodings[0])
        known_names.append(person_name)

data = {
    "encodings": known_encodings,
    "names": known_names
}

with open(MODEL_FILE, "wb") as f:
    pickle.dump(data, f)

print("[INFO] Training completed!")
print(f"[INFO] Model saved as {MODEL_FILE}")
