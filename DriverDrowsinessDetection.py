import cv2
import mediapipe as mp
import math
import threading
import smtplib
import time
import webbrowser
from flask import Flask, request, jsonify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pygame

# ── EMAIL CONFIG ─────────────────────────────
SENDER_EMAIL    = "senderemailid@gmail.com"
SENDER_PASSWORD = "apppassword"
RECEIVER_EMAIL  = "receiveremailid@gmail.com"

EMAIL_COOLDOWN = 10   # seconds between emails
last_email_time = 0   # timestamp of last email sent

# ── GLOBAL LOCATION STORE ────────────────────
current_location = (0.0, 0.0)

# ── FLASK APP FOR BROWSER-GEO ───────────────
app = Flask(__name__)
HTML_PAGE = """
<!doctype html>
<html>
  <head><title>Share Location</title></head>
  <body>
    <h2>Please allow location access</h2>
    <script>
      navigator.geolocation.getCurrentPosition(function(pos) {
        fetch('/location', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({
            lat: pos.coords.latitude,
            lng: pos.coords.longitude
          })
        });
      });
    </script>
  </body>
</html>
"""
@app.route('/')
def index(): return HTML_PAGE
@app.route('/location', methods=['POST'])
def location():
    global current_location
    data = request.get_json()
    current_location = (data.get('lat',0.0), data.get('lng',0.0))
    return jsonify(success=True)

def run_flask():
    app.run(port=5000, debug=False)

# ── EMAIL + ALERT FUNCTIONS ─────────────────
def send_email_alert(snapshot_path):
    """Sends a simple text email with no cooldown logic here."""
    subject = "Drowsiness Alert!"
    lat, lng = current_location
    body = f"Driver is drowsy. Please check immediately.\nLocation: https://www.google.com/maps?q={lat},{lng}"
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECEIVER_EMAIL
    msg.attach(MIMEText(body, "plain"))

    with open(snapshot_path, "rb") as f:
        part = MIMEBase("application","octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition",f"attachment; filename={snapshot_path}")
        msg.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            print("[INFO] Email sent.")
    except Exception as e:
        print(f"[ERROR] Email not sent: {e}")

# ── ALARM SETUP ─────────────────────────────
pygame.mixer.init()
def sound_alarm():
    pygame.mixer.music.load("alarm.mp3")
    pygame.mixer.music.play()

# ── MEDIAPIPE SETUP ─────────────────────────
mp_face_mesh = mp.solutions.face_mesh
face_mesh    = mp_face_mesh.FaceMesh(static_image_mode=False,
                                     max_num_faces=1,
                                     min_detection_confidence=0.5)
LEFT_EYE  = [362,385,387,263,373,380]
RIGHT_EYE = [33,160,158,133,153,144]
def euclidean(p1,p2): return math.dist(p1,p2)
def eye_aspect_ratio(lm, idx, w,h):
    pts   = [lm[i] for i in idx]
    coords= [(int(p.x*w),int(p.y*h)) for p in pts]
    vert  = euclidean(coords[1],coords[5])+euclidean(coords[2],coords[4])
    horz  = euclidean(coords[0],coords[3])
    return vert/(2.0*horz)

# ── MAIN ────────────────────────────────────
if __name__=="__main__":
    # 1) Start location-permission server
    threading.Thread(target=run_flask, daemon=True).start()
    webbrowser.open("http://localhost:5000")  # ask user for precise location

    # 2) Begin video + detection
    cap = cv2.VideoCapture(0)
    EAR_THRESH, EAR_FRAMES = 0.25, 100
    counter, alarm_on = 0, False

    while True:
        ret, frame = cap.read()
        if not ret: break
        h,w=frame.shape[:2]
        rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        res=face_mesh.process(rgb)

        if res.multi_face_landmarks:
            for fm in res.multi_face_landmarks:
                ear=(eye_aspect_ratio(fm.landmark, LEFT_EYE, w,h)+
                     eye_aspect_ratio(fm.landmark, RIGHT_EYE,w,h))/2
                if ear<EAR_THRESH:
                    counter+=1
                    if counter>=EAR_FRAMES:
                        if not alarm_on: alarm_on=True
                        # **ONLY** if cooldown expired
                        now=time.time()
                        if now-last_email_time>=EMAIL_COOLDOWN:
                            snapshot="snapshot.jpg"
                            cv2.imwrite(snapshot,frame)
                            threading.Thread(target=sound_alarm).start()
                            threading.Thread(target=send_email_alert,
                                             args=(snapshot,)).start()
                            last_email_time=now
                        cv2.putText(frame,"DROWSINESS DETECTED!",
                                    (20,50),cv2.FONT_HERSHEY_SIMPLEX,
                                    1.0,(0,0,255),2)
                else:
                    counter,alarm_on=0,False

        cv2.imshow("Driver Drowsiness Detection",frame)
        if cv2.waitKey(1)&0xFF==ord("q"): break

    cap.release()
    cv2.destroyAllWindows()

driver_drowsiness_mediapipe.py
Displaying driver_drowsiness_mediapipe.py.
