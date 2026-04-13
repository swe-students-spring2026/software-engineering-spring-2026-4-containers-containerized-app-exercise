# ML Module — Food Detection with Grounding DINO

## Overview

This module uses [Grounding DINO](https://github.com/IDEA-Research/GroundingDINO), an open-vocabulary object detection model, to identify food items in images. Unlike traditional detectors limited to fixed categories, it accepts **free-text class descriptions**, so you can detect any food type without retraining.

## Setup

### 1. Environment

```bash
# Python 3.9+ recommended
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Model Weights

Weights download **automatically** on first run (~700MB). No manual setup needed.

## Usage

### Basic

```bash
# Run on a folder of images
python food_detection.py --input ./images --output ./results
```

### Custom Classes

```bash
# Detect only specific foods (dot-separated)
python food_detection.py -i ./images -o ./results \
    --classes "sushi. ramen. burger. salad. coffee"
```

### Adjust Sensitivity

```bash
# Lower threshold = more detections (may include false positives)
python food_detection.py -i ./images -o ./results --box-thresh 0.2 --text-thresh 0.2

# Higher threshold = fewer but more confident detections
python food_detection.py -i ./images -o ./results --box-thresh 0.5 --text-thresh 0.4
```

### Save Cropped Detections

```bash
python food_detection.py -i ./images -o ./results --save-crop
```

## Output Structure

```
results/
├── annotated/                  # Images with bounding boxes drawn
│   ├── photo1.jpg
│   └── photo2.jpg
├── crops/                      # (optional, with --save-crop)
│   └── photo1/
│       ├── sushi_0_0.85.jpg
│       └── rice_1_0.72.jpg
├── detection_results.json      # Structured results for backend
└── detection_report.txt        # Human-readable summary
```

## JSON Output Format

The `detection_results.json` file is the primary output for backend integration:

```json
{
  "timestamp": "2026-04-13T15:30:00",
  "total_images": 10,
  "total_detections": 25,
  "results": [
    {
      "filename": "photo1.jpg",
      "num_detections": 3,
      "detections": [
        {
          "class_name": "sushi",
          "confidence": 0.8523,
          "bbox_xyxy": [120.5, 80.3, 340.1, 260.7]
        }
      ]
    }
  ]
}
```

Each detection includes:
- `class_name` — detected food label
- `confidence` — model confidence score (0–1)
- `bbox_xyxy` — bounding box coordinates `[x1, y1, x2, y2]` in pixels

## Integration Notes

- **Frontend**: Use `annotated/` images for display. Parse `detection_results.json` for overlay data.
- **Backend**: Read `detection_results.json` directly — it contains all detection metadata needed for database storage.
- **Adding new food classes**: Just modify the `--classes` argument. No retraining required.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `CUDA out of memory` | Add `--device cpu` or reduce `--img-size` |
| Low detection accuracy | Lower `--box-thresh` to 0.2 |
| Too many false positives | Raise `--box-thresh` to 0.5 |
| Import errors | Make sure `pip install -r requirements.txt` completed without errors |