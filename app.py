from flask import Flask, render_template, request, redirect, url_for
import subprocess

app = Flask(__name__)

# SIMPLE LOGIN (we can upgrade later)
users = {
    "admin": "admin123"
}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            return redirect(url_for("dashboard"))
        return "Invalid login"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/start-recognition")
def start_recognition():
    subprocess.run(["python", "recognize.py"])
    return redirect(url_for("dashboard"))


@app.route("/train")
def train():
    subprocess.run(["python", "train.py"])
    return redirect(url_for("dashboard"))


@app.route("/export")
def export():
    import pandas as pd
    df = pd.read_csv("attendance.csv")
    df.to_excel("attendance.xlsx", index=False)
    return "Exported Successfully"

if __name__ == "__main__":
    app.run(debug=True)