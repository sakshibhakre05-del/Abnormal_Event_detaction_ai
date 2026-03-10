import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from .model import AnomalyDetector
import numpy as np
import cv2
import os

# Mock Dataset (replace with actual UCF-Crime loading)
class VideoDataset(Dataset):
    def __init__(self, video_paths, labels, seq_len=16):
        self.video_paths = video_paths
        self.labels = labels
        self.seq_len = seq_len

    def __len__(self):
        return len(self.video_paths)

    def __getitem__(self, idx):
        # Extract frames (mock: random frames for demo)
        frames = []
        for _ in range(self.seq_len):
            frame = np.random.rand(224, 224, 3).astype(np.float32)
            frames.append(frame)
        frames = np.stack(frames)  # (seq_len, H, W, C)
        frames = torch.tensor(frames).permute(0, 3, 1, 2)  # (seq_len, C, H, W)
        label = torch.tensor(self.labels[idx], dtype=torch.long)
        return frames, label

# Training
def train_model():
    model = AnomalyDetector()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Mock data
    video_paths = ['path/to/video1.mp4', 'path/to/video2.mp4']  # Replace
    labels = [0, 1]  # 0: normal, 1: abnormal
    dataset = VideoDataset(video_paths, labels)
    dataloader = DataLoader(dataset, batch_size=2, shuffle=True)
    
    for epoch in range(10):
        for inputs, labels in dataloader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
        print(f'Epoch {epoch+1}, Loss: {loss.item()}')
    
    torch.save(model.state_dict(), 'models/weights/model_weights.pth')

if __name__ == '__main__':
    train_model()