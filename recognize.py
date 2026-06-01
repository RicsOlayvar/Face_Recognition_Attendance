import cv2
import csv
import os
from datetime import datetime

# Load recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer/trainer.yml")

# Face detector
detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Build labels
labels = {}
dataset_path = "dataset"

for i, person_name in enumerate(os.listdir(dataset_path)):
    labels[i] = person_name

attendance_file = "attendance.csv"

# Create file if not exists
if not os.path.exists(attendance_file):
    with open(attendance_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Date", "Time In", "Time Out"])


# =========================
# TIME IN / TIME OUT LOGIC (FIXED)
# =========================
def mark_time(name):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%I:%M:%S %p")

    rows = []
    time_in = ""
    time_out = ""

    if os.path.exists(attendance_file):
        with open(attendance_file, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)

    found = False

    for row in rows:
        if len(row) == 4:
            if row[0] == name and row[1] == date:
                time_in = row[2]
                time_out = row[3]

                # TIME OUT update
                if row[3] == "":
                    row[3] = time
                    time_out = time

                found = True
                break

    # TIME IN (new entry)
    if not found:
        rows.append([name, date, time, ""])
        time_in = time
        time_out = ""

    with open(attendance_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    return time_in, time_out


# =========================
# CAMERA START
# =========================
cam = cv2.VideoCapture(0)

print("Face Recognition Attendance Running... Press ESC to exit")

last_seen = {}  # prevents spam updates

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

            if name != "Unknown":

                # 🔥 prevent spam (only update if different moment)
                if name not in last_seen or (datetime.now().second % 5 == 0):
                    time_in, time_out = mark_time(name)
                    last_seen[name] = (time_in, time_out)
                else:
                    time_in, time_out = last_seen[name]

                # DISPLAY TEXT
                cv2.putText(frame, f"{name}", (x, y-40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                cv2.putText(frame, f"IN: {time_in}", (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

                cv2.putText(frame, f"OUT: {time_out}", (x, y+20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        else:
            cv2.putText(frame, "Unknown", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    cv2.imshow("Face Recognition Attendance", frame)

    if cv2.waitKey(1) == 27:
        break

cam.release()
cv2.destroyAllWindows()