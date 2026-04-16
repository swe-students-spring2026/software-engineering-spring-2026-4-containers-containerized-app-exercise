from pathlib import Path
from app.db import create_pending_scan

image_path = (Path("sample_data") / "test.jpg").resolve().as_posix()

scan_id = create_pending_scan(image_path)

print("Inserted document ID:", scan_id)
print("Image path:", image_path)