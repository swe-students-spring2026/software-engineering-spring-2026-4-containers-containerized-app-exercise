(function () {
  "use strict";

  let autoSpeakEnabled = false;

  function normalizeForSpeech(text) {
    const value = (text || "").trim();

    if (!value || value === "N/A") {
      return "";
    }

    const singleLetterMatch = /^[A-Z]$/.test(value);
    if (singleLetterMatch) {
      return value.toLowerCase();
    }

    const spacedLettersMatch = /^[A-Z](\s+[A-Z])+$/.test(value);
    if (spacedLettersMatch) {
      return value
        .split(/\s+/)
        .map((part) => part.toLowerCase())
        .join(" ");
    }

    return value;
  }

  function speak(text) {
    if (!window.speechSynthesis) {
      return;
    }

    const finalText = normalizeForSpeech(text);
    if (!finalText) {
      return;
    }

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(finalText);
    utterance.lang = "en-US";
    utterance.rate = 0.95;
    utterance.pitch = 1;
    utterance.volume = 1;

    window.speechSynthesis.speak(utterance);
  }

  function getSpeakableText() {
    const textArea = document.getElementById("accumulated-text");
    const latestLabel = document.getElementById("latest-label");

    const text = textArea ? textArea.value.trim() : "";
    if (text && text !== "N/A") {
      return text;
    }

    return latestLabel ? latestLabel.textContent.trim() : "";
  }

  function updateAutoSpeakButton() {
    const button = document.getElementById("auto-speak-btn");
    if (!button) {
      return;
    }

    button.textContent = autoSpeakEnabled ? "Auto Speak: On" : "Auto Speak: Off";
    button.classList.toggle("active-toggle", autoSpeakEnabled);
  }

  window.speakerAPI = {
    speakCurrent() {
      speak(getSpeakableText());
    },

    speakText(text) {
      speak(text);
    },

    stop() {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    },

    isAutoSpeakEnabled() {
      return autoSpeakEnabled;
    },

    toggleAutoSpeak() {
      autoSpeakEnabled = !autoSpeakEnabled;
      updateAutoSpeakButton();
      return autoSpeakEnabled;
    }
  };

  window.addEventListener("load", function () {
    const speakButton = document.getElementById("speak-btn");
    const autoSpeakButton = document.getElementById("auto-speak-btn");
    const stopSpeakerButton = document.getElementById("stop-speaker-btn");

    if (speakButton) {
      speakButton.addEventListener("click", function () {
        window.speakerAPI.speakCurrent();
      });
    }

    if (autoSpeakButton) {
      autoSpeakButton.addEventListener("click", function () {
        window.speakerAPI.toggleAutoSpeak();
      });
    }

    if (stopSpeakerButton) {
      stopSpeakerButton.addEventListener("click", function () {
        window.speakerAPI.stop();
      });
    }

    updateAutoSpeakButton();
  });
})();
