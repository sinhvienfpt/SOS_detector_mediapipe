import threading
import paho.mqtt.client as mqtt
import requests
from datetime import datetime
import base64
import json
import os
from config import (
    EMAIL_API_KEY, 
    MQTT_BROKER, 
    MQTT_PORT,
    SENDER_EMAIL,
    RECEIVER_EMAIL,
    RECEIVER_NAME
)
class NotificationManager:
    def __init__(self):
        # MQTT setup
        self.mqtt_broker = MQTT_BROKER
        self.mqtt_port = MQTT_PORT
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.connect(self.mqtt_broker, self.mqtt_port, 60)

        # Start MQTT loop in a separate thread
        threading.Thread(target=self.client.loop_forever, daemon=True).start()

    def _on_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT broker with result code: " + str(rc))

    def _on_message(self, client, userdata, message):
        print(f"Received message: {message.payload.decode()} on topic: {message.topic}")

    def _get_timestamp(self):
        """Get current timestamp in readable format"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _format_sos_info(self, message, image_path=None):
        """Format SOS information including timestamp and optional image"""
        sos_info = {
            "message": message,
            "timestamp": self._get_timestamp(),
            "location": "Camera 1",  # You can modify this based on your needs
        }
        
        # If image path is provided, encode the image
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode()
                sos_info["image"] = image_data
                sos_info["image_name"] = os.path.basename(image_path)

        return sos_info

    def send_mqtt_message(self, message, image_path=None):
        """Send message via MQTT with timestamp and image if available"""
        sos_info = self._format_sos_info(message, image_path)
        
        # Send basic info to a general topic
        self.client.publish("gesture/sos/status", json.dumps({
            "message": sos_info["message"],
            "timestamp": sos_info["timestamp"],
            "location": sos_info["location"]
        }))

        # If there's an image, send it to a separate topic to handle larger payloads
        if "image" in sos_info:
            self.client.publish("gesture/sos/image", json.dumps({
                "timestamp": sos_info["timestamp"],
                "image_name": sos_info["image_name"],
                "image_data": sos_info["image"]
            }))

    def send_email(self, message, image_path=None):
        """Send email notification with timestamp and image attachment"""
        timestamp = self._get_timestamp()
        
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": EMAIL_API_KEY,
            "content-type": "application/json"
        }

        # Create HTML content with timestamp
        html_content = f"""
        <html>
        <body>
            <h1>SOS DETECTION ALERT</h1>
            <p><strong>Message:</strong> {message}</p>
            <p><strong>Timestamp:</strong> {timestamp}</p>
            <p><strong>Location:</strong> Camera 1</p>
        </body>
        </html>
        """

        email_data = {
            "sender": {"name": "SOS DETECTION", "email": SENDER_EMAIL},
            "to": [{"email": RECEIVER_EMAIL, "name": "RECEIVER_NAME"}],
            "subject": f"SOS DETECTION - {timestamp}",
            "htmlContent": html_content
        }

        # Add image attachment if available
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode()
                email_data["attachment"] = [{
                    "content": image_data,
                    "name": os.path.basename(image_path)
                }]

        response = requests.post(url, json=email_data, headers=headers)

        if response.status_code == 201:
            print("Email sent successfully!")
        else:
            print(f"Email sending failed. Status code: {response.status_code}")
            print(response.json())

    def send_notifications(self, message, image_path=None):
        """Send all notifications with image if available"""
        self.send_mqtt_message(message, image_path)
        self.send_email(message, image_path)

    def cleanup(self):
        """Cleanup resources"""
        self.client.disconnect()