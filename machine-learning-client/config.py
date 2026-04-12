"""Configuration values for machine learning client."""

import os

VIDEO_PATH = os.getenv("VIDEO_PATH", "data/raw/sample.mp4")
MODEL_PATH = os.getenv("MODEL_PATH", "data/model/pose_landmarker_full.task")
