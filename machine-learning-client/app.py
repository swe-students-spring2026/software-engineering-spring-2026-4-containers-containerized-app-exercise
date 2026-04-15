"""machine learning client"""

from pathlib import Path
import tempfile

import av

# disabled pylint no-name-in-module
# as it cannot find FFmpegError

from av.error import FFmpegError

import birdnet
from flask import Flask, jsonify, render_template, request
import numpy as np
from numpy import float32
import numpy.typing as npt

from dotenv import load_dotenv

# import .config
# pylint complains about relative imports.
# machine-learning-client is not a valid module name
# so, we cannot import anything.
# to-do: fix this later

load_dotenv()

app = Flask(__name__)


audio_model = birdnet.load("acoustic", "2.4", "tf")


RATE = 48000
APPLY_SIGMOID = True
SIGMOID_SENSITIVITY = 1.2
DEFAULT_CONFIDENCE_THRESHOLD = 0.8  # 0.8

print(f"""birdnet inference options:
      RATE {RATE}
      APPLY_SIGMOID {APPLY_SIGMOID}
      SIGMOID_SENSITIVITY {SIGMOID_SENSITIVITY}
      DEFAULT_CONFIDENCE_THRESHOLD {DEFAULT_CONFIDENCE_THRESHOLD}
""")


@app.after_request
def add_cors_headers(response):
    """enable cors"""
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


@app.route("/")
def test():
    """test path"""
    return render_template("test.html")


@app.post("/analyze")
async def analyze():
    """send chunks here"""
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as data_file:
        data_file_path = Path(data_file.name)

        _ = data_file.write(request.data)

        try:
            if not request.data:
                return jsonify(error="Invalid Input", message="Audio empty"), 400

            # audio = extract_audio(data_file_path)
            # prediction = audio_model.predict_arrays((audio, RATE))

            prediction = audio_model.predict(
                data_file_path,
                apply_sigmoid=APPLY_SIGMOID,
                sigmoid_sensitivity=SIGMOID_SENSITIVITY,
                default_confidence_threshold=DEFAULT_CONFIDENCE_THRESHOLD,
            )

            df = prediction.to_dataframe()

            return jsonify(df.to_json(orient="records"))

        except (FFmpegError, ValueError) as e:
            return jsonify(error=str(e), message="PyAV error:"), 400

        finally:
            if data_file_path.exists():
                data_file_path.unlink()


def extract_audio(
    input_path: Path,
    rate=48000,
    max_sec=3.0,
    # min_sec=1.5
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
