let alarmAudio = new Audio("/static/Sound/alarm.wav");
alarmAudio.loop = true;
alarmAudio.volume = 1.0;
let soundEnabled = false;

const socket = io();

let alertCount = 0;
let alarmUnlocked = false;

// create alarm sound
const alarm = new Audio("/static/Sound/alarm.mp3.wav");
alarm.loop = true;

// unlock audio after user click
function unlockAudio() {
    alarm.play().then(() => {
        alarm.pause();
        alarm.currentTime = 0;
        alarmUnlocked = true;
        console.log("Audio unlocked");
    }).catch(err => console.log("Waiting for interaction"));
}

// Start camera
function startCamera() {
    document.getElementById("video-stream").src = "/video_feed";
    document.getElementById("status").innerText = "Status: Running";

    unlockAudio(); // 🔥 IMPORTANT
}
function enableSound() {
    alarmAudio.play().then(() => {
        alarmAudio.pause();
        alarmAudio.currentTime = 0;
        soundEnabled = true;
        console.log("Sound unlocked");
    }).catch(err => console.log("Blocked:", err));
}

// receive prediction from backend
socket.on('update_status', function(data) {
    const label = data.label;

    document.getElementById("status").innerText = "Status: " + label;

if (label === "abnormal") {
    alertCount++;
    document.getElementById("alert-counter").innerText = "Alerts: " + alertCount;

    if (soundEnabled) {
        alarmAudio.currentTime = 0;
        alarmAudio.play();
    }
} else {
    alarmAudio.pause();
}
});
