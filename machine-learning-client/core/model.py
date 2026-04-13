"""
Head pose estimation model using MediaPipe FaceMesh and OpenCV.
"""

import math
import cv2
import numpy as np
import mediapipe as mp

# pylint: disable=no-member

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True)

LANDMARKS = [1, 33, 263, 61, 291, 199]
MODEL_POINTS = np.array([
    (0.0, 0.0, 0.0),
    (-30.0, -30.0, -30.0),
    (30.0, -30.0, -30.0),
    (-25.0, 30.0, -30.0),
    (25.0, 30.0, -30.0),
    (0.0, 60.0, -30.0)
], dtype=np.float64)

def predict_focus(img):
    """
    This function uses MediaPipe FaceMesh to detect facial landmarks
    and OpenCV's solvePnP method to estimate the 3D head pose, including
    pitch, yaw, and roll angles.

    Based on the estimated head orientation, it computes a focus score
    between 0 and 1. The more the face is oriented toward the camera,
    the higher the focus score; otherwise, the score decreases.

    Args:
        img (numpy.ndarray):
            Input image in OpenCV format (BGR color space).

    Returns:
        float:
            A focus score ranging from 0.0 to 1.0:
            - 1.0 indicates the face is directly facing the camera (high focus)
            - 0.0 indicates no face detected or extreme head deviation
    """
    h, w = img.shape[:2]
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    result = face_mesh.process(rgb)

    if not result.multi_face_landmarks:
        return 0.0

    face = result.multi_face_landmarks[0]

    image_points = np.array([
        (int(face.landmark[i].x * w), int(face.landmark[i].y * h))
        for i in LANDMARKS
    ], dtype=np.float64)

    camera_matrix = np.array([
        [w, 0, w / 2],
        [0, w, h / 2],
        [0, 0, 1]
    ], dtype=np.float64)

    success, rvec, _ = cv2.solvePnP(
        MODEL_POINTS,
        image_points,
        camera_matrix,
        np.zeros((4, 1))
    )

    if not success:
        return 0.0

    rmat, _ = cv2.Rodrigues(rvec)

    sy = math.sqrt(rmat[0, 0]**2 + rmat[1, 0]**2)

    if sy < 1e-6:
        pitch = math.atan2(-rmat[1, 2], rmat[1, 1])
        yaw = math.atan2(-rmat[2, 0], sy)
        roll = 0
    else:
        pitch = math.atan2(rmat[2, 1], rmat[2, 2])
        yaw = math.atan2(-rmat[2, 0], sy)
        roll = math.atan2(rmat[1, 0], rmat[0, 0])

    pitch, yaw, roll = [abs(a * 180 / np.pi) for a in (pitch, yaw, roll)]

    focus = 1.0 - min((pitch + yaw + roll) / 90.0, 1.0)

    return round(float(focus), 3)