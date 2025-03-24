// JavaScript for match page

// Get room name in url
const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const room_name = urlParams.get('rn')

// Keeps track of current round
var currentRound = 1;

// Get csrftoken from cookie
const csrfmiddlewaretoken = document.cookie.split(';')
    .find(cookie => cookie.trim().startsWith('csrftoken='))
    ?.split('=')[1];

// Connect to websocket for this room
const matchWebSocket = new WebSocket("ws://" + window.location.host + "/ws/match/" + room_name + "/")

// Listen for message and parse the message data
matchWebSocket.onmessage = function(e) {
    const data = JSON.parse(e.data)
    console.log(data)

    // Read the message type
    var messagetype = data.message;
    switch(messagetype) {
        case "move":
            if (data.user_id !== user_id) {
                // Update match
                getMatchInfo()
            }
    }
}

// Shows an error
function showError(text) {
    var errorContainer = document.getElementById("error-container")
    errorContainer.style.display = "block"
    errorContainer.innerHTML = text;
    setTimeout(function() {
        errorContainer.style.display = "none";
    }, 3000)
}

// Checks if startup animation has been done. If it hasnt, do it
function animationSequence() {
    var url = "/match_animation_sequence"

    fetch(url, {
        method: "POST",
        body: JSON.stringify({
            "room_name": room_name
        }),
        headers : {
            "X-CSRFToken" : csrfmiddlewaretoken
        },
        credentials: "same-origin"
    })

    .then(response => response.json())

    .then(response => {
        // If animation sequence hasnt been done
        if (response.done == 0) {
            // Figure out x and o
            if (response.x == response.user_id_1) {
                // o is user id 2 and x is user id 1
                document.getElementById("x-nickname").innerHTML = response.user_id_1_nickname
                document.getElementById("o-nickname").innerHTML = response.user_id_2_nickname
                document.getElementById("x-profilepic").style.backgroundImage = `url(static/img/profile_pictures/${response.user_id_1_profilepic})`
                document.getElementById("o-profilepic").style.backgroundImage = `url(static/img/profile_pictures/${response.user_id_2_profilepic})`
            } else {
                // Reverse it
                document.getElementById("o-nickname").innerHTML = response.user_id_1_nickname
                document.getElementById("x-nickname").innerHTML = response.user_id_2_nickname
                document.getElementById("o-profilepic").style.backgroundImage = `url(static/img/profile_pictures/${response.user_id_1_profilepic})`
                document.getElementById("x-profilepic").style.backgroundImage = `url(static/img/profile_pictures/${response.user_id_2_profilepic})`
            }

            // Show animation container
            document.getElementById("animation-container").style.display = "flex"
        }
    })

    .finally(() => {
        // Hide after animation is done
        setTimeout(function() {
            document.getElementById("animation-container").style.display = "none"
        }, 3900)
    })
}

// Does a move
function doMove(td_element) {
    // Get the slot that user is trying to do a move on
    var id = td_element.id;

    // Do post request to server to see if move is allowed
    var url = "/match_do_move"
    fetch(url, {
        method: "POST",
        body: JSON.stringify({
            "slot_id": id,
            "room_name": room_name
        }),
        headers : {
            "X-CSRFToken" : csrfmiddlewaretoken
        },
        credentials: "same-origin"
    })

    .then(response => response.json())

    .then(response => {
        // If its the users turn
        if (response.allowed == 1) {
            if (response.turn == 1) {
                if (response.available == 1) {
                    // Send websocket message that you did move
                    matchWebSocket.send(JSON.stringify({
                        "message": "move",
                        "user_id": response.user_id,
                        "slot": response.slot
                    }))
                } else {
                    showError("This slot is taken.")
                }
            } else {
                showError("It is not your turn yet.");
            }
        } else {
            matchWebSocket.close()
            window.location.href = "/main"
        }
    })

    .finally(() => {
        // Update match info
        getMatchInfo()
    })

    .catch(error => {
        showError("Something went wrong.")
        console.error(error)
    })
}

// Add event listeners to each slot for a click
const td_tags = document.querySelectorAll("td")
td_tags.forEach((td) => {
    td.addEventListener("click", function tdEvent() {
        doMove(td)
    })
})

// Get match info, like which slots are taken, whos turn it is, if the timer ran out etc.
function getMatchInfo() {
    var url = "/get_match_info/" + room_name + "/" + currentRound + "/"

    fetch(url,{
        method: "GET",
        headers : {
            "X-CSRFToken" : csrfmiddlewaretoken
        },
        credentials: "same-origin"
    })

    .then(response => response.json())

    .then(response => {
        // If user is allowed in the match
        if (response.allowed == 1) {
            // Fill out slots on tictactoe board according to the backend
            var slotsJSON = response.slots;
            slotsJSON = JSON.parse(slotsJSON)
            for (var key in slotsJSON) {
                if (slotsJSON[key] == "x") {
                    // Replace element to remove event listener
                    var old_element = document.getElementById(key);
                    var new_element = old_element.cloneNode(true);
                    old_element.parentNode.replaceChild(new_element, old_element);

                    document.getElementById(key).style.backgroundImage = "url('static/img/icons/x-match.svg')"
                    document.getElementById(key).style.cursor = "not-allowed"
                } else if (slotsJSON[key] == "o") {
                    // Replace element to remove event listener
                    var old_element = document.getElementById(key);
                    var new_element = old_element.cloneNode(true);
                    old_element.parentNode.replaceChild(new_element, old_element);

                    document.getElementById(key).style.backgroundImage = "url('static/img/icons/o-match.svg')"
                    document.getElementById(key).style.cursor = "not-allowed"
                } else {
                    document.getElementById(key).style.backgroundImage = ""
                }
            }

            // Get x and o info
            var xNickname = response.x_nickname
            var oNickname = response.o_nickname
            var xProfilePic = response.x_profilepic
            var oProfilePic = response.o_profilepic
            var xUserId = response.x_uid
            var oUserId = response.o_uid

            // Get turn elements
            var turnIcon = document.getElementById("turn-icon")
            var turnProfilePic = document.getElementById("turn-profilepic")
            var turnNickname = document.getElementById("turn-nickname")

            // Check whos turn it is
            if (response.turn == "x") {
                turnNickname.innerHTML = xNickname;
                turnProfilePic.style.backgroundImage = `url(static/img/profile_pictures/${xProfilePic})`;
                turnIcon.src = "static/img/icons/x-match.svg";
                turnProfilePicUid = xUserId
            } else if (response.turn == "o") {
                turnNickname.innerHTML = oNickname;
                turnProfilePic.style.backgroundImage = `url(static/img/profile_pictures/${oProfilePic})`;
                turnIcon.src = "static/img/icons/o-match.svg";
                turnProfilePicUid = oUserId
            }

            // Start timer
            startTimer(response.seconds)

            // Get round
            var roundSpan = document.getElementById("round-count")
            roundSpan.innerHTML = response.round
            setTimeout(function() {
                currentRound = response.round
            }, 200)
        } else {
            matchWebSocket.close()
            window.location.href = "/main"
        }
    })

    .catch(error => {
        console.log(error)
    })
}

var timerInterval = "";
var turnProfilePicUid = "";

document.getElementById("turn-profilepic").addEventListener("click", function() {
    displayProfile(turnProfilePicUid)
})

// Start a timer that counts down from 60
function startTimer(start_seconds) {
    clearInterval(timerInterval)
    var timerElement = document.getElementById("timer")
    timerElement.innerHTML = start_seconds
    if (start_seconds < 0) {
        timerElement.innerHTML = 0;
    }

    timerInterval = setInterval(function() {
        start_seconds = start_seconds - 1
        if (start_seconds > 0) {
            timerElement.innerHTML = start_seconds
        } else {
            timerElement.innerHTML = 0;
            var randomDelay = Math.floor(Math.random() * 1500);
            setTimeout(function() {
                getMatchInfo()
            }, randomDelay)
        }
    }, 1000)
}

// Event listener for leave match button
document.getElementById("leave").addEventListener("click", function() {
    ajaxGet("/leave_match_modal", "dark-container", function() {
        document.getElementById("leave-confirm").addEventListener("click", function() {
            var url = "/leave_match"

            fetch(url, {
                method: "POST",
                body: JSON.stringify({
                    "room_name": room_name
                }),
                headers : {
                    "X-CSRFToken" : csrfmiddlewaretoken
                },
                credentials: "same-origin"
            })

            .then(response => response.json())

            .then(response => {
                if (response.ok == 1) {
                    // Send message that you left the match
                    matchWebSocket.send(JSON.stringify({
                        "message": "left_match",
                        "user_id": user_id
                    }))
                }
            })

            .finally(() => {
                matchWebSocket.close()
                window.location = "/main";
            })
        })
    })
})

// Update users online state in match
function matchPing() {
    var url = `/match_ping/${room_name}/`

    fetch(url, {
        method: "GET",
        headers : {
            "X-CSRFToken" : csrfmiddlewaretoken
        },
        credentials: "same-origin"
    })

    .then(response => response.json())

    .then(response => {
        if (response.allowed == 0) {
            matchWebSocket.close()
            window.location = "/main"
        }

        if (response.opponent_offline == 1) {
            // opponent is offline, get info
            getMatchInfo()
        }
    })

    .catch(error => {
        console.error(error)
    })
}

// Long polling for updateing match ping
const matchPingInterval = setInterval(function() {
    matchPing()
}, 7000)

// Do animation sequence, ping and get match info on load of dom content
document.addEventListener("DOMContentLoaded", function() {
    animationSequence()
    getMatchInfo()
    matchPing()
})