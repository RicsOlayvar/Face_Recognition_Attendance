import cv2
import os
import numpy as np

recognizer = cv2.face.LBPHFaceRecognizer_create()

faces = []
labels = []
label_map = {}

current_id = 0
dataset_path = "dataset"

print("Training started...")

for person_name in os.listdir(dataset_path):
    person_path = os.path.join(dataset_path, person_name)

    if not os.path.isdir(person_path):
        continue

    label_map[current_id] = person_name

    for image_name in os.listdir(person_path):
        img_path = os.path.join(person_path, image_name)

        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

        if img is None:
            continue

        # IMPORTANT: ensure correct format
        img = cv2.resize(img, (200, 200))
        img = np.array(img, dtype="uint8")

        faces.append(img)
        labels.append(current_id)

    current_id += 1

# Convert properly (NO object dtype)
faces = np.array(faces)
labels = np.array(labels)

recognizer.train(list(faces), labels)

os.makedirs("trainer", exist_ok=True)
recognizer.save("trainer/trainer.yml")

print("Training complete!")
print("People learned:", label_map)