import torch
import numpy as np
from .model import load_model  # Fixed relative import
from torchvision import transforms

def preprocess_frames(frames):
    # frames: list of np arrays (H, W, C)
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    processed = [transform(frame) for frame in frames]
    return torch.stack(processed).unsqueeze(0)  # (1, seq_len, C, H, W)

def predict_anomaly(model, frames):
    inputs = preprocess_frames(frames)
    with torch.no_grad():
        outputs = model(inputs)
        probs = outputs[0]  # [prob_normal, prob_abnormal]
        confidence = probs[1].item()  # Abnormal confidence
        label = 'ABNORMAL' if confidence > 0.5 else 'NORMAL'
    return label, confidence