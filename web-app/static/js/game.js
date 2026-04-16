(function () {
  "use strict";

  const STABLE_MS = 3000;

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

  function $(id) {
    return document.getElementById(id);
  }

  function currentChallenge() {
    return challenges[progress.current_level] || null;
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
    $("game-status-text").textContent = statusText;
  }

  function renderCurrentLevelCard() {
    const levelText =
      progress.current_level < challenges.length
        ? String(progress.current_level + 1)
        : String(challenges.length);
    $("game-current-level").textContent = levelText;
  }

  function renderStableLetter(letter) {
    $("game-stable-letter").textContent = letter || "-";
  }

  function renderChallengeSlots() {
    const container = $("challenge-slots");
    const challenge = currentChallenge();

    if (!container || !challenge) {
      return;
    }

    const displayText = challenge.display_text;
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

      const unlocked = progress.earned_medals.includes(challenge.image);
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
      $("game-status-text").textContent =
        progress.game_status.charAt(0).toUpperCase() +
        progress.game_status.slice(1);
    }
  }

  function resetCurrentChallengeState() {
    matchedCount = 0;
    stableCandidate = "";
    stableSince = 0;
    acceptedStableCandidate = false;
    renderStableLetter("-");
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

    progress.current_level += 1;
    matchedCount = 0;
    stableCandidate = "";
    stableSince = 0;
    acceptedStableCandidate = false;

    if (progress.current_level >= challenges.length) {
      progress.current_level = challenges.length - 1;
      updateGameStatus("Completed");
      gameRunning = false;
    } else {
      updateGameStatus("Completed");
      window.setTimeout(() => {
        if (gameRunning) {
          updateGameStatus("Running");
        }
        renderAll();
      }, 900);
    }

    renderAll();
    saveProgress().catch(console.error);
  }

  function applyStableLetter(letter) {
    const challenge = currentChallenge();
    if (!challenge) {
      return;
    }

    const targetCharacters = challenge.target_text.split("");
    const expected = targetCharacters[matchedCount];

    if (letter === expected) {
      matchedCount += 1;
      renderChallengeSlots();

      if (matchedCount === targetCharacters.length) {
        completeCurrentChallenge();
      }
      return;
    }

    matchedCount = 0;
    renderChallengeSlots();
    updateGameStatus("Failed");

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
    stableCandidate = "";
    stableSince = 0;
    acceptedStableCandidate = false;

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
