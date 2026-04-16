(function () {
  "use strict";

  const refreshMs = Number(document.body.dataset.refreshMs || 3000);

  let lastSpokenLabel = "";
  let lastPredictionId = "";
  let currentCameraStream = null;

  function updateText(id, value) {
    const el = document.getElementById(id);
    if (el) {
      el.textContent = value;
    }
  }

  function updateValue(id, value) {
    const el = document.getElementById(id);
    if (el) {
      el.value = value;
    }
  }

  function buildRecentRow(item) {
    return `
      <tr>
        <td>${item.timestamp ?? "N/A"}</td>
        <td>${item.predicted_label ?? "N/A"}</td>
        <td>${item.confidence ?? 0}</td>
      </tr>
    `;
  }

  function renderLabelChips(labelCounts) {
    const container = document.getElementById("label-chips");
    if (!container) {
      return;
    }

    const entries = Object.entries(labelCounts || {});
    if (!entries.length) {
      container.innerHTML = `<span class="chip">No data</span>`;
      return;
    }

    container.innerHTML = entries
      .map(([label, count]) => `<span class="chip">${label} · ${count}</span>`)
      .join("");
  }

  async function fetchLatest() {
    const response = await fetch("/api/latest");
    if (!response.ok) {
      throw new Error("Failed to fetch latest prediction");
    }
    return response.json();
  }

  async function fetchRecent() {
    const response = await fetch("/api/recent");
    if (!response.ok) {
      throw new Error("Failed to fetch recent predictions");
    }
    return response.json();
  }

  async function fetchStats() {
    const response = await fetch("/api/stats");
    if (!response.ok) {
      throw new Error("Failed to fetch stats");
    }
    return response.json();
  }

  function maybeAutoSpeak(data) {
    const toggle = document.getElementById("auto-speak-toggle");
    const shouldSpeak = toggle && toggle.checked;
    const label = data.predicted_label || "";
    const currentId = data.id || `${data.timestamp}-${label}`;

    if (
      shouldSpeak &&
      label &&
      label !== "N/A" &&
      currentId !== lastPredictionId &&
      label !== lastSpokenLabel
    ) {
      lastPredictionId = currentId;
      lastSpokenLabel = label;

      if (window.speakerAPI) {
        window.speakerAPI.speakLabel();
      }
    }
  }

  async function refreshDashboard() {
    const latest = await fetchLatest();
    const recent = await fetchRecent();
    const stats = await fetchStats();

    updateText("latest-label", latest.predicted_label ?? "N/A");
    updateText("latest-confidence", latest.confidence ?? 0);
    updateText("latest-timestamp", latest.timestamp ?? "N/A");

    const currentText =
      latest.current_text && latest.current_text.trim()
        ? latest.current_text
        : latest.predicted_label || "N/A";

    updateValue("accumulated-text", currentText);

    updateText("total-predictions", stats.total_predictions ?? 0);
    updateText("avg-confidence", stats.average_confidence ?? 0);
    updateText("top-label", stats.top_label ?? "N/A");

    const recentTableBody = document.getElementById("recent-table-body");
    if (recentTableBody) {
      if (recent.length) {
        recentTableBody.innerHTML = recent.map(buildRecentRow).join("");
      } else {
        recentTableBody.innerHTML =
          '<tr><td colspan="3">No prediction data available yet.</td></tr>';
      }
    }

    renderLabelChips(stats.label_counts);
    maybeAutoSpeak(latest);
  }

  async function startCamera() {
    const video = document.getElementById("camera-preview");
    const button = document.getElementById("camera-toggle-btn");

    if (!video || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert("Camera is not supported in this browser.");
      return;
    }

    if (currentCameraStream) {
      currentCameraStream.getTracks().forEach((track) => track.stop());
      currentCameraStream = null;
      video.srcObject = null;

      if (button) {
        button.textContent = "📷 Start Camera";
      }
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false
      });

      currentCameraStream = stream;
      video.srcObject = stream;

      if (button) {
        button.textContent = "⏹ Stop Camera";
      }
    } catch (error) {
      console.error("Camera access denied or unavailable:", error);
      alert("Unable to access the camera. Please allow camera permission in your browser.");
    }
  }

  window.addEventListener("load", function () {
    window.setTimeout(function () {
      document.body.classList.remove("is-preload");
    }, 100);

    const cameraBtn = document.getElementById("camera-toggle-btn");
    if (cameraBtn) {
      cameraBtn.addEventListener("click", function () {
        startCamera();
      });
    }

    if (!document.getElementById("latest-label")) {
      return;
    }

    refreshDashboard().catch(console.error);
    window.setInterval(function () {
      refreshDashboard().catch(console.error);
    }, refreshMs);
  });
})();