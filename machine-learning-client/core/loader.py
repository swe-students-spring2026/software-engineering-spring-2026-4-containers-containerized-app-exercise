import os
import cv2

def load_images(folder):
    images = []

    for file in os.listdir(folder):
        if file.lower().endswith((".jpg", ".png", ".jpeg")):
            path = os.path.join(folder, file)
            img = cv2.imread(path)

            if img is None:
                print(f"[SKIP] cannot read image: {path}")
                continue
            
            images.append((file, img))

    return images