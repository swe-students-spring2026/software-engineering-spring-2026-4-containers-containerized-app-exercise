import os
import time
import requests

base_url = "https://api.assemblyai.com"

headers = {
    "authorization": os.environ.get("ASSEMBLYAI_API_KEY")
}

def transcribe_audio(audio_bytes):
    upload_response = requests.post(
        base_url + "/v2/upload", headers=headers, data=audio_bytes, timeout=30
    )
    audio_url = upload_response.json()["upload_url"]

    data = {
        "audio_url": audio_url,
        "language_detection": True,
        "speech_models": ["universal-3-pro", "universal-2"],
    }

    url = base_url + "/v2/transcript"
    response = requests.post(url, json=data, headers=headers, timeout=30)

    transcript_id = response.json()["id"]
    polling_endpoint = base_url + "/v2/transcript/" + transcript_id

    while True:
        transcription_result = requests.get(polling_endpoint, headers=headers, timeout=30).json()
        transcript_text = transcription_result["text"]

        if transcription_result["status"] == "completed":
            return transcript_text

        if transcription_result["status"] == "error":
            raise RuntimeError(f"Transcription failed: {transcription_result['error']}")

        time.sleep(3)