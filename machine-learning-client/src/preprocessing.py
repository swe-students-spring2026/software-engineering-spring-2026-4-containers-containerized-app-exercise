"""Preprocessing helpers to convert camera frames to sign_mnist format."""

from typing import Dict, Tuple

import cv2
import numpy as np


def preprocess_frame(
    frame: np.ndarray, invert: bool = False
) -> Tuple[np.ndarray, np.ndarray, Dict[str, int]]:
    """Convert a raw camera frame into cropped 28x28 grayscale pixels and mapping."""
    height, width = frame.shape[:2]
    side = min(height, width)

    top = (height - side) // 2
    left = (width - side) // 2

    crop = frame[top : top + side, left : left + side]

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray_28 = cv2.resize(gray, (28, 28), interpolation=cv2.INTER_AREA)

    if invert:
        gray_28 = cv2.bitwise_not(gray_28)

    pixels = gray_28.flatten().astype(np.uint8)
    pixel_dict = {f"pixel{i + 1}": int(v) for i, v in enumerate(pixels)}

    return crop, gray_28, pixel_dict
