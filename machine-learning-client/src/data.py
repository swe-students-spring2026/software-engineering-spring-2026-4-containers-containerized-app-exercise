"""
Module for loading and preprocessing the Sign Language MNIST dataset.
"""
import os
import torch
import pandas as pd
import numpy as np
from pymongo import MongoClient
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from dotenv import load_dotenv
from src_config import BATCH_SIZE, DATA_ROOT, NUM_WORKERS

load_dotenv()

transform = transforms.Compose(
    [transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))]
)

def get_db():
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB_NAME", "sign_language_db")]
    return db

class SignLanguageDataset(Dataset):
    """Custom Dataset for loading sign language images and labels from CSV."""

    def __init__(self, collection, img_transform=None):
        docs = list(collection.find({}, {"_id": 0}))
        data = pd.DataFrame(docs)

        self.labels = torch.tensor(data["label"].values, dtype=torch.long)
        pixel_columns = [f"pixel{i}" for i in range(1, 785)]
        self.images = data[pixel_columns].values.astype(np.uint8).reshape(-1, 28, 28)
        self.transform = img_transform

    def __len__(self):
        """Returns the total number of samples."""
        return len(self.labels)

    def __getitem__(self, idx):
        """Generates one sample of data."""
        image = self.images[idx]
        label = self.labels[idx]
        if self.transform:
            image = self.transform(image)
        return image, label


def get_train_loader():
    """Returns a DataLoader for the training dataset."""
    db = get_db()
    trainset = SignLanguageDataset(
        db["sign_mnist_train"], img_transform=transform
    )
    return DataLoader(
        trainset, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS
    )


def get_test_loader():
    """Returns a DataLoader for the test dataset."""
    db = get_db()
    testset = SignLanguageDataset(
        db["sign_mnist_test"], img_transform=transform
    )
    return DataLoader(
        testset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS
    )
