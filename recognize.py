import cv2
import face_recognition
import pickle
import pandas as pd
from datetime import datetime
import os


MODEL_FILE = "model.pkl"
ATTENDANCE_FILE = "attendance/attendance.csv"


# ---------- Check Model ----------

if not os.path.exists(MODEL_FILE):
    print("[ERROR] model.pkl not found. Train first.")
    exit()


# ---------- Load Model ----------

with open(MODEL_FILE, "rb") as f:
    data = pickle.load(f)


# ---------- Attendance Setup ----------

os.makedirs("attendance", exist_ok=True)

if not os.path.exists(ATTENDANCE_FILE):
    df = pd.DataFrame(columns=["Name", "Date", "Time"])
    df.to_csv(ATTENDANCE_FILE, index=False)


# ---------- Camera Setup ----------

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("[ERROR] Camera not accessible")
    exit()


# ---------- Variables ----------

marked_names = set()
frame_count = 0

print("[INFO] Recognition started... Press ESC to exit")


# ---------- Main Loop ----------

while True:

    ret, frame = cap.read()

    if not ret:
        print("[ERROR] Camera frame failed")
        break


    # Resize (reduce lag)
    frame = cv2.resize(frame, (640, 480))


    # Skip frames (speed boost)
    frame_count += 1
    if frame_count % 3 != 0:

        cv2.imshow("Face Attendance", frame)

        if cv2.waitKey(1) == 27:
            break

        continue


    # Convert to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


    # Detect faces
    faces = face_recognition.face_locations(rgb)
    encs = face_recognition.face_encodings(rgb, faces)


    for enc, (top, right, bottom, left) in zip(encs, faces):

        matches = face_recognition.compare_faces(
            data["encodings"],
            enc,
            tolerance=0.5
        )

        name = "Unknown"


        if True in matches:

            idx = matches.index(True)
            name = data["names"][idx]


            # Mark attendance only once
            if name not in marked_names:

                now = datetime.now()

                df = pd.DataFrame(
                    [[name, now.date(), now.strftime("%H:%M:%S")]],
                    columns=["Name", "Date", "Time"]
                )

                df.to_csv(
                    ATTENDANCE_FILE,
                    mode="a",
                    header=False,
                    index=False
                )

                marked_names.add(name)

                print(f"[INFO] Attendance marked: {name}")


        # Draw box
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
            0.9,
            (0, 255, 0),
            2
        )


    cv2.imshow("Face Attendance", frame)


    if cv2.waitKey(1) == 27:
        break


# ---------- Cleanup ----------

cap.release()
cv2.destroyAllWindows()

print("[INFO] Program closed")
