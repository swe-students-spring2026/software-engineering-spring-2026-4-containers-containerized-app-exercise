"""
Validation module for calculating model performance on the test set.
"""

import torch
from torch import nn

from data import get_test_loader
from model import Net
from src_config import DEVICE, MODEL_PATH, CLASSES


def evaluate():
    """
    Loads the trained model and calculates overall and per-class accuracy
    on the test dataset.
    """
    net = Net().to(DEVICE)
    net.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    net.eval()

    testloader = get_test_loader()
    criterion = nn.CrossEntropyLoss()

    test_loss = 0
    correct = 0
    total = 0
    correct_per_class = {c: 0 for c in CLASSES}
    total_per_class = {c: 0 for c in CLASSES}
    with torch.no_grad():
        for data, target in testloader:
            data, target = data.to(DEVICE), target.to(DEVICE)

            output = net(data)
            test_loss += criterion(output, target).item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += target.size(0)

            for t, p in zip(target.view(-1), pred.view(-1)):
                label = CLASSES[t.item()]
                if t == p:
                    correct_per_class[label] += 1
                total_per_class[label] += 1

    avg_loss = test_loss / len(testloader)
    overall_acc = 100.0 * correct / total

    print(
        f"\nTest Set: Average Loss: {avg_loss:.4f}, "
        f"Accuracy: {correct}/{total} ({overall_acc:.2f}%)\n"
    )

    print("Accuracy per class:")
    for label in CLASSES:
        if total_per_class[label] > 0:
            acc = 100.0 * correct_per_class[label] / total_per_class[label]
            print(f"- {label:10s}: {acc:.2f}%")
