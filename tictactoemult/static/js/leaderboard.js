// JavaScript for leaderboard page

// Get csrftoken from cookie
const csrfmiddlewaretoken = document.cookie.split(';')
    .find(cookie => cookie.trim().startsWith('csrftoken='))
    ?.split('=')[1];

// Define order by and query vars
var order_by = "wins"
var query = ""

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
document.getElementById("sortby").addEventListener("change", function(e) {
    order_by = e.target.value
    loadLeaderboard()
})

// Event listener for search bar
document.getElementById("search-input").addEventListener("keyup", function(e) {
    query = e.target.value
    loadLeaderboard()
})

// Loads in the leaderboard 
function loadLeaderboard() {
    var url = "/load_leaderboard"
    var tableContent = document.getElementById("table-content")

    fetch(url, {
        method: "POST",
        credentials: "same-origin",
        body: JSON.stringify({
            query: query,
            order_by: order_by
        }),
        headers : {
            "X-CSRFToken" : csrfmiddlewaretoken
        },
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