"""the Dockerfile runs this file to auto-download the weights"""

import birdnet

audio_model = birdnet.load("acoustic", "2.4", "tf")
geo_model = birdnet.load("geo", "2.4", "tf")
