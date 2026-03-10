# import eventlet
# eventlet.monkey_patch()

import os
import re
import sqlite3
import time
import base64
import cv2
from datetime import datetime
from flask import Flask, render_template, request, redirect, session, jsonify, send_from_directory, flash
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from detection import detect_abnormal, reset_state
import threading

camera_running = False
camera_thread = None
cap = None

# -------------------- APP --------------------
app = Flask(__name__)
app.secret_key = "secret123"
app.config["TEMPLATES_AUTO_RELOAD"] = True
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# -------------------- PATHS --------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Use a persistent storage path if deployed, otherwise fallback to local BASE_DIR
STORAGE_BASE = os.environ.get('STORAGE_PATH', BASE_DIR)

UPLOAD_FOLDER = os.path.join(STORAGE_BASE, "static/uploads")
FRAME_FOLDER = os.path.join(STORAGE_BASE, "static/frames")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(FRAME_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["FRAME_FOLDER"] = FRAME_FOLDER

def get_user_folders(username):
    user_frame_folder = os.path.join(FRAME_FOLDER, username)
    user_upload_folder = os.path.join(UPLOAD_FOLDER, username)
    os.makedirs(user_frame_folder, exist_ok=True)
    os.makedirs(user_upload_folder, exist_ok=True)
    return user_frame_folder, user_upload_folder

# -------------------- DATABASE --------------------
DB = os.path.join(STORAGE_BASE, "users.db")

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -------------------- AUTH --------------------
def valid_username(name):
    # Allow uppercase, lowercase, and spaces
    return re.fullmatch(r"[A-Za-z ]+", name)

@app.route('/')
def home():
    if 'user' in session:
        return redirect('/dashboard')
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if not valid_username(username):
            flash("Name must contain only alphabets and spaces.", "error")
            return redirect('/register')

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        if cur.fetchone():
            conn.close()
            flash("This email is already registered! Please log in.", "error")
            return redirect('/register')

        cur.execute("INSERT INTO users(username,email,password) VALUES(?,?,?)",
                    (username,email,password))
        conn.commit()
        conn.close()

        session['user'] = username
        return redirect('/dashboard')

    return render_template("register.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT username FROM users WHERE email=? AND password=?",(email,password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['user'] = user[0]
            return redirect('/dashboard')

        return "Invalid Login"

    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template("dashboard.html", username=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- CAMERA ENGINE ----------------

def camera_loop(username):
    global camera_running, cap

    user_frame_folder, _ = get_user_folders(username)

    print(f"Opening camera for {username}...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print(f"Camera not detected for {username}!")
        return

    print(f"Camera connected for {username}.")

    while camera_running:

        ret, frame = cap.read()
        if not ret:
            print("Frame read failed")
            break

        # ---------- DETECTION ----------
        abnormal = detect_abnormal(frame)

        state = "ABNORMAL" if abnormal else "NORMAL"
        socketio.emit("status", {"state": state})

        # ---------- SAVE FRAME ----------
        if abnormal:
            filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
            cv2.imwrite(os.path.join(user_frame_folder, filename), frame)
            socketio.emit("alarm")

        # ---------- SEND FRAME ----------
        _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
        frame_base64 = base64.b64encode(buffer).decode('utf-8')

        socketio.emit("frame", frame_base64)

        time.sleep(0.05)

    cap.release()
    print("Camera released")
# ---------------- SOCKET CONTROLS ----------------

@socketio.on("start_camera")
def start_camera():
    global camera_running, camera_thread

    username = session.get('user')
    if not username:
        return

    if not camera_running:
        reset_state()
        camera_running = True
        camera_thread = socketio.start_background_task(camera_loop, username)
        print(f"Camera started for {username}")

@socketio.on("stop_camera")
def stop_camera():
    global camera_running
    camera_running = False
    print("Camera stopped")

# -------------------- UPLOAD VIDEO --------------------
@app.route("/upload", methods=["POST"])
def upload_video():
    if 'user' not in session:
        return jsonify({"msg":"Unauthorized"}), 401

    if "file" not in request.files:
        return jsonify({"msg":"No file"})

    username = session['user']
    user_frame_folder, user_upload_folder = get_user_folders(username)

    file = request.files["file"]
    filename = secure_filename(file.filename)
    path = os.path.join(user_upload_folder, filename)
    file.save(path)

    socketio.emit("upload_status","Processing...")

    abnormal, frame = detect_abnormal(path, video=True)

    if abnormal:
        name = "upload_"+datetime.now().strftime("%H%M%S")+".jpg"
        cv2.imwrite(os.path.join(user_frame_folder, name), frame)
        socketio.emit("play_alarm")
        return jsonify({"msg":"Abnormal detected"})

    return jsonify({"msg":"Video Normal"})

# -------------------- ALERT IMAGES --------------------
@app.route("/alerts")
def alerts():
    if 'user' not in session:
        return redirect('/login')

    username = session['user']
    user_frame_folder, _ = get_user_folders(username)
    
    images = sorted(os.listdir(user_frame_folder), reverse=True)
    return render_template("alerts.html", images=images)

@app.route("/frame/<filename>")
def frame_image(filename):
    if 'user' not in session:
        return "Unauthorized", 401
    
    username = session['user']
    user_frame_folder, _ = get_user_folders(username)
    return send_from_directory(user_frame_folder, filename)

@app.route("/alerts_list")
def alerts_list():
    if 'user' not in session:
        return jsonify([]), 401

    username = session['user']
    user_frame_folder, _ = get_user_folders(username)
    
    files = os.listdir(user_frame_folder)
    files.sort(reverse=True)
    return jsonify(files)
# -------------------- MAIN --------------------
if __name__ == "__main__":
    print("Server starting...")
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)