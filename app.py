from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
import subprocess
import os
import sys

app = Flask(__name__)
app.secret_key = "replace-this-with-a-secret-key"

DEFAULT_ACTION_STATUS = {
    "recognition": "Idle",
    "train": "Idle",
    "export": "Idle",
    "register": "Idle"
}

USER_CSV = os.path.join(os.path.dirname(__file__), "users.csv")
ATTENDANCE_FILE = os.path.join(os.path.dirname(__file__), "attendance.csv")
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")

os.makedirs(LOG_DIR, exist_ok=True)


def load_users():
    if not os.path.exists(USER_CSV):
        with open(USER_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["username", "password", "role"])
            writer.writerow(["admin", "admin123", "admin"])

    loaded = {}
    with open(USER_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            loaded[row["username"]] = {
                "password": row["password"],
                "role": row.get("role", "employee")
            }
    return loaded


def save_user(username, password, role="employee"):
    username = username.strip()
    password = password.strip()
    if not username or not password:
        return False

    existing = load_users()
    if username in existing:
        return False

    with open(USER_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([username, password, role])
    return True


def load_attendance_for_user(username):
    if not os.path.exists(ATTENDANCE_FILE):
        return []

    rows = []
    with open(ATTENDANCE_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Name") == username:
                if "Time In" not in row and "Time" in row:
                    row["Time In"] = row.get("Time", "")
                if "Time Out" not in row:
                    row["Time Out"] = row.get("Time Out", "") or ""
                rows.append(row)
    return rows

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        loaded_users = load_users()

        user = loaded_users.get(username)
        if user and user["password"] == password:
            session["username"] = username
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "error")
        return render_template("login.html")

    return render_template("login.html")


def get_action_status():
    return session.get("action_status", DEFAULT_ACTION_STATUS.copy())


def update_action_status(action, message):
    status = get_action_status()
    status[action] = message
    session["action_status"] = status


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") == "employee":
        return redirect(url_for("employee_dashboard"))

    return render_template(
        "dashboard.html",
        username=session["username"],
        status=get_action_status(),
        last_action=session.get("last_action", "No actions yet."),
        train_log=load_last_log("train.py"),
        recognition_log=load_last_log("recognize.py"),
    )


@app.route("/employee-dashboard")
def employee_dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "employee":
        return redirect(url_for("dashboard"))

    records = load_attendance_for_user(session["username"])
    return render_template(
        "employee_dashboard.html",
        username=session["username"],
        records=records,
        last_action=session.get("last_action", "No actions yet."),
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


def get_log_path(script_name):
    script_base = os.path.splitext(script_name)[0]
    return os.path.join(LOG_DIR, f"{script_base}.log")


def load_last_log(script_name, max_lines=30):
    log_path = get_log_path(script_name)
    if not os.path.exists(log_path):
        return ""

    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()
    return "\n".join(lines[-max_lines:])


def run_script(script_name, args=None):
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    if os.path.exists(script_path):
        log_path = get_log_path(script_name)
        command = [sys.executable, script_path]
        if args:
            command.extend(args)
        with open(log_path, "w", encoding="utf-8", errors="ignore") as log_f:
            subprocess.Popen(
                command,
                cwd=os.path.dirname(__file__),
                stdout=log_f,
                stderr=subprocess.STDOUT,
            )


@app.route("/register", methods=["GET", "POST"])
def register():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        password = request.form.get("password", "").strip()

        if not name or not password:
            flash("Please enter both a name and a password.", "error")
            return render_template("register.html", username=session["username"])

        if not save_user(name, password):
            flash("That username already exists.", "error")
            return render_template("register.html", username=session["username"])

        run_script("register.py", [name])
        update_action_status("register", "Started")
        session["last_action"] = f"Sign-up started for {name}"
        flash("Sign-up started. Follow the camera window.", "info")
        return redirect(url_for("dashboard"))

    return render_template("register.html", username=session["username"])


@app.route("/start-recognition")
def start_recognition():
    run_script("recognize.py")
    update_action_status("recognition", "Started")
    session["last_action"] = "Face recognition started"
    flash("Face recognition started.", "info")
    return redirect(url_for("dashboard"))


@app.route("/train")
def train():
    run_script("train.py")
    update_action_status("train", "Started")
    session["last_action"] = "Model training started"
    flash("Training started.", "info")
    return redirect(url_for("dashboard"))


@app.route("/export")
def export():
    import pandas as pd
    df = pd.read_csv("attendance.csv")
    df.to_excel("attendance.xlsx", index=False)
    update_action_status("export", "Completed")
    session["last_action"] = "Attendance export completed"
    flash("Export completed.", "info")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
