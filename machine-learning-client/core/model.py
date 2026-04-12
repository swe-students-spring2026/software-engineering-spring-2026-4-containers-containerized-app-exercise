import cv2
import numpy as np
import mediapipe as mp
import math

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True)

LANDMARKS = [1, 33, 263, 61, 291, 199]
MODEL_POINTS = np.array([
    (0.0, 0.0, 0.0),        # nose tip
    (-30.0, -30.0, -30.0),  # left eye
    (30.0, -30.0, -30.0),   # right eye
    (-25.0, 30.0, -30.0),   # left mouth
    (25.0, 30.0, -30.0),    # right mouth
    (0.0, 60.0, -30.0)      # chin
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

    image_points = []

    for idx in LANDMARKS:
        lm = face.landmark[idx]
        x, y = int(lm.x * w), int(lm.y * h)
        image_points.append((x, y))

    image_points = np.array(image_points, dtype=np.float64)

    focal_length = w
    center = (w / 2, h / 2)
    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype=np.float64)

    dist_coeffs = np.zeros((4, 1))

    success, rvec, tvec = cv2.solvePnP(
        MODEL_POINTS,
        image_points,
        camera_matrix,
        dist_coeffs
    )

    if not success:
        return 0.0

    rmat, _ = cv2.Rodrigues(rvec)

    sy = math.sqrt(rmat[0,0]**2 + rmat[1,0]**2)

    singular = sy < 1e-6

    if not singular:
        x = math.atan2(rmat[2,1], rmat[2,2])
        y = math.atan2(-rmat[2,0], sy)
        z = math.atan2(rmat[1,0], rmat[0,0])
    else:
        x = math.atan2(-rmat[1,2], rmat[1,1])
        y = math.atan2(-rmat[2,0], sy)
        z = 0

    pitch = abs(x * 180 / np.pi)
    yaw = abs(y * 180 / np.pi)
    roll = abs(z * 180 / np.pi)

    penalty = yaw + pitch + roll
    focus = 1.0 - min(penalty / 90.0, 1.0)

    return round(float(focus), 3)