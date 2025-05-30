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
    
    // Update match
    getMatchInfo()
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

var slotsJSON = ""
var matchInfoRunning = 0 // Makes sure only one match info can be run at once
// Get match info, like which slots are taken, whos turn it is, if the timer ran out etc.
function getMatchInfo() {
    if (matchInfoRunning == 0) {
        var url = "/get_match_info/" + room_name + "/" + currentRound + "/"
        matchInfoRunning = 1

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
                slotsJSON = response.slots;
                slotsJSON = JSON.parse(slotsJSON)

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

                // Check if a status is available
                if (response.match_status != "none") {
                    var match_status_json = JSON.parse(response.match_status)
                    var message = match_status_json.message
                    showMessage(message)
                }

                // Get round
                var roundSpan = document.getElementById("round-count")
                roundSpan.innerHTML = response.round
                setTimeout(function() {
                    currentRound = response.round
                }, 200)

                // Check if anyone lost, won or left the match
                if (response.final_win != "none") {
                    var final_win_json = JSON.parse(response.final_win)
                    var reason = final_win_json.reason

                    // Figure out who opponent is
                    if (xUserId == user_id) {
                        var opponentUid = oUserId
                        var opponentProfilePic = oProfilePic
                        var opponentNickname = oNickname
                    } else if (oUserId == user_id) {
                        var opponentUid = xUserId
                        var opponentProfilePic = xProfilePic
                        var opponentNickname = xNickname
                    } else {
                        var opponentUid = "unknown"
                        var opponentProfilePic = "defaultprofile.jpg"
                        var opponentNickname = "Unknown"
                    }

                    if (final_win_json.uid == user_id) {
                        // You won
                        endAnimation("win", reason, opponentProfilePic, opponentNickname, opponentUid)
                    } else if (final_win_json.uid == "tie"){
                        // it was a tie
                        endAnimation("tie", reason, opponentProfilePic, opponentNickname, opponentUid)
                    } else {
                        // you lost
                        endAnimation("loss", reason, opponentProfilePic, opponentNickname, opponentUid)
                    }

                    // Cancel intervals, close websocket
                    clearInterval(matchPingInterval)
                    clearInterval(timerInterval)
                    matchWebSocket.close()
                }
            } else {
                matchWebSocket.close()
                window.location.href = "/main"
            }
        })

        .finally(() => {
            // First check if there is a new round. If there is, replace all elements
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
                    const old_element = document.getElementById(key);
                    const new_element = old_element.cloneNode(true);
                    old_element.parentNode.replaceChild(new_element, old_element);

                    new_element.style.cursor = "pointer"
                    new_element.style.backgroundImage = ""

                    new_element.addEventListener("click", function() {
                        doMove(new_element)
                    })
                }
            }
            matchInfoRunning = 0
        })

        .catch(error => {
            console.log(error)
        })
    }
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

var messageTimeout = ""
// Shows a message from the current match status
function showMessage(text) {
    clearTimeout(messageTimeout)
    if (text !== undefined) {
        var messageContainer = document.getElementById("message-container")
        messageContainer.innerHTML = text
        messageContainer.style.display = "block"
        messageTimeout = setTimeout(function() {
            messageContainer.style.display = "none"
        }, 2000)
    }
}

// Show the end animation for either winning or losing
function endAnimation(winloss, reason, profilepic, nickname, uid) {
    var endAnimationBackground = document.getElementById("endAnimationContainerBackground")
    var endAnimationContainer = document.getElementById("endAnimationContainer")
    var endAnimationH1 = document.getElementById("endAnimationH1")
    var endAnimationReasonP = document.getElementById("endAnimationReasonP")
    var endAnimationButton = document.getElementById("endAnimationButton")
    var endAnimationProfilePic = document.getElementById("endAnimationProfilepic")
    var endAnimationNickname = document.getElementById("endAnimationNickname")

    if (winloss == "win") {
        endAnimationContainer.style.backgroundColor = "var(--accept-green)"
        endAnimationH1.innerHTML = "You won!"
        endAnimationButton.classList.add("end-animation-button-win")
    } else if (winloss == "loss") {
        endAnimationContainer.style.backgroundColor = "var(--warning-red)"
        endAnimationH1.innerHTML = "You lost."
        endAnimationButton.classList.add("end-animation-button-loss")
    } else if (winloss == "tie") {
        endAnimationContainer.style.backgroundColor = "gray"
        endAnimationH1.innerHTML = "It was a tie."
        endAnimationButton.classList.add("end-animation-button-tie")
    }

    endAnimationReasonP.innerHTML = reason
    endAnimationBackground.style.display = "flex"
    endAnimationProfilePic.style.backgroundImage = `url(static/img/profile_pictures/${profilepic})`
    endAnimationNickname.innerHTML = nickname

    endAnimationProfilePic.addEventListener("click", function() {
        displayProfile(uid)
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