import cv2
from models.predict import predict_anomaly

img = cv2.imread("test.jpg")  # put any photo in project folder

label, conf = predict_anomaly(img)

print("Prediction:", label)
print("Confidence:", conf)