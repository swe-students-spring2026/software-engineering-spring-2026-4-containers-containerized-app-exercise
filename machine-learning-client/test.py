"""test if birdnet works properly"""

import birdnet

import io
import soundfile as sf

audio_model = birdnet.load("acoustic", "2.4", "pb")

predictions = audio_model.predict(
    "example/Colaptes_auratus.ogg",
    # predict only the species from the file
    # custom_species_list="example/species_list.txt",
    # batch_size=64,
)
