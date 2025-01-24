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

                var url = "/add_friends_result"

                fetch(url, {
                    method : "POST",
                    body : JSON.stringify({
                        query:query
                    }),
                    credentials : "same-origin",
                    headers : {
                        "X-CSRFToken" : csrfmiddlewaretoken
                    }
                })

                .then(response => response.text())

                .then(response => {
                    document.getElementById("add-friends-result").innerHTML = response
                })

                .catch(error => {
                    document.getElementById("add-friends-result").innerHTML = "Something went wrong."
                    console.error(error)
                })
            })
        })
    }
}

loadYourFriends();

// Sends a friend request to user_id in parameter
function sendFriendRequest(user_id) {
    var url = "/send_friend_request"

    fetch(url, {
        method : "POST",
        body : JSON.stringify({
            user_id:user_id
        }),
        credentials : "same-origin",
        headers : {
            "X-CSRFToken" : csrfmiddlewaretoken
        }
    })

    .then(response => response.json())

    .then(response => {
        switch(response.error) {
            case "already_friends":
                showConfirm("This user is already in your friends list.");
                break;
            case "yourself":
                showConfirm("This user is yourself");
                break;
            case "noexist":
                showConfirm("This user doesnt exist.");
                break;
            case "alreadysent":
                showConfirm("You have already sent this user a friend request.");
                break;
        }

        if (response.ok == 1) {
            // Get button that user pressed and disable it
            var alreadySentButton = document.getElementById(response.sentbutton);
            alreadySentButton.disabled = true;
            alreadySentButton.style.cursor = "not-allowed";
            alreadySentButton.title = "You have already sent this user a friend request.";
            showConfirm("Friend request sent!");
        }
    })

    .catch(error => {
        showConfirm("Something went wrong.");
        console.error(error);
    })
}

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