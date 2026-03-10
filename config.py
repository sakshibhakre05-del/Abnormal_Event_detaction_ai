import torch
# config.py

# Path to the trained model
MODEL_PATH = "models/anomaly_detector.pth"

# Database path
DATABASE_PATH = "database.db"

# Device configuration
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Hyperparameters
BATCH_SIZE = 32
LEARNING_RATE = 0.001
NUM_EPOCHS = 50
