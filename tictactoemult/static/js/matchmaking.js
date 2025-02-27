// JavaScript file for matchmaking page

// Finding opponent text animation
var findingOpponent = document.getElementById("finding-opponent");
var dots = ""
const findingOpponentInterval = setInterval(function() {
    dots = dots + "."
    if (dots.length > 5) {
        dots = ".";
    }
    findingOpponent.innerHTML = "Finding opponent" + dots
}, 1000)

// Time elapsed timer
var timeElapsed = document.getElementById("time-elapsed");
var hours = 0;
var minutes = 0
var seconds = 0;

// Interval of one second
const timeElapsedInterval = setInterval(function() {
    // Deal with seconds and minutes going to 60
    seconds = seconds + 1;
    if (seconds == 60) {
        seconds = 0;
        minutes++;
    }
    if (minutes == 60) {
        minutes = 0;
        hours++;
    }

    // Add an extra zero if the length of the variable is one

    // convert everything to string
    seconds_str = String(seconds);
    minutes_str = String(minutes);
    hours_str = String(hours);

    if (seconds_str.length == 1) {
        seconds_str = "0" + seconds_str;
    }

    if (minutes_str.length == 1) {
        minutes_str = "0" + minutes_str;
    }

    if (hours_str.length == 1) {
        hours_str = "0" + hours_str;
    }
    timeElapsed.innerHTML = `${hours_str}:${minutes_str}:${seconds_str}`
}, 1000)

const matchmakingSocket = new WebSocket('ws://' + window.location.host + "/matchmaking")

matchmakingSocket.onmessage = function(e) {
    const data = JSON.parse(e.data)
    console.log(data)
}

// event listener for cancelling matchmaking
document.getElementById("cancel").addEventListener("click", function() {
    matchmakingSocket.close()
    window.location = "/main";
})