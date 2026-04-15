"""
Module for loading and preprocessing the Sign Language MNIST dataset.
"""

import torch
import pandas as pd
import numpy as np
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from src_config import BATCH_SIZE, DATA_ROOT, NUM_WORKERS

transform = transforms.Compose(
    [transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))]
)


class SignLanguageDataset(Dataset):
    """Custom Dataset for loading sign language images and labels from CSV."""

    def __init__(self, csv_file, img_transform=None):
        data = pd.read_csv(csv_file)
        self.labels = torch.tensor(data.iloc[:, 0].values, dtype=torch.long)
        self.images = data.iloc[:, 1:].values.astype(np.uint8).reshape(-1, 28, 28)
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
    trainset = SignLanguageDataset(
        f"{DATA_ROOT}/raw/sign_mnist_train.csv", img_transform=transform
    )
    return DataLoader(
        trainset, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS
    )


def get_test_loader():
    """Returns a DataLoader for the test dataset."""
    testset = SignLanguageDataset(
        f"{DATA_ROOT}/raw/sign_mnist_test.csv", img_transform=transform
    )
    return DataLoader(
        testset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS
    )
