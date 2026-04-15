"""test if birdnet works properly"""

import birdnet
from dotenv import load_dotenv

load_dotenv()

# audio_model = birdnet.load("acoustic", "2.4", "tf")

audio_model = birdnet.load_perch_v2("CPU")

predictions = audio_model.predict(
    "example/Colaptes_auratus.ogg",
    # "example/soundscape.wav",
    # custom_species_list="example/species_list.txt",
)
print(predictions.to_structured_array())
