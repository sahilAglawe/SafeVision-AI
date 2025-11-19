from flask import Flask, render_template, Response, jsonify, request
import cv2
from ultralytics import YOLO
from db import init_db, get_session, Incident
from datetime import datetime
import threading
import time
import os
import base64
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

app = Flask(__name__)

# Global variables for detection state
detection_active = True
recording_active = True
current_threat_level = "LOW"
detection_stats = {
    'total_detections': 0,
    'threat_detections': 0,
    'last_detection_time': None,
    'detection_accuracy': 94.7
}

model = YOLO("women_safety_model.pt")

cap = None

def initialize_camera():
    global cap
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        # Try alternative camera index
        cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        # Try another alternative
        cap = cv2.VideoCapture(2)
    return cap.isOpened()

# Initialize database (will create tables if needed)
# Uses SQLAlchemy and is configurable via DATABASE_URL env var
init_db()

# Email configuration
EMAIL_SENDER = "shrikantambatkar8@gmail.com"
EMAIL_PASSWORD = "qchs fegx zrct hwdr"
  # You may need to use an App Password for Gmail
EMAIL_RECEIVER = "shrikantambatkar115@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email_alert(subject, message, image_path=None):
    """Send email alert with optional image attachment"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = subject

        # Add text body
        text_body = f"""
        SafeVisionAI Alert System
        
        {message}
        
        Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        Threat Level: {current_threat_level}
        
        This is an automated alert from SafeVisionAI Women Safety Surveillance System.
        Please take immediate action if required.
        """
        
        msg.attach(MIMEText(text_body, 'plain'))

        # Add image attachment if provided
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
                image = MIMEImage(img_data, name=os.path.basename(image_path))
                msg.attach(image)

        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        
        # Try to login - if it fails, provide helpful error message
        try:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        except smtplib.SMTPAuthenticationError:
            print("Gmail authentication failed. You may need to:")
            print("1. Enable 2-factor authentication on your Gmail account")
            print("2. Generate an App Password and use it instead of your regular password")
            print("3. Or use 'Less secure app access' (not recommended)")
            return False
        
        server.send_message(msg)
        server.quit()
        
        print(f"Email alert sent successfully: {subject}")
        return True
        
    except Exception as e:
        print(f"Failed to send email alert: {e}")
        return False

# Email configuration complete


def save_incident(label, confidence, severity="Medium", frame=None):
    # Use SQLAlchemy session to persist incident
    timestamp_dt = datetime.now()
    zone = "Zone 1"  # Default zone
    description = f"{label} detected with {confidence:.2f}% confidence"

    session = get_session()
    try:
        incident = Incident(timestamp=timestamp_dt, label=label, severity=severity, zone=zone, description=description, confidence=confidence)
        session.add(incident)
        session.commit()
        session.refresh(incident)
    except Exception as e:
        session.rollback()
        print(f"Failed to save incident to DB: {e}")
    finally:
        session.close()

    # Update detection stats
    timestamp = timestamp_dt.strftime("%Y-%m-%d %H:%M:%S")
    detection_stats['total_detections'] += 1
    detection_stats['last_detection_time'] = timestamp

    if severity == "High":
        detection_stats['threat_detections'] += 1

        # Save frame for email alert
        image_path = None
        if frame is not None:
            timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            image_path = f"static/snapshots/alert_{timestamp_str}.jpg"
            os.makedirs("static/snapshots", exist_ok=True)
            cv2.imwrite(image_path, frame)

        # Send email alert
        email_subject = f"SafeVisionAI - HIGH PRIORITY ALERT: {label} Detected"
        email_message = f"""
        CRITICAL ALERT - IMMEDIATE ATTENTION REQUIRED
        
        Detection Type: {label}
        Confidence: {confidence:.2f}%
        Timestamp: {timestamp}
        Zone: {zone}
        
        A high-priority threat has been detected by the SafeVisionAI surveillance system.
        Please review the attached image and take appropriate action immediately.
        """
        send_email_alert(email_subject, email_message, image_path)

def process_frame(frame):
    """Process frame with YOLO detection and return annotated frame"""
    if not detection_active:
        return frame
    
    try:
        results = model(frame, conf=0.5)  # Confidence threshold
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get box coordinates
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    # Get class and confidence
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    label = model.names[cls]
                    
                    # Determine severity based on class
                    severity = "High" if label in ["Men attacking woman", "Weapon"] else "Medium"
                    
                    # Draw bounding box
                    color = (0, 0, 255) if severity == "High" else (0, 255, 0)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    
                    # Add label
                    label_text = f"{label} {conf:.2f}"
                    cv2.putText(frame, label_text, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    
                    # Save incident to database with frame for high priority alerts
                    if severity == "High":
                        save_incident(label, conf * 100, severity, frame.copy())
                    else:
                        save_incident(label, conf * 100, severity)
                    
                    # Update threat level
                    global current_threat_level
                    if severity == "High":
                        current_threat_level = "HIGH"
                    elif current_threat_level == "LOW" and severity == "Medium":
                        current_threat_level = "MEDIUM"
    except Exception as e:
        print(f"Error in process_frame: {e}")
    
    return frame

def generate_frames():
    """Generate video frames with detection"""
    global recording_active, cap
    
    # Initialize camera if not already done
    if cap is None:
        if not initialize_camera():
            print("Failed to initialize camera")
            return
    
    print("Starting video feed generation...")
    
    while True:
        if not recording_active:
            time.sleep(0.1)
            continue
            
        try:
            if cap is None or not cap.isOpened():
                print("Camera not available, trying to reinitialize...")
                if not initialize_camera():
                    time.sleep(1)
                    continue
            
            success, frame = cap.read()
            if not success:
                print("Failed to read frame, trying to reinitialize camera...")
                if cap:
                    cap.release()
                if not initialize_camera():
                    time.sleep(1)
                    continue
                continue
            
            # Process frame with detection
            processed_frame = process_frame(frame)
            
            # Encode frame
            ret, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret:
                continue
                
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Error in generate_frames: {e}")
            time.sleep(0.1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stats')
def api_stats():
    """Get real-time statistics"""
    uptime_seconds = int(time.time() - app.start_time) if hasattr(app, 'start_time') else 0
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    camera_status = 1 if cap and cap.isOpened() else 0
    
    stats = {
        'total_alerts': detection_stats['total_detections'],
        'last_detection': detection_stats['last_detection_time'] or 'No detections yet',
        'uptime': uptime_str,
        'active_cameras': camera_status,
        'threat_level': current_threat_level,
        'detection_accuracy': detection_stats['detection_accuracy'],
        'threat_detections': detection_stats['threat_detections']
    }
    return jsonify(stats)

@app.route('/api/alerts')
def api_alerts():
    """Get alert history from database"""
    try:
        session = get_session()
        try:
            rows = session.query(Incident).order_by(Incident.timestamp.desc()).limit(50).all()
            alerts = []
            for row in rows:
                alerts.append({
                    'id': f'ALT-{row.id:03d}',
                    'timestamp': row.timestamp.strftime("%Y-%m-%d %H:%M:%S") if row.timestamp else None,
                    'detectedClass': row.label,
                    'severity': row.severity,
                    'zone': row.zone,
                    'description': row.description,
                    'confidence': f"{row.confidence:.1f}%" if row.confidence is not None else "N/A"
                })
            return jsonify(alerts)
        finally:
            session.close()
    except Exception as e:
        print(f"Error in api_alerts: {e}")
        return jsonify([])

@app.route('/api/control', methods=['POST'])
def control_detection():
    """Control detection and recording"""
    global detection_active, recording_active
    
    data = request.get_json()
    action = data.get('action')
    
    if action == 'toggle_detection':
        detection_active = not detection_active
        return jsonify({'detection_active': detection_active})
    elif action == 'toggle_recording':
        recording_active = not recording_active
        return jsonify({'recording_active': recording_active})
    elif action == 'get_status':
        return jsonify({
            'detection_active': detection_active,
            'recording_active': recording_active,
            'threat_level': current_threat_level
        })
    
    return jsonify({'error': 'Invalid action'})

@app.route('/api/snapshot')
def take_snapshot():
    """Take a snapshot of current frame"""
    global cap
    if cap and cap.isOpened():
        success, frame = cap.read()
        if success:
            # Save snapshot
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"static/snapshots/{timestamp}.jpg"
            os.makedirs("static/snapshots", exist_ok=True)
            cv2.imwrite(filename, frame)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'timestamp': timestamp
            })
    return jsonify({'success': False})

@app.route('/api/clear_alerts', methods=['POST'])
def clear_alerts():
    """Clear all alerts from database"""
    session = get_session()
    try:
        deleted = session.query(Incident).delete()
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Failed to clear alerts: {e}")
        deleted = 0
    finally:
        session.close()
    
    # Reset stats
    detection_stats['total_detections'] = 0
    detection_stats['threat_detections'] = 0
    detection_stats['last_detection_time'] = None
    
    return jsonify({'success': True, 'deleted': deleted})

@app.route('/api/camera_status')
def camera_status():
    """Check camera status"""
    global cap
    if cap and cap.isOpened():
        return jsonify({'status': 'connected', 'message': 'Camera is working'})
    else:
        return jsonify({'status': 'disconnected', 'message': 'Camera not available'})

@app.route('/api/test_camera')
def test_camera():
    """Test camera by capturing a single frame"""
    global cap
    try:
        if cap and cap.isOpened():
            success, frame = cap.read()
            if success:
                # Save test image
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"static/snapshots/test_{timestamp}.jpg"
                os.makedirs("static/snapshots", exist_ok=True)
                cv2.imwrite(filename, frame)
                
                return jsonify({
                    'success': True,
                    'message': 'Camera test successful',
                    'filename': filename,
                    'frame_shape': frame.shape
                })
            else:
                return jsonify({'success': False, 'message': 'Failed to read frame'})
        else:
            return jsonify({'success': False, 'message': 'Camera not initialized'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Camera test failed: {str(e)}'})

@app.route('/api/test_email')
def test_email():
    """Test email alert functionality"""
    try:
        # Capture current frame for test
        global cap
        image_path = None
        if cap and cap.isOpened():
            success, frame = cap.read()
            if success:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                image_path = f"static/snapshots/email_test_{timestamp}.jpg"
                os.makedirs("static/snapshots", exist_ok=True)
                cv2.imwrite(image_path, frame)
        
        # Send test email
        subject = "SafeVisionAI - Email Alert Test"
        message = """
        This is a test email from SafeVisionAI Women Safety Surveillance System.
        
        Email alert system is working correctly.
        Timestamp: {}
        
        If you receive this email, the alert system is properly configured.
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        success = send_email_alert(subject, message, image_path)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Test email sent successfully',
                'image_path': image_path
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send test email'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Email test failed: {str(e)}'
        })

@app.route('/api/trigger_alert', methods=['POST'])
def trigger_alert():
    """Manually trigger an alert for testing"""
    try:
        data = request.get_json()
        alert_type = data.get('type', 'Test Alert')
        severity = data.get('severity', 'High')
        
        # Capture current frame
        global cap
        image_path = None
        if cap and cap.isOpened():
            success, frame = cap.read()
            if success:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                image_path = f"static/snapshots/manual_alert_{timestamp}.jpg"
                os.makedirs("static/snapshots", exist_ok=True)
                cv2.imwrite(image_path, frame)
        
        # Send alert
        if severity == "High":
            email_subject = f"SafeVisionAI - MANUAL ALERT: {alert_type}"
            email_message = f"""
            MANUAL ALERT TRIGGERED - TESTING
            
            Alert Type: {alert_type}
            Severity: {severity}
            Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            
            This is a manually triggered test alert from SafeVisionAI.
            Please verify that the alert system is working correctly.
            """
            send_email_alert(email_subject, email_message, image_path)
        
        return jsonify({
            'success': True,
            'message': f'Manual alert triggered: {alert_type}',
            'severity': severity,
            'image_path': image_path
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to trigger alert: {str(e)}'
        })

if __name__ == '__main__':
    app.start_time = time.time()
    print("Starting SafeVisionAI Guardian...")
    
    # Initialize camera
    if initialize_camera():
        print("Camera initialized successfully")
    else:
        print("Warning: Could not initialize camera")
    
    print("Access the application at: http://localhost:5000")
    print("Video feed available at: http://localhost:5000/video_feed")
    app.run(debug=True, host='0.0.0.0', port=5000)