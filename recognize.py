import cv2
import csv
import os
from datetime import datetime

# Load recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer/trainer.yml")

# Face detector
detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Rebuild labels from dataset
labels = {}
dataset_path = "dataset"

for i, person_name in enumerate(os.listdir(dataset_path)):
    labels[i] = person_name

# Attendance file
attendance_file = "attendance.csv"

# Create file if not exists
if not os.path.exists(attendance_file):
    with open(attendance_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Date", "Time"])

def mark_attendance(name):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    with open(attendance_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, date, time])

cam = cv2.VideoCapture(0)

print("Attendance System Running... Press ESC to exit")

while True:
    ret, frame = cam.read()
    if not ret:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector.detectMultiScale(gray, 1.2, 5)

    for (x, y, w, h) in faces:
        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (200, 200))

        id_, confidence = recognizer.predict(face)

        if confidence < 70:
            name = labels.get(id_, "Unknown")
            mark_attendance(name)

            cv2.putText(frame, name, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Unknown", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    cv2.imshow("Face Recognition Attendance", frame)

    if cv2.waitKey(1) == 27:
        break

cam.release()
cv2.destroyAllWindows()