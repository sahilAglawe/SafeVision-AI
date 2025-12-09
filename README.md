# SafeVisionAI Guardian - Women Safety Surveillance System

A real-time AI-powered surveillance system designed for women's safety using computer vision and machine learning.

---

## 🚀 Features

- **Real-time Camera Detection**: Live video feed with AI-powered object detection  
- **Threat Detection**: Automatic detection of suspicious activities and threats  
- **Alert System**: Real-time alerts with database storage and optional SMS notifications  
- **Dashboard**: Comprehensive monitoring interface with live statistics  
- **Alert History**: Complete log of all detections with search and filtering  
- **Camera Controls**: Start/stop recording, pause/resume detection, take snapshots  
- **Responsive UI**: Modern, mobile-friendly interface  

---

## 📌 Prerequisites

- Python 3.8 or higher  
- Webcam or camera device  
- Internet connection (for optional SMS alerts)  

---

## 📥 Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
Ensure you have the trained model:

women_safety_model.pt must be in the project root

This is a YOLOv8 model trained for women safety detection



## ⚙️ Configuration
### 🔹 Camera Setup
By default, the app uses the primary camera (index `0`):
```python
cap = cv2.VideoCapture(0)
If multiple cameras exist, change index to 1, 2, etc.

🔹 SMS Alerts (Optional)
To enable WhatsApp/SMS alerts via Twilio:

Create a Twilio account

Update your Twilio credentials in app.py:

python
Copy code
account_sid = 'YOUR_ACCOUNT_SID'
auth_token = 'YOUR_AUTH_TOKEN'
your_verified_number = 'whatsapp:+YOUR_PHONE_NUMBER'
▶️ Usage
Start the Application
bash
Copy code
python app.py
Open browser and visit:

arduino
Copy code
http://localhost:5000
🖥️ Interface Overview
📊 Dashboard
Live camera feed

Total alerts

Last detection time

System uptime

Recent alerts

Threat notifications

🎥 Live Detection
Full-screen video with detection boxes

Controls: Start/Stop Recording, Pause/Resume Detection, Snapshot

Real-time detection stats

📚 Alert History
Full log of all detections

Search by keyword

Filter by severity

Clear all alerts

🧠 Detection Classes
High Priority
Man attacking woman

Weapons

Medium Priority
Suspicious activities

Unusual movements

Low Priority
General monitoring events

🔗 API Endpoints
Method	Endpoint	Description
GET	/api/stats	Get system statistics
GET	/api/alerts	Retrieve alert history
POST	/api/control	Control detection/recording
GET	/api/snapshot	Take a snapshot
POST	/api/clear_alerts	Delete all alerts

🗄️ Database
Uses SQLite (incidents.db) to store:

Timestamp

Detection label

Severity level

Confidence score

Zone information

Database auto-creates if missing.

🛠️ Troubleshooting
Camera Issues
Close other camera apps

Change camera index

Check permissions

Model Issues
Ensure women_safety_model.pt exists

Check memory/disk space

Performance Issues
Reduce JPEG quality

Lower detection confidence

Close heavy apps

SMS Issues
Verify Twilio credentials

Use verified number

Check internet

🔐 Security Considerations
Runs on localhost

Add authentication for production

Protect Twilio credentials

Keep dependencies updated

🧩 Development
Folder Structure
csharp
Copy code
├── app.py                 # Main Flask application
├── detector.py            # Standalone detection script
├── requirements.txt       # Dependencies
├── women_safety_model.pt  # YOLOv8 model
├── static/
│   ├── css/
│   ├── js/
│   └── snapshots/
├── templates/
└── incidents.db
Customization Options
Modify detection classes

Adjust confidence thresholds

Customize alert messages

Add new API endpoints

📄 License
This project is intended for educational and safety purposes only. Follow local laws regarding surveillance and privacy.

🆘 Support
Check troubleshooting

Verify dependencies

Check camera functionality

View console logs

🤝 Contributing
Contributions are welcome!
Ensure:

Clean, maintainable code

Proper documentation

Security considerations

Testing before submission
