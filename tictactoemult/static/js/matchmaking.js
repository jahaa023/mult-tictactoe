// JavaScript file for matchmaking page

// Get gamemode in url
const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const gamemode = urlParams.get("m")

// Get csrftoken from cookie
const csrfmiddlewaretoken = document.cookie.split(';')
    .find(cookie => cookie.trim().startsWith('csrftoken='))
    ?.split('=')[1];

// Define row id var
var row_id = 0;

// Function that fetches startup details
function startup() {
    var url = "/matchmaking_onload"

    fetch(url, {
        method: "POST",
        body: JSON.stringify({
            "user_id": user_id,
            "gamemode": gamemode
        }),
        headers : {
            "X-CSRFToken" : csrfmiddlewaretoken
        },
        credentials: "same-origin"
    })

    .then(response => response.json())

    .then(response => {
        if (response.nonefound == 0) {
            // Opponent was found, send message that you joined the row
            matchmakingSocket.send(JSON.stringify({
                "message": "joining_row",
                "row_id": response.row_id,
                "user_id_1": response.user_id_1
            }))
            alert(response.row_id)
        }
    })
}

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

// connect to websocket and listen for messages
const matchmakingSocket = new WebSocket('ws://' + window.location.host + "/ws/matchmaking/")
matchmakingSocket.onmessage = function(e) {
    const data = JSON.parse(e.data)
    console.log(data)
    
    // Read the message type
    var messagetype = data.message;
    switch(messagetype) {
        case "joining_row":
            var row = data.row_id
            var user_id_1 = data.user_id_1

            checkJoinedRow(row, user_id_1)
        case "match_created":
            var row_id = data.row_id
            var room_name = data.room_name
            var user_id = data.user_id

            checkMatchCreated(row_id, room_name, user_id)
    }
}

// event listener for cancelling matchmaking
document.getElementById("cancel").addEventListener("click", function() {
    var url = "/matchmaking_cancel"

    fetch(url, {
        method: "GET",
        credentials: "same-origin",
        headers : {
            "X-CSRFToken" : csrfmiddlewaretoken
        }
    })

    .then(response => response.json())

    .then(response => {
        if (response.ok == 1) {
            matchmakingSocket.send(JSON.stringify({
                "message": "cancel_match",
                "user_id": user_id,
                "row_id": response.row_id
            }))
        }
    })

    .finally(() => {
        matchmakingSocket.close()
        window.location = "/main";
    })
})

// Function that check if the row that was joined is your row
function checkJoinedRow(row_id, user_id_1) {
    var url = "/check_joined_row"

    fetch(url, {
        method: "POST",
        body: JSON.stringify({
            "row_id": row_id,
            "user_id_1": user_id_1
        }),
        headers : {
            "X-CSRFToken" : csrfmiddlewaretoken
        },
        credentials: "same-origin"
    })

    .then(response => response.json())

    .then(response => {
        if (response.yourrow == 1) {
            matchmakingSocket.send(JSON.stringify({
                "message": "match_created",
                "user_id": response.user_id,
                "row_id": response.row_id,
                "room_name": response.room_name
            }))

            window.location = "/match?rn=" + response.room_name
        }
    })

    .catch(error => {
        console.error(error)
    })
}

// Checks if the match that was created includes you
function checkMatchCreated(row_id, room_name, user_id) {
    var url = "/check_match_created"

    fetch(url, {
        method: "POST",
        body: JSON.stringify({
            "row_id": row_id,
            "user_id": user_id,
            "room_name": room_name
        }),
        headers : {
            "X-CSRFToken" : csrfmiddlewaretoken
        },
        credentials: "same-origin"
    })

    .then(response => response.json())

    .then(response => {
        if (response.yourmatch == 1) {
            window.location = "/match?rn=" + room_name
        }
    })

    .catch(error => {
        console.error(error)
    })
}

setTimeout(startup, 500)