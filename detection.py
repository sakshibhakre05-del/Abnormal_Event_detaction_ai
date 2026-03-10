import cv2
import numpy as np

# store previous frame globally
previous_frame = None

def reset_state():
    global previous_frame
    previous_frame = None

def detect_abnormal(frame, video=False):

    global previous_frame

    # ================= LIVE CAMERA =================
    if video == False:

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21,21), 0)

        if previous_frame is None:
            previous_frame = gray
            return False

        # frame difference
        diff = cv2.absdiff(previous_frame, gray)
        thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        motion_pixels = np.sum(thresh == 255)

        previous_frame = gray

        # 🔥 IMPORTANT: tune sensitivity here
        if motion_pixels > 15000:
            return True
        else:
            return False

    # ================= VIDEO FILE =================
    else:
        cap = cv2.VideoCapture(frame)
        prev = None

        while True:
            ret, img = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21,21),0)

            if prev is None:
                prev = gray
                continue

            diff = cv2.absdiff(prev, gray)
            thresh = cv2.threshold(diff, 25,255,cv2.THRESH_BINARY)[1]
            motion = np.sum(thresh==255)

            if motion > 20000:
                cap.release()
                return True, img

            prev = gray

        cap.release()
        return False, None