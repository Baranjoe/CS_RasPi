# Imports
import os
import socket
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import subprocess
import time
import logging
from datetime import timedelta
from threading import Timer

# Initialisierung der Flask App
app = Flask(__name__)
app.debug = True
app.secret_key = 'XXX'  # Aus Sicherheitsgründen entfernt
app.permanent_session_lifetime = timedelta(days=1)

# Einfaches Logging-Setup
logging.basicConfig(filename='flaskapp.log', level=logging.DEBUG)

# Globale Variablen zur Überwachung der Streaming-Prozesse
video_stream_process = None
audio_stream_process = None

# Funktion, um die interne IP-Adresse zu ermitteln (wurde implementiert
# um HASS_SERVER-Umgebungsvariable auch bei wechsel des Netzwerks dynamisch anzupassen)
def get_ip_address():
    try:
        # Versuchen, eine externe Adresse zu erreichen, um die interne IP zu bestimmen
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(("8.8.8.8", 80))  # DNS von Google
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except:
        return "127.0.0.1"  # Standardmässig localhost, wenn die Bestimmung nicht möglich ist

# Funktion zum Ausschalten des Systems
def shutdown():
    subprocess.run(["/home/baranjoe/power_off.sh"])

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Passwortprüfung
        if request.form['password'] == 'XXX': # Aus Sicherheitsgründen entfernt
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return 'Invalid password'
    return render_template('login.html')

# Startseite Route
@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        # Dynamisches Setzen der HASS_SERVER-Umgebungsvariable
        hass_ip = get_ip_address()
        os.environ['HASS_SERVER'] = f"http://{hass_ip}:8123"
        os.environ['HASS_TOKEN'] = "XXX" # Aus Sicherheitsgründen entfernt
    return render_template('index.html')

# Video-Streaming Route
@app.route('/video')
def video():
    global video_stream_process
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    # Starten des Video-Streams mit FFmpeg
    video_stream_process = subprocess.Popen([
        "ffmpeg",
        "-thread_queue_size", "2048",
        "-fflags", "nobuffer",
        "-f", "alsa", "-ar", "22050", "-i", "hw:1,0",
        "-acodec", "aac",
        "-f", "v4l2", "-i", "/dev/video0",
        "-vf",
        "drawtext=fontfile=/path/to/font.ttf: text='%{localtime}': x=10: y=10: fontcolor=white: fontsize=24: box=1: boxcolor=black@0.5: boxborderw=5",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "ultrafast",
        "-tune", "zerolatency",
        "-g", "15",
        "-b:v", "800k",
        "-b:a", "96k",
        "-f", "hls",
        "-hls_time", "1",
        "-hls_list_size", "3",
        "-hls_flags", "delete_segments",
        "/home/baranjoe/flask_server/static/live/video.m3u8"
    ])
    time.sleep(5)
    return render_template('video.html')

# Audio-Streaming Route
@app.route('/audio')
def audio():
    global audio_stream_process
    if not session.get('logged_in'):
        return redirect(url_for('home'))
    # Starten des Audio-Streams mit FFmpeg
    audio_stream_process = subprocess.Popen(["ffmpeg", "-thread_queue_size", "256", "-fflags", "nobuffer", "-f", "alsa", "-ar", "22050", "-i", "hw:1,0", "-acodec", "aac", "-b:a", "96k", "-f", "hls", "-hls_time", "3", "-hls_list_size", "3", "-hls_flags", "delete_segments", "/home/baranjoe/flask_server/static/audio/audio.m3u8"])  # Your FFmpeg command
    time.sleep(5)
    return render_template('audio.html')

# Route zum Ausschalten des Systems
@app.route('/power-off', methods=['POST'])
def power_off():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    # Zeitverzögerte Abschaltung
    t = Timer(5.0, shutdown)
    t.start()
    return render_template('powering_off.html')

# Hama WLAN-Steckdose: On
@app.route('/turn-on-light', methods=['POST'])
def turn_on_light():
    subprocess.run(["/home/baranjoe/.local/bin/hass-cli", "service", "call", "switch.turn_on", "--arguments", "entity_id=switch.baby_light_socket_1"])
    return jsonify({"status": "success", "action": "turned on"})

# Hama WLAN-Steckdose: Off
@app.route('/turn-off-light', methods=['POST'])
def turn_off_light():
    subprocess.run(["/home/baranjoe/.local/bin/hass-cli", "service", "call", "switch.turn_off", "--arguments", "entity_id=switch.baby_light_socket_1"])
    return jsonify({"status": "success", "action": "turned off"})

# Blink: Helles weisses Licht
@app.route('/turn-bright-blink', methods=['POST'])
def turn_bright_blink():
    subprocess.run(["/home/baranjoe/kill_blink.sh"])
    subprocess.run(["/home/baranjoe/bright_light.sh"], env={'PATH': '/usr/local/bin:/usr/bin:/bin'})
    return jsonify({"status": "success", "action": "turned bright"})

# Blink: Sleep Pattern 1
@app.route('/turn-pattern1-blink', methods=['POST'])
def turn_pattern1_blink():
    subprocess.run(["/home/baranjoe/kill_blink.sh"])
    subprocess.run(["/home/baranjoe/sleep_pattern.sh"])
    return jsonify({"status": "success", "action": "turned pattern1"})

# Blink: Sleep Pattern 2
@app.route('/turn-pattern2-blink', methods=['POST'])
def turn_pattern2_blink():
    subprocess.run(["/home/baranjoe/kill_blink.sh"])
    subprocess.run(["/home/baranjoe/sleep_pattern_1.sh"])
    return jsonify({"status": "success", "action": "turned pattern2"})

# Blink: Off
@app.route('/turn-off-blink', methods=['POST'])
def turn_off_blink():
    subprocess.run(["/home/baranjoe/kill_blink.sh"])
    subprocess.run(["/home/baranjoe/light_off.sh"])
    return jsonify({"status": "success", "action": "turned off"})

# Route um FFmpeg-Stream zu stoppen
@app.route('/stop-stream', methods=['POST'])
def stop_stream():
    subprocess.run(["/home/baranjoe/flask_server/assets/stop_ffmpeg.sh"])
    return redirect(url_for('home'))

# Starten der Flask-App
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
