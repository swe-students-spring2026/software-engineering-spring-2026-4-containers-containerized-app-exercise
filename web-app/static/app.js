let isListening = false;

const btn = document.getElementById("toggleBtn");
const statusText = document.getElementById("statusText");
const statusDot = document.getElementById("statusDot");
const detectionList = document.getElementById("detectionList");

let seconds = 0;
let timer_interval = null;
let record_interval = null;

function updateTimer() {
    seconds++;
    let minutes = Math.floor(seconds / 60);
    let secs = seconds % 60;
    //make into text and 2 digits
    minutes = minutes.toString().padStart(2, "0");
    secs = seconds.toString().padStart(2, "0");
    document.getElementById("timer").textContent = `${minutes}:${secs}`;
}

async function recordChunk() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true, mimeType: 'audio/ogg' });

    const recorder = new MediaRecorder(stream);
    const chunks = [];

    recorder.ondataavailable = e => chunks.push(e.data);
    recorder.onstop = async () => {
        const blob = new Blob(chunks, { type: "audio/ogg; codecs=opus" });
        const res = await fetch("http://localhost:8000/analyze", {
            method: "POST",
            headers: { "Content-Type": "audio/ogg" },
            body: blob,
        });
        const detections = await res.json();
        console.log("Birds detected:", detections);
    };

    recorder.start();
    setTimeout(() => recorder.stop(), 3000);
}

//detections
function renderDetections(detections) {
    detectionList.innerHTML = "";
    detections.forEach(d => {
        const item = document.createElement("div");
        item.className = "detection-item";
        item.innerHTML = `
            <div class="bird-name">${d.name}</div>
            <div class="meta">
                Confidence: ${d.confidence}% • ${d.time}
            </div>
        `;
        detectionList.appendChild(item);
    });
}

function loadDetections() {
    fetch("/detections")
        .then(res => res.json())
        .then(data => renderDetections(data));
}

//start listening and stop listening
btn.addEventListener("click", () => {
    isListening = !isListening;

    if (isListening) {
        btn.textContent = "Stop Listening";
        btn.classList.remove("start");
        btn.classList.add("stop");

        statusText.textContent = "Listening...";
        statusDot.classList.remove("idle");
        statusDot.classList.add("active");
        seconds = 0;
        document.getElementById("timer").textContent = "00:00";
        timer_interval = setInterval(updateTimer, 1000); // update timer every second

        recordChunk();
        record_interval = setInterval(recordChunk, 3000); // new recorder every 3s


        // later: call backend API
        // fetch("/start")

        // fetch("/start").then(response => response.json()).then(data => console.log(data));

    } else {
        btn.textContent = "Start Listening";
        btn.classList.remove("stop");
        btn.classList.add("start");

        statusText.textContent = "Idle";
        statusDot.classList.remove("active");
        statusDot.classList.add("idle")

        clearInterval(timer_interval);
        timer_interval = null;

        clearInterval(record_interval); 
        record_interval = null;

        // fetch("/stop").then(response => response.json()).then(data => console.log(data));
    }
});

loadDetections();