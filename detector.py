import cv2
from ultralytics import YOLO
from datetime import datetime
import sqlite3
from twilio.rest import Client

# Load YOLOv8 model
model = YOLO("women_safety_model.pt")
cap = cv2.VideoCapture(0)

# Setup SQLite database
conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS incidents(time TEXT, label TEXT)''')
conn.commit()

# Twilio setup
account_sid = 'ACa674dc9cb23887179a62f66a4e63569e'
auth_token = '5b7d49a883979b1dfff2aa94413842bc'
twilio_whatsapp_number = 'whatsapp:+14155238886'
your_verified_number = 'whatsapp:+918668268460'
client = Client(account_sid, auth_token)

def send_alert(message):
    client.messages.create(
        from_=twilio_whatsapp_number,
        body=message,
        to=your_verified_number
    )

while True:
    success, frame = cap.read()
    if not success:
        break

    results = model(frame)

    for result in results:
        for box in result.boxes.data:
            cls = int(box[-1])
            label = model.names[cls]

            if label == 'Men attacking woman':
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO incidents VALUES (?, ?)", (timestamp, label))
                conn.commit()

                alert_msg = f"🚨 ALERT: {label} detected at {timestamp}."
                send_alert(alert_msg)

    cv2.imshow("YOLOv8 Detection Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()