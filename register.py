import cv2
import os

name = input("Enter employee name: ")
path = f"dataset/{name}"
os.makedirs(path, exist_ok=True)

cam = cv2.VideoCapture(0)
detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

count = 0

print("Look at the camera... capturing clean face images")

while True:
    ret, frame = cam.read()
    if not ret:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Better detection settings (IMPORTANT)
    faces = detector.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=6,
        minSize=(100, 100)
    )

    for (x, y, w, h) in faces:
        # EXTRA CLEAN CROP (focus only on face)
        face = gray[y:y+h, x:x+w]

        # Resize to uniform size (VERY IMPORTANT for training)
        face = cv2.resize(face, (200, 200))

        count += 1

        cv2.imwrite(f"{path}/{count}.jpg", face)

        # draw rectangle for preview only
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.imshow("Register Face (Clean Capture)", frame)

    if cv2.waitKey(1) == 10 or count >= 10:
        break

cam.release()
cv2.destroyAllWindows()

print("Face dataset created successfully!")