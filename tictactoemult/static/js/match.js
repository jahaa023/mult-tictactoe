// JavaScript for match page

// Get room name in url
const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const room_name = urlParams.get('rn')

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
        
    }
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

// Do animation sequence on load of dom content
document.addEventListener("DOMContentLoaded", function() {
    animationSequence()
})