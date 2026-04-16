"""Configuration values for machine learning core."""

import torch

BATCH_SIZE = 32
LR = 0.01
EPOCH = 10
NUM_WORKERS = 0
DATA_ROOT = "./data"
MODEL_PATH = "./data/processed/sign_language_model.pth"
MOMENTUM = 0.9

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

CLASSES = (
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "N/A",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "N/A",
)
