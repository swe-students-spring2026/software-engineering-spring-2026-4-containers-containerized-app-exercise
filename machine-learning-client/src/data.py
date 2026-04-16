"""Module for loading and preprocessing the Sign Language MNIST dataset."""

import os
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from dotenv import load_dotenv
from pymongo import MongoClient
from torch.utils.data import DataLoader, Dataset

from src_config import BATCH_SIZE, NUM_WORKERS

ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ROOT_ENV)


def transform_image(image: np.ndarray) -> torch.Tensor:
    """Convert a 28x28 uint8 image to a normalized tensor."""
    tensor = torch.from_numpy(image).float().unsqueeze(0) / 255.0
    tensor = (tensor - 0.5) / 0.5
    return tensor


def get_db():
    """Connect to MongoDB and return the database object."""
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB_NAME", "sign_language_db")]
    return db


class SignLanguageDataset(Dataset):
    """Custom dataset for loading sign language images and labels from MongoDB."""

    def __init__(self, collection):
        docs = list(collection.find({}, {"_id": 0}))
        data = pd.DataFrame(docs)

        self.labels = torch.tensor(data["label"].values, dtype=torch.long)
        pixel_columns = [f"pixel{i}" for i in range(1, 785)]
        self.images = data[pixel_columns].values.astype(np.uint8).reshape(-1, 28, 28)

    def __len__(self):
        """Return the total number of samples."""
        return len(self.labels)

    def __getitem__(self, idx):
        """Generate one sample of data."""
        image = self.images[idx]
        label = self.labels[idx]
        image = transform_image(image)
        return image, label


def get_train_loader():
    """Return a DataLoader for the training dataset."""
    db = get_db()
    trainset = SignLanguageDataset(db["sign_mnist_train"])
    return DataLoader(
        trainset, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS
    )


def get_test_loader():
    """Return a DataLoader for the test dataset."""
    db = get_db()
    testset = SignLanguageDataset(db["sign_mnist_test"])
    return DataLoader(
        testset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS
    )
