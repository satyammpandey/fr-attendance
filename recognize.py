import cv2
import face_recognition
import pickle
import os
import sqlite3
from datetime import datetime
import time
import sys


# ================= CONFIG =================

MODEL_FILE = "model.pkl"
DB_FILE = "attendance_system.db"
CAMERA_INDEX = 0
TOLERANCE = 0.5


# ================= DATABASE =================

def save_to_db(name):

    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()

        now = datetime.now()

        student_id = name.lower().replace(" ", "_")
        date_today = now.strftime("%Y-%m-%d")

        cur.execute("""
            INSERT OR IGNORE INTO attendance
            (student_id, name, date, time, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            student_id,
            name,
            date_today,
            now.strftime("%H:%M:%S"),
            "Present"
        ))

        conn.commit()
        conn.close()

        print(f"[DB] Saved: {name}", flush=True)

    except Exception as e:

        print(f"[DB ERROR] {e}", flush=True)


# ================= LOAD MODEL =================

if not os.path.exists(MODEL_FILE):
    print("[ERROR] model.pkl not found", flush=True)
    sys.exit(1)


with open(MODEL_FILE, "rb") as f:
    data = pickle.load(f)


known_encodings = data["encodings"]
known_names = data["names"]


# ================= CAMERA =================

def open_camera():

    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

    if not cap.isOpened():
        return None

    return cap


cap = None

while cap is None:

    cap = open_camera()

    if cap is None:
        print("[INFO] Waiting for camera...", flush=True)
        time.sleep(2)


print("[INFO] Camera started", flush=True)
print("[INFO] Press Q to quit", flush=True)


# ================= MAIN LOOP =================

marked = set()
frame_count = 0


while True:

    ret, frame = cap.read()

    if not ret:

        print("[WARNING] Camera lost, reconnecting...", flush=True)

        cap.release()
        time.sleep(1)

        cap = open_camera()
        continue


    frame = cv2.resize(frame, (640, 480))


    frame_count += 1

    if frame_count % 3 != 0:

        cv2.imshow("Face Attendance", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        continue


    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


    faces = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, faces)


    for enc, (top, right, bottom, left) in zip(encodings, faces):

        matches = face_recognition.compare_faces(
            known_encodings,
            enc,
            tolerance=TOLERANCE
        )

        name = "Unknown"


        if True in matches:

            index = matches.index(True)
            name = known_names[index]


            if name not in marked:

                marked.add(name)

                save_to_db(name)

                print(f"[INFO] Marked: {name}", flush=True)


        # Draw face box
        cv2.rectangle(
            frame,
            (left, top),
            (right, bottom),
            (0, 255, 0),
            2
        )


        # Show name
        cv2.putText(
            frame,
            name,
            (left, top - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )


    cv2.imshow("Face Attendance", frame)


    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ================= CLEANUP =================

print("[INFO] Closing camera...", flush=True)

cap.release()
cv2.destroyAllWindows()

print("[INFO] Recognition stopped", flush=True)
