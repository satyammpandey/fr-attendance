import cv2
import face_recognition

# Open webcam
cap = cv2.VideoCapture(0)

while True:
    # Read camera frame
    ret, frame = cap.read()

    # Convert BGR to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect faces
    faces = face_recognition.face_locations(rgb)

    # Draw rectangle around face
    for (top, right, bottom, left) in faces:
        cv2.rectangle(
            frame,
            (left, top),
            (right, bottom),
            (0, 255, 0),
            2
        )

    # Show window
    cv2.imshow("Face Test", frame)

    # Press ESC to exit
    if cv2.waitKey(1) == 27:
        break

# Release camera
cap.release()
cv2.destroyAllWindows()
