"""Prediction script for garbage classification."""
from roboflow import Roboflow

rf = Roboflow(api_key="x0xfp0u9VthGksTIwXs8")
project = rf.workspace("material-identification").project("garbage-classification-3")
model = project.version(2).model  # loads the hosted pre-trained model

# Run inference on an image (calls Roboflow's cloud API)
result = model.predict("capture.jpg", confidence=40, overlap=30)
result.save("result.jpg")
print(result.json())
