# pylint: disable=no-member
"""Preprocessing helpers to convert camera frames to sign_mnist-like input."""

from typing import Dict, Tuple

import cv2
import numpy as np


def _center_crop(frame: np.ndarray, crop_ratio: float = 0.65) -> np.ndarray:
    """Crop the center square region of the frame."""
    height, width = frame.shape[:2]
    side = min(height, width)
    crop_side = max(1, int(side * crop_ratio))

    center_y = height // 2
    center_x = width // 2

    top = max(center_y - crop_side // 2, 0)
    left = max(center_x - crop_side // 2, 0)
    bottom = min(top + crop_side, height)
    right = min(left + crop_side, width)

    return frame[top:bottom, left:right]


def preprocess_frame(
    frame: np.ndarray, invert: bool = False
) -> Tuple[np.ndarray, np.ndarray, Dict[str, int]]:
    """Convert a raw camera frame into a grayscale 28x28 image and pixel mapping."""
    crop = _center_crop(frame, crop_ratio=0.65)

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    gray_28 = cv2.resize(gray, (28, 28), interpolation=cv2.INTER_AREA)

    if invert:
        gray_28 = cv2.bitwise_not(gray_28)

    pixels = gray_28.flatten().astype(np.uint8)
    pixel_dict = {f"pixel{i + 1}": int(value) for i, value in enumerate(pixels)}

    return crop, gray_28, pixel_dict
