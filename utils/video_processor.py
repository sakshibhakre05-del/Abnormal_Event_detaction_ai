import cv2

def extract_frames(video_path, seq_len=16):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while len(frames) < seq_len:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames