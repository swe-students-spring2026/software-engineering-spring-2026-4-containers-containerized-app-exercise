let mediaRecorder;
let audioChunks = [];
let stream;
let statusPollTimer;

const startButton = document.querySelector(".btn-start");
const statusText = document.querySelector("section p i");

const latestDuration = document.querySelector("#latest-duration");
const latestWpm = document.querySelector("#latest-wpm");
const latestFillerCount = document.querySelector("#latest-filler-count");
const latestPaceFeedback = document.querySelector("#latest-pace-feedback");
const latestTranscript = document.querySelector("#latest-transcript");
const latestFillerFeedback = document.querySelector("#latest-filler-feedback");

const sessionsTbody = document.querySelector("#sessions-tbody");
const wpmChartCanvas = document.querySelector("#wpmChart");
const fillerChartCanvas = document.querySelector("#fillerChart");

let wpmChart;
let fillerChart;

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

function objectIdToDate(oid) {
  if (typeof oid !== "string" || oid.length < 8) return null;
  const tsHex = oid.slice(0, 8);
  const seconds = Number.parseInt(tsHex, 16);
  if (!Number.isFinite(seconds)) return null;
  return new Date(seconds * 1000);
}

function fmtDateTime(date) {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) return "--";
  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function renderSessionsTable(sessions) {
  if (!sessionsTbody) return;
  sessionsTbody.innerHTML = "";

  if (!Array.isArray(sessions) || sessions.length === 0) {
    const tr = document.createElement("tr");
    tr.innerHTML =
      '<td colspan="5"><i>No sessions yet. Record one above.</i></td>';
    sessionsTbody.appendChild(tr);
    return;
  }

  for (const s of sessions) {
    const id = s._id;
    const createdAt = objectIdToDate(id);
    const wpm = s?.analysis?.wpm ?? "--";
    const filler = s?.analysis?.total_filler_count ?? "--";

    const tr = document.createElement("tr");
    const shortId = typeof id === "string" ? id.slice(-8) : "--";
    tr.innerHTML = `
      <td><code>${shortId}</code></td>
      <td>${fmtDateTime(createdAt)}</td>
      <td>${wpm}</td>
      <td>${filler}</td>
      <td><a href="#" data-session-id="${id}">View Details</a></td>
    `;

    const link = tr.querySelector("a[data-session-id]");
    link.addEventListener("click", (e) => {
      e.preventDefault();
      renderLatestSession(s);
      statusText.textContent = "Showing selected session.";
      window.scrollTo({ top: 0, behavior: "smooth" });
    });

    sessionsTbody.appendChild(tr);
  }
}

function buildWpmChartData(sessions) {
  const points = (Array.isArray(sessions) ? sessions : [])
    .map((s) => {
      const d = objectIdToDate(s?._id);
      const wpm = s?.analysis?.wpm;
      return { d, wpm };
    })
    .filter((p) => p.d && Number.isFinite(p.wpm))
    .sort((a, b) => a.d - b.d);

  return {
    labels: points.map((p) =>
      p.d.toLocaleDateString(undefined, { month: "2-digit", day: "2-digit" })
    ),
    data: points.map((p) => p.wpm),
  };
}

function buildFillerTotals(sessions) {
  const totals = {};
  for (const s of Array.isArray(sessions) ? sessions : []) {
    const fw = s?.analysis?.filler_words;
    if (!fw || typeof fw !== "object") continue;
    for (const [word, count] of Object.entries(fw)) {
      if (!Number.isFinite(count) || count <= 0) continue;
      totals[word] = (totals[word] || 0) + count;
    }
  }
  const sorted = Object.entries(totals).sort((a, b) => b[1] - a[1]);
  return {
    labels: sorted.map(([w]) => w),
    data: sorted.map(([, c]) => c),
  };
}

function updateCharts(sessions) {
  if (!window.Chart || !wpmChartCanvas || !fillerChartCanvas) return;

  const wpm = buildWpmChartData(sessions);
  if (!wpmChart) {
    wpmChart = new Chart(wpmChartCanvas, {
      type: "line",
      data: {
        labels: wpm.labels,
        datasets: [
          {
            label: "WPM",
            data: wpm.data,
            borderColor: "#2b6cb0",
            backgroundColor: "rgba(43, 108, 176, 0.15)",
            tension: 0.25,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { y: { beginAtZero: true } },
      },
    });
  } else {
    wpmChart.data.labels = wpm.labels;
    wpmChart.data.datasets[0].data = wpm.data;
    wpmChart.update();
  }

  const fillers = buildFillerTotals(sessions);
  if (!fillerChart) {
    fillerChart = new Chart(fillerChartCanvas, {
      type: "bar",
      data: {
        labels: fillers.labels,
        datasets: [
          {
            label: "Filler word count (total)",
            data: fillers.data,
            backgroundColor: "rgba(220, 38, 38, 0.35)",
            borderColor: "rgba(220, 38, 38, 0.85)",
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { y: { beginAtZero: true } },
      },
    });
  } else {
    fillerChart.data.labels = fillers.labels;
    fillerChart.data.datasets[0].data = fillers.data;
    fillerChart.update();
  }
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
      renderSessionsTable([]);
      updateCharts([]);
      return;
    }

    const latestSession = sessions[sessions.length - 1];
    renderLatestSession(latestSession);
    renderSessionsTable(sessions);
    updateCharts(sessions);

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

const commandId = data.command_id;

        statusText.textContent = "Processing audio (waiting for ML results)...";

        if (statusPollTimer) clearInterval(statusPollTimer);
        statusPollTimer = setInterval(async () => {
          try {
            const statusRes = await fetch(`/api/commands/${commandId}`);
            const statusData = await statusRes.json();


            if (statusData.status === "done" && statusData.result_id) {
              clearInterval(statusPollTimer);
              statusPollTimer = null;

              statusText.textContent = "Done. Results updated.";
              await loadLatestSession();
              return;
            }

            statusText.textContent = `Processing audio... (${statusData.status})`;
          
          } catch (error) {
            statusText.textContent = `Upload failed: ${error.message}`;
          }
        }, 2000);

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