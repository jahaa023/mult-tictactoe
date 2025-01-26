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

// Ping interval
setInterval(function() {
    ping();
}, 5000)

// When document loads in, ping
document.addEventListener("DOMContentLoaded", function() {
    ping();
})