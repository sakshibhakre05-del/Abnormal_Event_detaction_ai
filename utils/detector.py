import cv2

def detect_persons_and_anomalies(frame, label):
    # Simple person detection (use YOLO or Haar cascades in production)
    # Draw bounding box if abnormal
    if label == 'ABNORMAL':
        cv2.rectangle(frame, (50, 50), (200, 200), (0, 0, 255), 2)  # Mock box
        cv2.putText(frame, label, (50, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    return frame