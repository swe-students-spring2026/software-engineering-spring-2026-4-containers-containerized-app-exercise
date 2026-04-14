let mediaRecorder;
let audioChunks = [];
let stream;

const startButton = document.querySelector(".btn-start");
const statusText = document.querySelector("section p i");

async function startRecording() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data);
      }
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");

      statusText.textContent = "Uploading audio...";

      try {
        const response = await fetch("/api/upload-audio", {
          method: "POST",
          body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Upload failed");
        }

        statusText.textContent = "Audio uploaded and queued for processing.";
      } catch (error) {
        statusText.textContent = `Upload failed: ${error.message}`;
      }

      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }

      startButton.textContent = "⏺ Start Practice Session";
      startButton.dataset.recording = "false";
    };

    mediaRecorder.start();
    startButton.textContent = "⏹ Stop Practice Session";
    startButton.dataset.recording = "true";
    statusText.textContent = "Recording...";
  } catch (error) {
    statusText.textContent = `Microphone access failed: ${error.message}`;
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
    statusText.textContent = "Stopping recording...";
  }
}

startButton.addEventListener("click", async () => {
  const isRecording = startButton.dataset.recording === "true";

  if (!isRecording) {
    await startRecording();
  } else {
    stopRecording();
  }
});