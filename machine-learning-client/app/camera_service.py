import os
import cv2
import time
from datetime import datetime

def capture_image(output_dir = 'sample_data'):
    print("inside capture_image")
    os.makedirs(output_dir, exist_ok = True)
    camera = cv2.VideoCapture(1)
    print("camera opened object created")

    if not camera.isOpened():
        raise RuntimeError('Could not open camera')
    
    print("camera appears open")
    time.sleep(2)

    success, frame = camera.read()
    print(f"read success: {success}")
    camera.release()
    if not success:
        raise RuntimeError('Could not capture image')
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    image_path = os.path.join(output_dir, f'scan_{timestamp}.jpg')

    saved = cv2.imwrite(image_path, frame)
    print(f"image saved: {saved}")

    if not saved:
        raise RuntimeError('Could not save image')

    return image_path