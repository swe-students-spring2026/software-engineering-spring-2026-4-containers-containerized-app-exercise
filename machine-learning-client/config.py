"""config.py"""

import os
import birdnet
from dotenv import load_dotenv

audio_model = birdnet.load("acoustic", "2.4", "tf")
geo_model = birdnet.load("geo", "2.4", "tf")


_ = load_dotenv()

NUM_CPUS = os.cpu_count()
