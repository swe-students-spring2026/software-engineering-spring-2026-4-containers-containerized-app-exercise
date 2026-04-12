"""Video preprocessing pipeline: MediaPipe Pose landmarks to CSV."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import VIDEO_PATH
from config import MODEL_PATH


def resolve_path(path_str: str) -> Path:
    """Resolve a path against cwd first, then this file's directory."""
    raw_path = Path(path_str)
    if raw_path.is_absolute():
        return raw_path

    cwd_candidate = Path.cwd() / raw_path
    if cwd_candidate.exists():
        return cwd_candidate

    project_root_candidate = Path(__file__).resolve().parent.parent / raw_path
    return project_root_candidate


def build_default_output_path(video_path: Path) -> Path:
    """Return default output CSV path under data/processed."""
    base_dir = Path(__file__).resolve().parent.parent
    processed_dir = base_dir / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    return processed_dir / f"{video_path.stem}_pose_landmarks.csv"


def extract_pose_landmarks_to_csv(video_path: Path, output_csv_path: Path, model_path: Path) -> tuple[int, int]:
    """
    Run MediaPipe Pose Landmarker on a video and save joint coordinates to CSV.

    Each CSV row represents one landmark for one frame.
    Returns: (frames_processed, rows_written).
    We still need to figure out how to match the skeleton to the output csv later
    """
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise FileNotFoundError(f"Unable to open video file: {video_path}")

    fps = capture.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0  
    try:
        landmark_names = [landmark.name for landmark in mp.solutions.pose.PoseLandmark]
    except AttributeError:
        landmark_names = [f"LANDMARK_{i}" for i in range(33)]

    output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    frames_processed = 0
    rows_written = 0
    fieldnames = [
        "frame_idx",
        "timestamp_sec",
        "landmark_index",
        "landmark_name",
        "x",
        "y",
        "z",
        "visibility",
        "presence",
    ]

    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(model_path)),
        running_mode=VisionRunningMode.VIDEO,
        min_pose_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    with open(output_csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        with PoseLandmarker.create_from_options(options) as landmarker:
            while True:
                success, frame_bgr = capture.read()
                if not success:
                    break

                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
                
                frame_timestamp_ms = int((frames_processed * 1000) / fps)
                
                results = landmarker.detect_for_video(mp_image, frame_timestamp_ms)

                # note here we use the long format, can change it to wide to fit the skeleton
                if results.pose_landmarks:
                    timestamp_sec = frames_processed / fps
                    for index, landmark in enumerate(results.pose_landmarks[0]):
                        writer.writerow(
                            {
                                "frame_idx": frames_processed,
                                "timestamp_sec": timestamp_sec,
                                "landmark_index": index,
                                "landmark_name": landmark_names[index] if index < len(landmark_names) else f"LANDMARK_{index}",
                                "x": landmark.x,
                                "y": landmark.y,
                                "z": landmark.z,
                                "visibility": landmark.visibility,
                                "presence": landmark.presence,
                            }
                        )
                        rows_written += 1

                frames_processed += 1

    capture.release()
    return frames_processed, rows_written


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Extract MediaPipe Pose landmarks from a video into CSV."
    )
    parser.add_argument(
        "--video-path",
        default=VIDEO_PATH,
        help="Path to input video. Defaults to VIDEO_PATH from config.py.",
    )
    parser.add_argument(
        "--output-csv",
        default="",
        help="Path to output CSV. Defaults to data/processed/<video_name>_pose_landmarks.csv.",
    )
    parser.add_argument(
        "--model-path",
        default=MODEL_PATH,
        help="Path to the MediaPipe Pose landmarker model (.task file).",
    )
    args = parser.parse_args()

    resolved_video_path = resolve_path(args.video_path)
    resolved_model_path = resolve_path(args.model_path)

    output_csv_path = (
        resolve_path(args.output_csv)
        if args.output_csv
        else build_default_output_path(resolved_video_path)
    )

    frames_processed, rows_written = extract_pose_landmarks_to_csv(
        resolved_video_path, output_csv_path, resolved_model_path
    )
    print(f"Video: {resolved_video_path}")
    print(f"Model: {resolved_model_path}")
    print(f"Output CSV: {output_csv_path}")
    print(f"Frames processed: {frames_processed}")
    print(f"Rows written: {rows_written}")


if __name__ == "__main__":
    main()
