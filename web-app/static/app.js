let isListening = false;

const btn = document.getElementById("toggleBtn");
const statusText = document.getElementById("statusText");
const statusDot = document.getElementById("statusDot");

let seconds = 0;
let interval = null;

function updateTimer(){
    seconds++;
    let minutes = Math.floor(seconds/60);
    let seconds = seconds%60;
    //make into text and 2 digits
    minutes = minutes.toString().padStart(2,"0");
    seconds = seconds.toString().padStart(2,"0");
    document.getElementById("timer").textContent = `${minutes}:${seconds}`;
}

btn.addEventListener("click", () => {
    isListening = !isListening;

    if (isListening) {
        btn.textContent = "Stop Listening";
        btn.classList.remove("start");
        btn.classList.add("stop");

        statusText.textContent = "Listening...";
        statusDot.classList.remove("idle");
        statusDot.classList.add("active");
        
        seconds=0;
        interval=setInterval(updateTimer,1000);

        // later: call backend API
        // fetch("/start")
    } else {
        btn.textContent = "Start Listening";
        btn.classList.remove("stop");
        btn.classList.add("start");

        statusText.textContent = "Idle";
        statusDot.classList.remove("active");
        statusDot.classList.add("idle");

        clearInterval(interval);

        // fetch("/stop")
    }
});