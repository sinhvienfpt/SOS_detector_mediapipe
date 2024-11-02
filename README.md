## SOS Hand Gesture Detection System

This project implements a real-time hand gesture detection system that can recognize the SOS signal (distress signal) in a video stream. The system utilizes Mediapipe's hand tracking capabilities and leverages MQTT messaging and email notifications for alerting in case of emergency.

### Project Structure

The project consists of two Python files:

* **`sos_detector.py`**: This file contains the main logic for hand gesture detection. It utilizes Mediapipe's hand tracking to recognize the SOS signal sequence. 
* **`notifications.py`**: This file handles sending notifications to the user through both email and MQTT messaging.

### Dependencies

The required Python packages are listed in the `requirements.txt` file. To install them, run:

```bash
pip install -r requirements.txt
```

### Setup

1. **Configure Settings:**
   - Create a configuration file named **`config.py`**.
   - Fill in the required settings:
     * `EMAIL_API_KEY`: Your Brevo (formerly Sendinblue) API key.
     * `MQTT_BROKER`: The hostname or IP address of your MQTT broker.
     * `MQTT_PORT`: The port number of your MQTT broker.
     * `SENDER_EMAIL`: The email address you want to use for sending notifications.
     * `RECEIVER_EMAIL`: The email address you want to receive notifications on.
     * `RECEIVER_NAME`: The name of the recipient of the notifications.
2. **Run the Program:**
   ```bash
   python sos_detector.py
   ```

### Usage

1. **Run the script:** The program will open your default webcam.
2. **Perform the SOS gesture:** The system will detect the SOS hand gesture sequence, which involves:
    * All fingers open (stage 1)
    * Thumb folds, other fingers open (stage 2)
    * All fingers fold over the thumb (stage 3)
    * Thumb folds, other fingers open (stage 2)
3. **Notification:** Upon successful detection of the SOS gesture, the system will:
    * Capture a screenshot of the moment.
    * Send an email notification with the captured image to the specified recipient.
    * Publish a message to an MQTT topic, which can be used to trigger further actions, such as activating an alert system.

### Features

* **Real-time hand gesture detection:** Uses Mediapipe's hand tracking for accurate and efficient gesture recognition.
* **SOS signal recognition:** Specifically designed to detect the distress signal sequence.
* **Image capture:** Captures a screenshot of the moment the SOS signal is detected for evidence.
* **Multi-platform notification:** Supports sending notifications via both email and MQTT messaging.
* **Configuration flexibility:** Allows customization of email and MQTT settings.

### Future Improvements

* **Advanced hand tracking models:** Explore more advanced hand tracking models for improved accuracy and robustness.
* **Speech recognition:** Integrate speech recognition to allow users to verbally trigger alerts.
* **Location tracking:** Incorporate GPS location tracking to provide precise information about the user's location.
* **Integration with other devices:** Extend the system to interact with other devices, like a smartwatch or mobile phone.

### Disclaimer

This project is for demonstration purposes only and should not be used as a substitute for professional security or emergency services. Always contact emergency services directly in case of an actual emergency.
