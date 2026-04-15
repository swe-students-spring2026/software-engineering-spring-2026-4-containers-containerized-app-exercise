"""Realtime camera capture for inference."""

import torch
import cv2
import numpy as np

from inference import load_model, predict
from preprocessing import preprocess_frame


def run(camera_index: int = 0, frame_step: int = 10, invert: bool = False):
    """Capture webcam frames, sample every 10 frame, and print predictions."""

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = load_model(device)

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera {camera_index}")

    print(f"Running on {device}. Press 'q' to quit.")

    frame_count = 0
    last_label = "-"
    last_conf = 0.0
    preview_28 = np.zeros((28, 28), dtype=np.uint8)

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame_count += 1

            if frame_count % frame_step == 0:
                _, gray_28, _ = preprocess_frame(frame, invert=invert)
                preview_28 = gray_28

                idx, label, conf = predict(model, gray_28, device)
                last_label, last_conf = label, conf

                print(
                    f"frame={frame_count} class={label} "
                    f"(index={idx}, confidence={conf:.2%})"
                )

            preview_frame = frame.copy()
            cv2.putText(
                preview_frame,
                f"class: {last_label} ({last_conf:.2%})",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

            cv2.imshow("Prediction", preview_frame)
            cv2.imshow(
                "28x28",
                cv2.resize(preview_28, (280, 280), interpolation=cv2.INTER_NEAREST),
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
