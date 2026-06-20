# Face Recognition Attendance

A lightweight Flask-based face recognition attendance system using OpenCV. It provides: web login (admin/employee), admin dashboard (train, start recognition, export, sign-up), and a simple CSV-backed attendance log.

**Quick Summary**
- Admin can train the model, start live recognition (camera window), sign up employees, and export attendance to Excel.
- Employees see a simplified dashboard with their attendance records.

**Prerequisites**
- Windows recommended (camera device tested on Windows)
- Python 3.10+ in a virtual environment
- Camera (internal or USB)

**Core dependencies**
- Flask
- pandas
- opencv-contrib-python (required for `cv2.face` LBPH recognizer)
- Optional: dlib / face-recognition for more robust detection

**Install (recommended)**
1. Create and activate a venv:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

2. Install packages:

```powershell
pip install --upgrade pip
pip install flask pandas opencv-contrib-python
# Optional, if you plan to use dlib/face-recognition
pip install dlib face-recognition
```

3. Run the app:

```powershell
cd Face_Recognition_Attendance
.\.venv\Scripts\python.exe app.py
```

Open http://127.0.0.1:5000 in your browser and log in with the default admin account (created in `users.csv`).

**Project layout (important files)**
- `app.py` — Flask app and routes
- `recognize.py` — Camera recognition loop (opens OpenCV window)
- `train.py` — Train LBPH model and write `trainer/trainer.yml`
- `register.py` — Camera capture for signing up new employees
- `users.csv`, `attendance.csv` — simple CSV storage for users and attendance
- `templates/` and `static/` — HTML/CSS UI
- `logs/` — training/recognition stdout logs (created at runtime)

**How recognition & attendance works**
- `recognize.py` runs a live OpenCV window and uses an LBPH recognizer to identify people.
- When a known person is seen, the script appends/updates a row in `attendance.csv` with `Time In` and later `Time Out` on the same day.
- The web dashboard reads logs and CSVs to display status and records.

**Troubleshooting**
- AttributeError: `cv2.face` missing — install `opencv-contrib-python` in the active venv.
- Camera not opening on Windows — try `cv2.VideoCapture(0, cv2.CAP_DSHOW)` in scripts.
- `trainer/trainer.yml` missing — run `Train Model` from admin dashboard or run `train.py` to generate the model.
- If recognition is slow or inaccurate, collect more labeled images per user (different angles/lighting) and retrain.

**Recommendations & Improvements**
- Replace CSVs with a proper database (SQLite/Postgres) for concurrency and reliability.
- Use secure password hashing (bcrypt) instead of plain CSV passwords.
- Replace LBPH with a modern face embedding model (FaceNet, ArcFace) and a classifier for better accuracy.
- Stream camera preview into the browser using a WebSocket or MJPEG endpoint for smoother demos.
- Add background workers (Celery/RQ) for training and long-running tasks instead of subprocesses.
- Add unit/integration tests and a `requirements.txt` or `pyproject.toml` for reproducible installs.
- Add a `Dockerfile` for containerized demos and consistent environments.

If you want, I can add a `requirements.txt`, create a `Dockerfile`, or add an example `README` section showing how to record a short demo video of the live recognition window.
