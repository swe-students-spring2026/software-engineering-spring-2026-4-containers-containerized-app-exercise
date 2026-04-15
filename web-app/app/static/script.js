let mediaRecorder;
let audioChunks = [];
let stream;

const startButton = document.querySelector(".btn-start");
const statusText = document.querySelector("section p i");

const latestDuration = document.querySelector("#latest-duration");
const latestWpm = document.querySelector("#latest-wpm");
const latestFillerCount = document.querySelector("#latest-filler-count");
const latestPaceFeedback = document.querySelector("#latest-pace-feedback");
const latestTranscript = document.querySelector("#latest-transcript");
const latestFillerFeedback = document.querySelector("#latest-filler-feedback");

function renderLatestSession(session) {
  if (!session) {
    latestDuration.textContent = "No session yet";
    latestWpm.textContent = "--";
    latestFillerCount.textContent = "--";
    latestPaceFeedback.textContent = "--";
    latestTranscript.textContent = "No transcript yet.";
    latestFillerFeedback.innerHTML = "<i>No feedback yet.</i>";
    return;
  }

  latestDuration.textContent = `${session.duration_seconds} seconds`;
  latestWpm.textContent = session.analysis.wpm;
  latestFillerCount.textContent = session.analysis.total_filler_count;
  latestPaceFeedback.textContent = session.analysis.pace_feedback;
  latestTranscript.textContent = session.transcript || "No transcript available.";
  latestFillerFeedback.innerHTML = `<i>${session.analysis.filler_feedback}</i>`;
}

async function loadLatestSession() {
  try {
    const response = await fetch("/api/sessions");
    const sessions = await response.json();

    if (!response.ok) {
      throw new Error("Failed to load sessions");
    }

    if (!Array.isArray(sessions) || sessions.length === 0) {
      renderLatestSession(null);
      return;
    }

    const latestSession = sessions[sessions.length - 1];
    renderLatestSession(latestSession);
  } catch (error) {
    console.error("Error loading latest session:", error);
  }
}

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

        setTimeout(loadLatestSession, 5000);
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

loadLatestSession();