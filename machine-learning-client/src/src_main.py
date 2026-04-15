"""
Execution entry point for training and evaluating the sign language model.
"""

from train import train
from val import evaluate


def main():
    """Run the full training and evaluation pipeline."""
    train()
    evaluate()


if __name__ == "__main__":
    main()
