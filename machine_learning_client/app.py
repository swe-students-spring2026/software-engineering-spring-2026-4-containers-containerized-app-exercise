from pathlib import Path
import tempfile

import birdnet
from flask import Flask, jsonify, render_template, request
import numpy as np
from numpy._core import float32

# from .load_model import audio_model
import numpy.typing as npt
import av

from .config import NUM_CPUS


app = Flask(__name__)

audio_model = birdnet.load("acoustic", "2.4", "tf")


RATE = 48000


@app.route("/")
def test():
    return render_template("test.html")


@app.post("/analyze")
async def analyze():
    data_file = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
    data_file_path = Path(data_file.name)

    _ = data_file.write(request.data)

    try:
        if not request.data:
            return jsonify(error="Invalid Input", message="Audio empty"), 400

        # audio = extract_audio(data_file_path)
        # prediction = audio_model.predict_arrays((audio, RATE))

        prediction = audio_model.predict(data_file_path)

        df = prediction.to_dataframe()

        return jsonify(df.to_json())

    except Exception as e:
        return jsonify(error=str(e), message="Failed to process"), 400

    finally:
        if data_file_path.exists():
            data_file_path.unlink()


def extract_audio(
    input_path: Path, rate=48000, max_sec=3.0, min_sec=1.5
) -> npt.NDArray[np.float32]:
    """from input file, extract 3 second long recording at 48000hz"""

    in_container = av.open(input_path)

    resampler = av.AudioResampler(format="fltp", layout="mono", rate=rate)

    # resampled_audio: npt.NDArray[np.float32] = np.array([])
    resampled_audio: list[npt.NDArray[np.float32]] = []

    for frame in in_container.decode(audio=0):
        resampled_frames = resampler.resample(frame)

        for resampled_frame in resampled_frames:
            resampled_frame = resampled_frame.to_ndarray()

            # resampled_audio = np.append(resampled_audio, resampled_frame.astype(np.float32))
            resampled_audio.append(resampled_frame.astype(np.float32))

        if frame.time and frame.time >= max_sec:
            break

    audio_array: npt.NDArray[np.float32] = np.concatenate(
        resampled_audio, axis=1
    ).flatten()

    if len(audio_array) < int(rate * max_sec):
        tmp: npt.NDArray[float32] = np.zeros((int(rate * max_sec)), dtype=float32)
        tmp[: len(audio_array)] = audio_array[0]
        audio_array = np.array([tmp])

    if len(audio_array) > int(rate * max_sec):
        audio_array = audio_array[: int(rate * max_sec)]

    return audio_array


# audio = extract_audio(
#     Path(
#         # "/home/hxia/git/4-containers-lime_llamas/machine-learning-client/example/file_example_WEBM_1920_3_7MB.webm
#         # "/home/hxia/git/4-containers-lime_llamas/machine-learning-client/example/soundscape.wav"
#         "/home/hxia/git/4-containers-lime_llamas/machine-learning-client/example/Machine Gun Woodpecker - Flicker [YQ2wIOcO7aE].webm"
#     )
# )


# result = audio_model.predict_arrays((audio, 48000))

# dataframe = result.to_dataframe()

# print(dataframe.to_json())
