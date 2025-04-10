// JavaScript for leaderboard page

// Interval that pings and checks match invites
setInterval(function() {
    ping();
    checkMatchInvites();
}, 5000)

// When document loads in, ping, load leaderboard and check match invites
document.addEventListener("DOMContentLoaded", function() {
    ping();
    checkMatchInvites();
    loadLeaderboard();
})

// Event listener for back button
document.getElementById("back-button").addEventListener("click", function() {
    window.location.href = "/main"
})

// Event listener for sort by dropdown
document.getElementById("sortby").addEventListener("change", function() {
})

// Loads in the leaderboard 
function loadLeaderboard() {
    var url = "/load_leaderboard"
    var tableContent = document.getElementById("table-content")

    fetch(url, {
        method: "GET",
        credentials: "same-origin"
    })

    .then(response => response.text())

    .then(response => {
        tableContent.innerHTML = response
    })

    .catch(error => {
        console.error(error)
        tableContent.innerHTML = "<tr><td colspan='5'>There was a problem loading the leaderboard.</td></tr>"
    })
}