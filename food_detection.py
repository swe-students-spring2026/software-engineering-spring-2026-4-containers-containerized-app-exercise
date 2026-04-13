"""
Open-vocabulary food detection using Grounding DINO.
Supports both groundingdino-py and HuggingFace transformers backends.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

import cv2
import numpy as np

try:
    import torch
except ImportError:
    print("Error: PyTorch is required. Install via: pip install torch torchvision")
    sys.exit(1)

# Dot-separated class prompt for Grounding DINO (add/remove as needed)
DEFAULT_FOOD_CLASSES = (
    "rice. noodle. soup. bread. sandwich. hamburger. pizza. hot dog. "
    "sushi. dumpling. spring roll. fried rice. fried chicken. steak. "
    "grilled fish. salmon. shrimp. lobster. crab. "
    "salad. broccoli. carrot. corn. tomato. cucumber. potato. "
    "egg. tofu. cheese. butter. yogurt. "
    "cake. cookie. donut. ice cream. chocolate. pie. pancake. waffle. "
    "apple. banana. orange. grape. strawberry. watermelon. mango. "
    "coffee. tea. juice. milk. beer. wine. water bottle. soda. "
    "french fries. taco. burrito. pasta. ramen. pho. curry. "
    "chicken wing. bacon. sausage. ham. "
    "bowl of food. plate of food. dish"
)

IMG_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"}


def parse_args():
    parser = argparse.ArgumentParser(description="Food Detection (Grounding DINO)")
    parser.add_argument("--input", "-i", type=str, required=True, help="Path to input image directory")
    parser.add_argument("--output", "-o", type=str, default="./results", help="Path to output directory")
    parser.add_argument("--classes", type=str, default=DEFAULT_FOOD_CLASSES,
                        help="Dot-separated food classes (e.g. 'sushi. ramen. rice')")
    parser.add_argument("--box-thresh", type=float, default=0.35, help="Box confidence threshold")
    parser.add_argument("--text-thresh", type=float, default=0.25, help="Text matching threshold")
    parser.add_argument("--device", type=str, default="", help="Device: 'cpu' or 'cuda'")
    parser.add_argument("--save-crop", action="store_true", help="Save cropped detections")
    return parser.parse_args()


def get_image_files(input_dir: str) -> list:
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"Error: Input directory '{input_dir}' does not exist")
        sys.exit(1)
    image_files = sorted(f for f in input_path.iterdir() if f.suffix.lower() in IMG_EXTENSIONS)
    if not image_files:
        print(f"Error: No image files found in '{input_dir}'")
        sys.exit(1)
    print(f"Found {len(image_files)} images")
    return image_files


def load_model(device: str):
    """Load Grounding DINO. Tries groundingdino-py first, falls back to HuggingFace."""
    try:
        from groundingdino.util.inference import load_model as gd_load_model
        import groundingdino

        gd_dir = Path(groundingdino.__file__).parent
        config_path = gd_dir / "config" / "GroundingDINO_SwinT_OGC.py"
        if not config_path.exists():
            config_path = gd_dir / "config" / "GroundingDINO_SwinB.py"

        weights_dir = Path.home() / ".cache" / "groundingdino"
        weights_dir.mkdir(parents=True, exist_ok=True)
        weights_path = weights_dir / "groundingdino_swint_ogc.pth"

        if not weights_path.exists():
            print("Downloading Grounding DINO weights (first run only)...")
            url = "https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth"
            torch.hub.download_url_to_file(url, str(weights_path))

        model = gd_load_model(str(config_path), str(weights_path), device=device)
        print("Loaded Grounding DINO (groundingdino-py)")
        return model, "groundingdino"

    except ImportError:
        print("groundingdino-py not found, trying HuggingFace transformers...")

    try:
        from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection

        model_id = "IDEA-Research/grounding-dino-tiny"
        print(f"Loading {model_id} (~700MB on first run)...")
        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id)
        model = model.to(device)
        model.eval()
        print("Loaded Grounding DINO (HuggingFace)")
        return (model, processor), "transformers"

    except ImportError:
        print("\nError: Install one of the following:")
        print("  Option 1: pip install groundingdino-py")
        print("  Option 2: pip install transformers[torch]")
        sys.exit(1)


def detect_groundingdino(model, image_path: str, text_prompt: str,
                         box_threshold: float, text_threshold: float, device: str):
    """Run inference with the groundingdino-py backend."""
    from groundingdino.util.inference import predict, load_image

    image_source, image_tensor = load_image(image_path)
    boxes, logits, phrases = predict(
        model=model,
        image=image_tensor,
        caption=text_prompt,
        box_threshold=box_threshold,
        text_threshold=text_threshold,
        device=device,
    )
    h, w, _ = image_source.shape
    detections = []
    for i in range(len(boxes)):
        cx, cy, bw, bh = boxes[i].tolist()
        x1, y1 = (cx - bw / 2) * w, (cy - bh / 2) * h
        x2, y2 = (cx + bw / 2) * w, (cy + bh / 2) * h
        detections.append({
            "class_name": phrases[i].strip(),
            "confidence": round(logits[i].item(), 4),
            "bbox_xyxy": [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)],
        })
    # load_image returns RGB; convert to BGR for cv2
    image_bgr = cv2.cvtColor(image_source, cv2.COLOR_RGB2BGR)
    return detections, image_bgr


def detect_transformers(model_tuple, image_path: str, text_prompt: str,
                        box_threshold: float, text_threshold: float, device: str):
    """Run inference with the HuggingFace transformers backend."""
    from PIL import Image

    model, processor = model_tuple
    image = Image.open(image_path).convert("RGB")
    w, h = image.size

    inputs = processor(images=image, text=text_prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)

    results = processor.post_process_grounded_object_detection(
        outputs,
        inputs.input_ids,
        box_threshold=box_threshold,
        text_threshold=text_threshold,
        target_sizes=[(h, w)],
    )[0]

    detections = []
    for i in range(len(results["boxes"])):
        box = results["boxes"][i].tolist()
        detections.append({
            "class_name": results["labels"][i].strip(),
            "confidence": round(results["scores"][i].item(), 4),
            "bbox_xyxy": [round(v, 2) for v in box],
        })

    image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    return detections, image_np


def draw_detections(image: np.ndarray, detections: list) -> np.ndarray:
    """Draw bounding boxes and labels on a BGR image."""
    img = image.copy()
    colors = {}

    for det in detections:
        cls_name = det["class_name"]
        if cls_name not in colors:
            hash_val = hash(cls_name)
            colors[cls_name] = (
                (hash_val & 0xFF),
                ((hash_val >> 8) & 0xFF),
                ((hash_val >> 16) & 0xFF),
            )
        color = colors[cls_name]
        x1, y1, x2, y2 = [int(v) for v in det["bbox_xyxy"]]
        conf = det["confidence"]

        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        label = f"{cls_name} {conf:.0%}"
        (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(img, (x1, y1 - lh - 10), (x1 + lw + 4, y1), color, -1)
        cv2.putText(img, label, (x1 + 2, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    return img


def run_detection(args):
    device = args.device if args.device else ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    annotated_dir = output_dir / "annotated"
    annotated_dir.mkdir(exist_ok=True)

    model, backend = load_model(device)

    text_prompt = args.classes.strip()
    if not text_prompt.endswith("."):
        text_prompt += "."
    print(f"\nClasses: {text_prompt[:100]}{'...' if len(text_prompt) > 100 else ''}")

    image_files = get_image_files(args.input)
    all_results = []
    detect_fn = detect_groundingdino if backend == "groundingdino" else detect_transformers

    for idx, img_path in enumerate(image_files, 1):
        print(f"\n[{idx}/{len(image_files)}] {img_path.name}")

        detections, image_np = detect_fn(
            model, str(img_path), text_prompt,
            args.box_thresh, args.text_thresh, device
        )

        annotated = draw_detections(image_np, detections)
        cv2.imwrite(str(annotated_dir / img_path.name), annotated)

        img_result = {
            "filename": img_path.name,
            "num_detections": len(detections),
            "detections": detections,
        }
        all_results.append(img_result)

        if detections:
            counts = {}
            for d in detections:
                counts[d["class_name"]] = counts.get(d["class_name"], 0) + 1
            print(f"  {len(detections)} detected -> {counts}")
        else:
            print("  No detections")

        if args.save_crop:
            crop_dir = output_dir / "crops" / img_path.stem
            crop_dir.mkdir(parents=True, exist_ok=True)
            for i, d in enumerate(detections):
                x1, y1, x2, y2 = [int(v) for v in d["bbox_xyxy"]]
                crop = image_np[y1:y2, x1:x2]
                if crop.size > 0:
                    cv2.imwrite(str(crop_dir / f"{d['class_name']}_{i}_{d['confidence']:.2f}.jpg"), crop)

    # Save structured JSON (for backend/database consumption)
    summary_data = {
        "timestamp": datetime.now().isoformat(),
        "backend": backend,
        "text_prompt": text_prompt,
        "box_threshold": args.box_thresh,
        "text_threshold": args.text_thresh,
        "device": device,
        "total_images": len(image_files),
        "total_detections": sum(r["num_detections"] for r in all_results),
        "results": all_results,
    }
    json_path = output_dir / "detection_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)

    # Save human-readable report
    report_path = output_dir / "detection_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("Food Detection Report (Grounding DINO)\n")
        f.write(f"Timestamp : {summary_data['timestamp']}\n")
        f.write(f"Backend   : {backend}\n")
        f.write(f"Device    : {device}\n")
        f.write(f"Box Thresh: {args.box_thresh} | Text Thresh: {args.text_thresh}\n")
        f.write(f"Images    : {len(image_files)}\n")
        f.write(f"Detections: {summary_data['total_detections']}\n")
        f.write("=" * 60 + "\n\n")
        for r in all_results:
            f.write(f"--- {r['filename']} ---\n")
            if r["detections"]:
                for d in r["detections"]:
                    bbox = d["bbox_xyxy"]
                    f.write(
                        f"  {d['class_name']} (conf: {d['confidence']:.2%}) "
                        f"bbox: [{bbox[0]:.0f}, {bbox[1]:.0f}, {bbox[2]:.0f}, {bbox[3]:.0f}]\n"
                    )
            else:
                f.write("  No detections\n")
            f.write("\n")

    print("\n" + "=" * 60)
    print("Done!")
    print(f"  Images processed : {len(image_files)}")
    print(f"  Total detections : {summary_data['total_detections']}")
    print(f"  Annotated images : {annotated_dir}")
    print(f"  JSON results     : {json_path}")
    print(f"  Text report      : {report_path}")
    print("=" * 60)


if __name__ == "__main__":
    run_detection(parse_args())