// JavaScript file for friends page

// Varible for keeping track of which tab the user is on. This is to prevent unnessesary get requests for the tab youre already on
var currentTab = "";
var friendListInterval = "";
// Function that loads in your friends page
function loadYourFriends() {
    if (currentTab != "your_friends") {
        ajaxGet("/your_friends", "friends-page-container", function() {
            currentTab = "your_friends";
            hideUniversalDropdown();

            // Update friends list every 10 seconds to update online and offline friends status
            friendListInterval = setInterval(function() {
                ajaxGet("/your_friends", "friends-page-container")
            }, 10000)
        })
    }
}

// Get csrftoken from cookie
const csrfmiddlewaretoken = document.cookie.split(';')
    .find(cookie => cookie.trim().startsWith('csrftoken='))
    ?.split('=')[1];

// Function that loads in the add friends page
function loadAddFriends() {
    if (currentTab != "add_friends") {
        ajaxGet("/add_friends", "friends-page-container", function() {
            currentTab = "add_friends";
            hideUniversalDropdown();
            clearInterval(friendListInterval);

            // Event listener for input for searching for friends
            document.getElementById("add-friends-input").addEventListener("keyup", function() {
                var query = this.value;

                // Do post request to search url and return the response
                $.ajax({
                    url: '/add_friends_result',
                    type: 'POST',
                    headers: {"X-CSRFToken": csrfmiddlewaretoken},
                    data: JSON.stringify({
                        query:query
                    }),
                    success: function (response) {
                        document.getElementById("add-friends-result").innerHTML = response
                    },
                    error: function() {
                        document.getElementById("add-friends-result").innerHTML = "Something went wrong."
                    },
                    cache: false,
                    contentType: "application/json; charset=utf-8",
                    processData: false,
                });
            })
        })
    }
}

loadYourFriends();

// Event listeners for dropdown and navbar
document.getElementById("your_friends").addEventListener("click", function(){
    loadYourFriends();
})

document.getElementById("your_friends_mobile").addEventListener("click", function(){
    loadYourFriends();
})

document.getElementById("add_friends").addEventListener("click", function() {
    loadAddFriends();
})

document.getElementById("add_friends_mobile").addEventListener("click", function() {
    loadAddFriends();
})