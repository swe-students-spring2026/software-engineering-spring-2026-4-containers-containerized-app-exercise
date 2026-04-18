"""Capture module for executing image captures."""

from app.camera_service import capture_image


def main():
    """Main function to start the capture script."""
    print("starting capture script")
    image_path = capture_image()
    print(f"Saved captured image to {image_path}")


if __name__ == "__main__":
    main()
