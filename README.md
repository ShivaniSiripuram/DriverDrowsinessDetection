# 🚗 Driver Drowsiness Detection System

This Python-based application detects driver drowsiness in real-time using the webcam feed and Mediapipe's face mesh technology. When drowsiness is detected, it triggers an alarm sound and sends an email alert with the driver's live location and a snapshot.

---

## 🔍 Features

- Real-time drowsiness detection using Eye Aspect Ratio (EAR)
- Alarm sound alert using `pygame`
- Email alert with snapshot and location via Google Maps
- Location fetched from browser using Flask server
- Non-blocking multithreading for performance

---

## 📸 How It Works

- Uses MediaPipe FaceMesh to detect facial landmarks
- Calculates EAR (Eye Aspect Ratio) to detect eye closure
- If eyes remain closed beyond a threshold:
  - Plays an alarm sound
  - Captures a webcam snapshot
  - Sends an email with:
    - Timestamped photo
    - Location (Google Maps link)

---

## 🧰 Requirements

Install required Python packages:

```bash
pip install opencv-python mediapipe pygame flask
```

Also ensure:
- You have an `alarm.mp3` file in the same directory
- Gmail settings allow "less secure apps" or you are using an App Password

---

## ✉️ Email Configuration

Edit the following lines in the script with your credentials:

```python
SENDER_EMAIL    = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"
RECEIVER_EMAIL  = "receiver_email@gmail.com"
```

Use an **App Password** if you have 2FA enabled on your Gmail account.

---

## 🗺️ Location Sharing

The script launches a local Flask server and opens a browser window requesting location access. This allows the script to:

- Receive user's latitude & longitude
- Generate a Google Maps link
- Include it in the alert email

---

## 🧪 How to Run

```bash
python driver_drowsiness_mediapipe.py
```

> Press `q` to exit the webcam window.

---

## 🛡️ Disclaimer

This tool is for demonstration and educational purposes only. It should **not** be used as a substitute for professional driver monitoring systems in real vehicles.
