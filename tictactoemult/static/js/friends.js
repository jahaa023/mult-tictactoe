// JavaScript file for friends page

// Varible for keeping track of which tab the user is on. This is to prevent unnessesary get requests for the tab youre already on
var currentTab = "";
var friendListInterval = "";
var pendingFriendsInterval = "";
// Function that loads in your friends page
function loadYourFriends() {
    if (currentTab != "your_friends") {
        ajaxGet("/your_friends", "friends-page-container", function() {
            currentTab = "your_friends";
            hideUniversalDropdown();
            clearInterval(pendingFriendsInterval);

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
            clearInterval(pendingFriendsInterval);

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

// Function that loads in pending invites page
function loadPendingInvites() {
    if (currentTab != "pending_invites") {
        ajaxGet("/pending_invites", "friends-page-container", function() {
            currentTab = "pending_invites";
            hideUniversalDropdown();
            clearInterval(friendListInterval);

            // Update pending friends every 5 seconds to update requests coming in
            pendingFriendsInterval = setInterval(function() {
                ajaxGet("/pending_invites", "friends-page-container")
            }, 5000)
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
            case "alreadyreceived":
                showConfirm("You have already received a friend request from this user.");
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

// Function that cancels or declines a friend request
function cancelDeclineFriendRequest(row_id, cancel_decline) {
    var url = "/cancel_decline_friend_request"

    fetch(url, {
        method : "POST",
        body : JSON.stringify({
            row_id : row_id
        }),
        credentials : "same-origin",
        headers : {
            "X-CSRFToken" : csrfmiddlewaretoken
        }
    })

    .then(response => response.json())

    .then(response => {
        switch(response.error) {
            case "error":
                showConfirm("Something went wrong.");
                break;
        }

        if (response.ok == 1) {
            currentTab = ""
            loadPendingInvites();
            friendsListNotif();
            showConfirm("Friend request " + cancel_decline + ".");
        }
    })

    .catch(error => {
        showConfirm("Something went wrong")
        console.error(error)
    })
}

// Function that accepts a friend request
function acceptFriendRequest(row_id) {
    var url = "/accept_friend_request";

    fetch(url, {
        method : "POST",
        body : JSON.stringify({
            row_id : row_id
        }),
        credentials : "same-origin",
        headers : {
            "X-CSRFToken" : csrfmiddlewaretoken
        }
    })

    .then(response => response.json())

    .then(response => {
        switch(response.error) {
            case "error":
                showConfirm("Something went wrong.");
                break;
        }

        if (response.ok == 1) {
            currentTab = ""
            loadPendingInvites();
            friendsListNotif();
            showConfirm("Friend request accepted. You can see your new friend in the 'Your friends' tab.")
        }
    })

    .catch(error => {
        showConfirm("Something went wrong.")
        console.error(error)
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

document.getElementById("pending_invites").addEventListener("click", function() {
    loadPendingInvites();
    friendsListNotif();
})

document.getElementById("pending_invites_mobile").addEventListener("click", function() {
    loadPendingInvites();
    friendsListNotif();
})

// Ping interval
setInterval(function() {
    ping();
}, 5000)

// When document loads in, ping
document.addEventListener("DOMContentLoaded", function() {
    ping();
    friendsListNotif();
})

var friendListBubbles = document.querySelectorAll(".universal-dropdown-notif")

// Check for pending invites and send to notif bubble
const friendsNotifInterval = setInterval(function() {
    friendsListNotif();
}, 5000)

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

// Renders modal for managing friend for things like removing friends
function manageFriend(user_id) {
    var url = "/manage_friend"

    fetch(url, {
        method : "POST",
        credentials : "same-origin",
        body : JSON.stringify({
            user_id : user_id
        }),
        headers : {
            "X-CSRFToken" : csrfmiddlewaretoken
        }
    })

    .then(response => response.text())

    .then(response => {
        switch(response) {
            case "error":
                showConfirm("Something went wrong.")
                break;
        }

        document.getElementById("dark-container").innerHTML = response;
        $('#dark-container').fadeIn(300)
    })

    .then(() => {
        // Event listeners for modal
        document.getElementById("manage-friend-close").addEventListener("click", function() {
            hideDarkContainer()
        })

        document.getElementById("remove-friend").addEventListener("click", function() {
            document.getElementById("manage-friend-container").style.display = "none"
            document.getElementById("manage-friend-warning").style.display = "inline"
        })

        document.getElementById("manage-friend-cancel").addEventListener("click", function() {
            document.getElementById("manage-friend-container").style.display = "inline"
            document.getElementById("manage-friend-warning").style.display = "none"
        })

        // When remove friend comfirm button is pressed, do post request
        document.getElementById("confirm-remove-friend").addEventListener("click", function() {
            // Get user id of friend from name
            var user_id = this.name;
            var url = "/remove_friend";

            // Do post request
            fetch(url, {
                method : "POST",
                credentials : "same-origin",
                body : JSON.stringify({
                    user_id : user_id
                }),
                headers : {
                    "X-CSRFToken" : csrfmiddlewaretoken
                }
            })

            .then(response => response.json())

            .then(response => {
                switch(response.error) {
                    case "error":
                        showConfirm("Something went wrong. Please try again later.");
                        break;
                    case "not_friend":
                        showConfirm("This person is not in your friend list.");
                        break;
                }

                if (response.ok == 1) {
                    showConfirm("Friend removed.");
                    hideDarkContainer();
                    currentTab = "";
                    ajaxGet("/your_friends", "friends-page-container")
                }
            })

            .catch(error => {
                console.error(error);
                showConfirm("Something went wrong. Please try again later.");
            })
        })
    })

    .catch(error => {
        console.error(error)
        showConfirm("Something went wrong.")
    })
}