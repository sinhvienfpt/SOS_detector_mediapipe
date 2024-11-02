import os
import cv2
import mediapipe as mp
from datetime import datetime
import time
from notifications import NotificationManager

class SOSdetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
        self.current_stage = 0
        self.start_time = time.time()
        self.end_time = time.time()
        self.notification_manager = NotificationManager()

    def _save_image(self, image):
            """ Save image to folder detected and return the file path """
            if not os.path.exists("./detected"):
                os.makedirs("./detected")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"./detected/screenshot_{timestamp}.png"
            cv2.imwrite(filename, image)
            print(f"Image saved as {filename}")
            return filename


    def _stage1(self, hand_landmarks):
        """Stage 1: All fingers (A to E) open""" 
        THUMB_TIP = hand_landmarks[4]
        THUMB_IP = hand_landmarks[3]
        THUMB_MCP = hand_landmarks[2]
        
        INDEX_FINGER_TIP = hand_landmarks[8]
        INDEX_FINGER_PIP = hand_landmarks[6]
        
        MIDDLE_FINGER_TIP = hand_landmarks[12]
        MIDDLE_FINGER_PIP = hand_landmarks[10]
        
        RING_FINGER_TIP = hand_landmarks[16]
        RING_FINGER_PIP = hand_landmarks[14]
        
        PINKY_TIP = hand_landmarks[20]
        PINKY_PIP = hand_landmarks[18]
            
        return (
            THUMB_TIP.y < THUMB_IP.y and THUMB_MCP.y and 
            INDEX_FINGER_TIP.y < INDEX_FINGER_PIP.y and
            MIDDLE_FINGER_TIP.y < MIDDLE_FINGER_PIP.y and
            RING_FINGER_TIP.y < RING_FINGER_PIP.y and
            PINKY_TIP.y < PINKY_PIP.y
        )

    def _stage2(self, hand_landmarks):
        """ Stage 2: Only finger A (thumb) folds and fingers (B to E) open"""
        THUMB_TIP = hand_landmarks[4]
        THUMB_IP = hand_landmarks[3]
        THUMB_MCP = hand_landmarks[2]
        
        INDEX_FINGER_TIP = hand_landmarks[8]
        INDEX_FINGER_PIP = hand_landmarks[6]
        
        MIDDLE_FINGER_TIP = hand_landmarks[12]
        MIDDLE_FINGER_PIP = hand_landmarks[10]
        
        RING_FINGER_TIP = hand_landmarks[16]
        RING_FINGER_PIP = hand_landmarks[14]
        
        PINKY_TIP = hand_landmarks[20]
        PINKY_PIP = hand_landmarks[18]
        return (
            THUMB_TIP.x > THUMB_IP.x and THUMB_IP.x > THUMB_MCP.x and 
            INDEX_FINGER_TIP.y < INDEX_FINGER_PIP.y and
            MIDDLE_FINGER_TIP.y < MIDDLE_FINGER_PIP.y and
            RING_FINGER_TIP.y < RING_FINGER_PIP.y and
            PINKY_TIP.y < PINKY_PIP.y
        )

    def _stage3(self, hand_landmarks):
        """Stage 3: All fingers (B to E) fold over finger A (thumb)"""        
        INDEX_FINGER_TIP = hand_landmarks[8]
        INDEX_FINGER_PIP = hand_landmarks[6]
        
        MIDDLE_FINGER_TIP = hand_landmarks[12]
        MIDDLE_FINGER_PIP = hand_landmarks[10]
        
        RING_FINGER_TIP = hand_landmarks[16]
        RING_FINGER_PIP = hand_landmarks[14]
        
        PINKY_TIP = hand_landmarks[20]
        PINKY_PIP = hand_landmarks[18]

        return (
            INDEX_FINGER_TIP.y > INDEX_FINGER_PIP.y and
            MIDDLE_FINGER_TIP.y > MIDDLE_FINGER_PIP.y and
            RING_FINGER_TIP.y > RING_FINGER_PIP.y and
            PINKY_TIP.y > PINKY_PIP.y
        )    

    def detect_hand_signal(self, hand_landmarks):
        """Detect SOS hand signal"""
        if self.current_stage == 0 and self._stage1(hand_landmarks):
            self.current_stage = 1
        
        if self.current_stage == 1 and self._stage2(hand_landmarks):
            self.current_stage = 2
            self.start_time = time.time()
        
        if self.current_stage == 2 and self._stage3(hand_landmarks):
            self.current_stage = 3
                
        if self.current_stage == 3 and self._stage2(hand_landmarks):
            self.current_stage = 4
            self.end_time = time.time()

        if self.current_stage == 4:
            if self.end_time - self.start_time < 3:
                return "SOS DETECTION"
            else:
                self.current_stage = 0

        if time.time() - self.start_time > 3:
            self.current_stage = 0
            
        return "No SOS"
    

    def run_detection(self):
        """Run hand gesture detection"""
        cap = cv2.VideoCapture(0)
        try:
            while cap.isOpened():
                success, image = cap.read()
                if not success:
                    break

                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                results = self.hands.process(image)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    self.mp_drawing.draw_landmarks(image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    signal = self.detect_hand_signal(hand_landmarks.landmark)
                    cv2.putText(image, signal, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

                    if signal == "SOS DETECTION":
                        image_path = self._save_image(image)
                        self.notification_manager.send_notifications("SOS Alert detected!", image_path)
                        self.current_stage = 0  # Reset stages after capture

                cv2.imshow('Hand Signal Detection', image)

                if cv2.waitKey(5) & 0xFF == 27:  # Press Esc to stop
                    break
        finally:
            cap.release()
            self.notification_manager.cleanup()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = SOSdetector()
    detector.run_detection()