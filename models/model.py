import torch
import torch.nn as nn
from torchvision import models
import torchvision.transforms as T
from collections import deque
import collections
import cv2

# ---------------- Anomaly Detector ----------------
class AnomalyDetector(nn.Module):
    def __init__(self, num_classes=2, hidden_size=512, num_layers=2):
        super(AnomalyDetector, self).__init__()
        # CNN Feature Extractor (pretrained ResNet-50)
        self.cnn = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        self.cnn.fc = nn.Identity()  # Remove final layer
        # LSTM for temporal modeling
        self.lstm = nn.LSTM(input_size=2048, hidden_size=hidden_size,
                            num_layers=num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_classes)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        batch_size, seq_len, C, H, W = x.size()
        x = x.view(batch_size * seq_len, C, H, W)
        features = self.cnn(x)
        features = features.view(batch_size, seq_len, -1)
        lstm_out, _ = self.lstm(features)
        out = self.fc(lstm_out[:, -1, :])
        return self.softmax(out)

# ---------------- Prediction Function ----------------
# store last 16 frames globally
frame_buffer = collections.deque(maxlen=16)

transform = T.Compose([
    T.ToPILImage(),
    T.Resize((224, 224)),
    T.ToTensor()
])

def predict_frame(frame, model=None):

    # DEMO fallback
    if model is None:
        return "normal"

    # preprocess frame
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = transform(frame)

    frame_buffer.append(frame)

    # wait until buffer fills
    if len(frame_buffer) < 16:
        return "loading"

    # make sequence tensor
    sequence = torch.stack(list(frame_buffer))  # (16, 3, 224, 224)
    sequence = sequence.unsqueeze(0)  # (1, 16, 3, 224, 224)

    with torch.no_grad():
        output = model(sequence)
        label_index = torch.argmax(output, dim=1).item()

    return "abnormal" if label_index == 1 else "normal"


# ---------------- Load Model Function ----------------
def load_model(weights_path="models/weights.pth"):
    model = AnomalyDetector()
    try:
        model.load_state_dict(torch.load(weights_path, map_location=torch.device('cpu')))
        print("✅ Trained weights loaded")
    except FileNotFoundError:
        print(f"⚠ WARNING: {weights_path} not found. Running in DEMO mode.")
    except RuntimeError as e:
        print(f"⚠ WARNING: Failed to load weights: {e}. Running in DEMO mode.")
    model.eval()
    return model
