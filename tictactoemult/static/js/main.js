// JavaScript file for the main page

// jQuery animations for play buttons

$('#header-play-button-1').mouseenter(function() {
    $('#header-play-button-1').stop()
    $('#header-play-button-1').animate({
        width: '500px'
    });
})

$('#header-play-button-1').mouseleave(function() {
    $('#header-play-button-1').stop()
    $('#header-play-button-1').animate({
        width: '400px'
    });
})

$('#header-play-button-2').mouseenter(function() {
    $('#header-play-button-2').stop()
    $('#header-play-button-2').animate({
        width:'500px'
    });
})

$('#header-play-button-2').mouseleave(function() {
    $('#header-play-button-2').stop()
    $('#header-play-button-2').animate({
        width:'400px'
    });
})

// Event listeners
document.getElementById("leaderboard-button").addEventListener("click", function(){
    window.location = "/leaderboard"
})

document.getElementById("settings-button").addEventListener("click", function(){
    window.location = "/settings"
})

document.getElementById("friends-button").addEventListener("click", function(){
    window.location = "/friends"
})

document.getElementById("about-button").addEventListener("click", function(){
    window.location = "/about"
})

document.getElementById("dropdown-button").addEventListener("click", function() {
    document.getElementById("mobile-dropdown-background").style.display = "inline"
    $('#mobile-dropdown-container').animate({
        width:'300px'
    });
})

document.getElementById("dropdown-button-exit").addEventListener("click", function() {
    $('#mobile-dropdown-container').animate({
        width:'0px'
    }, 200);
    $('#mobile-dropdown-background').delay(200).fadeOut(200)
})

document.getElementById("header-play-button-1").addEventListener("click", function(){
    window.location.href = "/matchmaking?m=r";
})

// Function that loads in list of online friends
function loadOnlineFriends() {
    var url = "/main_online_friends"

    fetch(url, {
        method : "GET",
        credentials : "same-origin"
    })

    .then(response => response.text())

    .then(html => {
        document.getElementById("online-friends-container").innerHTML = html
    })
}

// Get csrftoken from cookie
const csrfmiddlewaretoken = document.cookie.split(';')
    .find(cookie => cookie.trim().startsWith('csrftoken='))
    ?.split('=')[1];

var friendListBubbles = document.querySelectorAll(".universal-dropdown-notif")

// Function that checks for pending friend invites and returns an amount of them
function friendsListNotif() {
    var url = "/pending_friends_notif"

    fetch(url, {
        method : "GET",
        credentials : "same-origin",
        headers : {
            "X-CSRFToken" : csrfmiddlewaretoken
        }
    })

    .then(response => response.json())

    .then(response => {
        if (response.amount > 0) {
            friendListBubbles.forEach(element => {
                var span = element.querySelector("span");
                span.innerHTML = response.amount;
                element.style.display = "flex";
            })
        } else {
            friendListBubbles.forEach(element => {
                element.style.display = "none";
            })
        }
    })

    .catch(error => {
        console.error(error)
        friendListBubbles.forEach(element => {
            element.style.display = "none";
        })
    })
}

// Interval that pings and loads list of online friends and number of pending invites
setInterval(function() {
    ping();
    loadOnlineFriends();
    friendsListNotif();
}, 5000)

// When document loads in, ping and show online friends
document.addEventListener("DOMContentLoaded", function() {
    ping();
    loadOnlineFriends();
    friendsListNotif()
})