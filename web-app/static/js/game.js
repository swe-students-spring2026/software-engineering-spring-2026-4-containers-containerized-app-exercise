(function () {
  "use strict";

  const STABLE_MS = 2000;
  const FEEDBACK_MS = 2000;

  let challenges = [];
  let progress = {
    current_level: 0,
    completed_words: [],
    earned_medals: [],
    game_status: "idle"
  };

  let gameRunning = false;
  let matchedCount = 0;
  let stableCandidate = "";
  let stableSince = 0;
  let acceptedStableCandidate = false;
  let feedbackTimeoutId = null;

  function $(id) {
    return document.getElementById(id);
  }

  function currentChallenge() {
    return challenges[progress.current_level] || null;
  }

  function normalizedTargetCharacters(challenge) {
    if (!challenge || !challenge.target_text) {
      return [];
    }

    return challenge.target_text
      .toUpperCase()
      .split("")
      .filter((character) => character !== " ");
  }

  async function saveProgress() {
    await fetch("/api/game/save-progress", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(progress)
    });
  }

  async function loadGameConfig() {
    const response = await fetch("/api/game/config");
    if (!response.ok) {
      throw new Error("Failed to load game config.");
    }

    const data = await response.json();
    challenges = data.challenges || [];
    progress = data.progress || progress;

    matchedCount = 0;
    stableCandidate = "";
    stableSince = 0;
    acceptedStableCandidate = false;

    renderAll();
  }

  function updateGameStatus(statusText) {
    progress.game_status = statusText.toLowerCase();
    const statusEl = $("game-status-text");
    if (statusEl) {
      statusEl.textContent = statusText;
    }
  }

  function showFeedback(message) {
    const feedback = $("game-feedback");
    if (!feedback) {
      return;
    }

    feedback.textContent = message;
    feedback.classList.add("is-visible");

    if (feedbackTimeoutId) {
      window.clearTimeout(feedbackTimeoutId);
    }

    feedbackTimeoutId = window.setTimeout(() => {
      feedback.classList.remove("is-visible");
      feedback.textContent = "";
      feedbackTimeoutId = null;
    }, FEEDBACK_MS);
  }

  function renderCurrentLevelCard() {
    const levelText =
      progress.current_level < challenges.length
        ? String(progress.current_level + 1)
        : String(challenges.length);

    const levelEl = $("game-current-level");
    if (levelEl) {
      levelEl.textContent = levelText;
    }
  }

  function renderStableLetter(letter) {
    const stableEl = $("game-stable-letter");
    if (stableEl) {
      stableEl.textContent = letter || "-";
    }
  }

  function renderChallengeSlots() {
    const container = $("challenge-slots");
    const challenge = currentChallenge();

    if (!container || !challenge) {
      return;
    }

    const displayText = challenge.display_text || "";
    let letterIndex = 0;

    container.innerHTML = "";

    for (const character of displayText) {
      if (character === " ") {
        const gap = document.createElement("span");
        gap.className = "challenge-gap";
        gap.textContent = " ";
        container.appendChild(gap);
        continue;
      }

      const slot = document.createElement("span");
      slot.className = "challenge-slot";
      slot.textContent = character;

      if (letterIndex < matchedCount) {
        slot.classList.add("matched");
      }

      container.appendChild(slot);
      letterIndex += 1;
    }
  }

  function renderChallengePanel() {
    const challenge = currentChallenge();

    if (!challenge) {
      $("challenge-display-text").textContent = "All Challenges Complete";
      $("challenge-image").src = "";
      $("challenge-image").alt = "Completed";
      $("challenge-slots").innerHTML = "";
      return;
    }

    $("challenge-display-text").textContent = challenge.display_text;
    $("challenge-image").src = `/static/images/${challenge.image}`;
    $("challenge-image").alt = challenge.display_text;
    renderChallengeSlots();
  }

  function renderMedalWall() {
    const wall = $("medal-wall");
    if (!wall) {
      return;
    }

    wall.innerHTML = "";

    challenges.forEach((challenge) => {
      const card = document.createElement("div");
      card.className = "medal-card";

      const unlocked =
        progress.earned_medals.includes(challenge.image) ||
        progress.completed_words.includes(challenge.display_text);

      if (unlocked) {
        card.classList.add("unlocked");
      }

      const img = document.createElement("img");
      img.src = `/static/images/${challenge.image}`;
      img.alt = challenge.display_text;
      img.className = "medal-image";

      const label = document.createElement("span");
      label.className = "medal-label";
      label.textContent = challenge.display_text;

      card.appendChild(img);
      card.appendChild(label);
      wall.appendChild(card);
    });
  }

  function renderAll() {
    renderCurrentLevelCard();
    renderStableLetter(stableCandidate);
    renderChallengePanel();
    renderMedalWall();

    if (!progress.game_status) {
      updateGameStatus("Idle");
    } else {
      const statusText =
        progress.game_status.charAt(0).toUpperCase() +
        progress.game_status.slice(1);
      const statusEl = $("game-status-text");
      if (statusEl) {
        statusEl.textContent = statusText;
      }
    }
  }

  function resetStableTracking() {
    stableCandidate = "";
    stableSince = 0;
    acceptedStableCandidate = false;
    renderStableLetter("-");
  }

  function resetCurrentChallengeState() {
    matchedCount = 0;
    resetStableTracking();
    renderChallengeSlots();
  }

  function completeCurrentChallenge() {
    const challenge = currentChallenge();
    if (!challenge) {
      return;
    }

    if (!progress.completed_words.includes(challenge.display_text)) {
      progress.completed_words.push(challenge.display_text);
    }

    if (!progress.earned_medals.includes(challenge.image)) {
      progress.earned_medals.push(challenge.image);
    }

    updateGameStatus("Completed");
    showFeedback(
      `Match success! You earned the ${challenge.display_text} medal.`
    );

    progress.current_level += 1;
    matchedCount = 0;
    resetStableTracking();

    if (progress.current_level >= challenges.length) {
      updateGameStatus("Completed");
      gameRunning = false;
      renderAll();
      saveProgress().catch(console.error);
      return;
    }

    renderAll();
    saveProgress().catch(console.error);

    window.setTimeout(() => {
      if (gameRunning) {
        updateGameStatus("Running");
      }
      renderAll();
    }, FEEDBACK_MS);
  }

  function applyStableLetter(letter) {
    const challenge = currentChallenge();
    if (!challenge) {
      return;
    }

    const targetCharacters = normalizedTargetCharacters(challenge);
    const expected = targetCharacters[matchedCount];

    if (!expected) {
      return;
    }

    if (letter === expected) {
      matchedCount += 1;
      updateGameStatus("Matched");
      renderChallengeSlots();

      resetStableTracking();

      if (matchedCount === targetCharacters.length) {
        completeCurrentChallenge();
        return;
      }

      window.setTimeout(() => {
        if (gameRunning) {
          updateGameStatus("Running");
        }
      }, 350);

      return;
    }

    matchedCount = 0;
    renderChallengeSlots();
    updateGameStatus("Failed");
    resetStableTracking();

    window.setTimeout(() => {
      if (gameRunning) {
        updateGameStatus("Running");
      }
    }, 700);
  }

  function startGame() {
    gameRunning = true;
    resetCurrentChallengeState();
    updateGameStatus("Running");
    renderAll();
  }

  function stopGame() {
    gameRunning = false;
    updateGameStatus("Stopped");
    renderAll();
    saveProgress().catch(console.error);
  }

  async function restartGame() {
    const response = await fetch("/api/game/reset", {
      method: "POST"
    });

    if (!response.ok) {
      throw new Error("Failed to reset game progress.");
    }

    const data = await response.json();
    progress = data.progress;
    gameRunning = false;
    matchedCount = 0;
    resetStableTracking();

    const feedback = $("game-feedback");
    if (feedback) {
      feedback.textContent = "";
      feedback.classList.remove("is-visible");
    }

    updateGameStatus("Idle");
    renderAll();
  }

  document.addEventListener("prediction-update", function (event) {
    const detail = event.detail || {};
    const label = (detail.label || "").trim().toUpperCase();

    if (!gameRunning || !label || label === "N/A") {
      return;
    }

    if (label !== stableCandidate) {
      stableCandidate = label;
      stableSince = Date.now();
      acceptedStableCandidate = false;
      renderStableLetter(label);
      return;
    }

    renderStableLetter(label);

    if (!acceptedStableCandidate && Date.now() - stableSince >= STABLE_MS) {
      acceptedStableCandidate = true;
      applyStableLetter(label);
      saveProgress().catch(console.error);
    }
  });

  window.addEventListener("load", function () {
    const startBtn = $("game-start-btn");
    const stopBtn = $("game-stop-btn");
    const restartBtn = $("game-restart-btn");

    if (startBtn) {
      startBtn.addEventListener("click", function () {
        startGame();
      });
    }

    if (stopBtn) {
      stopBtn.addEventListener("click", function () {
        stopGame();
      });
    }

    if (restartBtn) {
      restartBtn.addEventListener("click", function () {
        restartGame().catch(console.error);
      });
    }

    loadGameConfig().catch(console.error);
  });
})();
