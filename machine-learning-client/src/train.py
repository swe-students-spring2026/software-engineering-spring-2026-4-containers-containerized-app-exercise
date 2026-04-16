"""
Training logic for the sign language recognition model.
"""

import torch
from torch import nn
from torch import optim

from data import get_train_loader
from model import Net
from src_config import LR, EPOCH, MODEL_PATH, DEVICE, MOMENTUM


def train():
    """
    Initializes the model, defines the loss and optimizer,
    and runs the training loop over the specified number of epochs.
    """
    net = Net().to(DEVICE)
    trainloader = get_train_loader()

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(net.parameters(), lr=LR, momentum=MOMENTUM)

    print(f"Starting training on {DEVICE}...")
    for epoch in range(EPOCH):
        running_loss = 0.0
        for i, (inputs, labels) in enumerate(trainloader):
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)

            optimizer.zero_grad()

            outputs = net(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            if i % 100 == 99:
                print(f"[{epoch + 1}, {i + 1:5d}] loss: {running_loss / 100:.3f}")
                running_loss = 0.0

    print("Finished Training")
    torch.save(net.state_dict(), MODEL_PATH)


if __name__ == "__main__":
    train()
