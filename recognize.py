import sys
import cv2
import csv
import os
from datetime import datetime

def create_lbph_recognizer():
    face = getattr(cv2, "face", None)
    if face is None:
        raise ImportError("cv2.face module not found. Install opencv-contrib-python")

    # common factory/function names across OpenCV versions
    candidates = [
        "LBPHFaceRecognizer_create",
        "createLBPHFaceRecognizer",
        "createLBPHFaceRecognizer_old",
    ]

    for name in candidates:
        func = getattr(face, name, None)
        if callable(func):
            return func()

    # try class constructor if present
    cls = getattr(face, "LBPHFaceRecognizer", None)
    if cls:
        try:
            return cls()
        except Exception:
            pass

    raise ImportError("LBPHFaceRecognizer not available in cv2.face; ensure opencv-contrib-python is installed")


# Load recognizer
recognizer = create_lbph_recognizer()
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
attendance_header = ["Name", "Date", "Time In", "Time Out"]

# Create file if not exists
if not os.path.exists(attendance_file):
    with open(attendance_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(attendance_header)


def read_attendance_rows():
    rows = []
    if os.path.exists(attendance_file):
        with open(attendance_file, "r", newline="") as f:
            reader = csv.reader(f)
            rows = [row for row in reader if row]

    if not rows:
        return [attendance_header]

    if rows[0] != attendance_header:
        rows[0] = attendance_header
        for idx in range(1, len(rows)):
            if len(rows[idx]) == 3:
                rows[idx].append("")
            elif len(rows[idx]) < 4:
                rows[idx] += [""] * (4 - len(rows[idx]))
    return rows


def write_attendance_rows(rows):
    with open(attendance_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


# =========================
# TIME IN / TIME OUT LOGIC
# =========================
def mark_time(name):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%I:%M:%S %p")

    rows = read_attendance_rows()
    time_in = ""
    time_out = ""
    found = False

    for idx in range(1, len(rows)):
        row = rows[idx]
        if len(row) < 4:
            row += [""] * (4 - len(row))
            rows[idx] = row

        if row[0] == name and row[1] == date:
            time_in = row[2]
            time_out = row[3]

            if row[3] == "":
                rows[idx][3] = time
                time_out = time

            found = True
            break

    if not found:
        rows.append([name, date, time, ""])
        time_in = time
        time_out = ""

    write_attendance_rows(rows)
    return time_in, time_out


# =========================
# CAMERA START
# =========================
# --cam = cv2.VideoCapture(0)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)


print("Face Recognition Attendance Running... Press ESC to exit")

last_seen = {}  # prevents spam updates

while True:
    ret, frame = cap.read()
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

cap.release()
cv2.destroyAllWindows()