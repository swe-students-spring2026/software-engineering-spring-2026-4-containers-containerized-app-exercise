(function () {
  "use strict";

  function speak(text) {
    if (!text || !window.speechSynthesis) {
      return;
    }

    const synth = window.speechSynthesis;
    synth.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = 0.95;
    utterance.pitch = 1;
    utterance.volume = 1;

    const voices = synth.getVoices();
    const englishVoice = voices.find((voice) => voice.lang && voice.lang.startsWith("en"));

    if (englishVoice) {
      utterance.voice = englishVoice;
    }

    utterance.onstart = function () {
      console.log("Speech started:", text);
    };

    utterance.onend = function () {
      console.log("Speech ended");
    };

    utterance.onerror = function (event) {
      console.error("Speech error:", event);
    };

    synth.speak(utterance);
  }

  function getCurrentLabel() {
    const el = document.getElementById("latest-label");
    return el ? el.textContent.trim() : "";
  }

  function getCurrentText() {
    const el = document.getElementById("accumulated-text");
    return el ? el.value.trim() : "";
  }

  window.speakerAPI = {
    speakLabel() {
      const label = getCurrentLabel();
      console.log("Current label:", label);
      if (label && label !== "N/A") {
        speak(label);
      }
    },

    speakText() {
      const text = getCurrentText();
      console.log("Current text:", text);
      if (text && text !== "N/A") {
        speak(text);
      }
    },

    stop() {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    }
  };

  function loadVoices() {
    window.speechSynthesis.getVoices();
  }

  window.speechSynthesis.onvoiceschanged = loadVoices;
  loadVoices();

  window.addEventListener("load", function () {
    const speakCurrentBtn = document.getElementById("speak-current-btn");
    const speakTextBtn = document.getElementById("speak-text-btn");
    const clearTextBtn = document.getElementById("clear-text-btn");
    const textArea = document.getElementById("accumulated-text");

    if (speakCurrentBtn) {
      speakCurrentBtn.addEventListener("click", function () {
        console.log("Speak Current clicked");
        window.speakerAPI.speakLabel();
      });
    }

    if (speakTextBtn) {
      speakTextBtn.addEventListener("click", function () {
        console.log("Speak Text clicked");
        window.speakerAPI.speakText();
      });
    }

    if (clearTextBtn && textArea) {
      clearTextBtn.addEventListener("click", function () {
        textArea.value = "";
        window.speakerAPI.stop();
      });
    }
  });
})();