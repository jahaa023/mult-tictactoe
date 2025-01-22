// JavaScript file for friends page

// Varible for keeping track of which tab the user is on. This is to prevent unnessesary get requests for the tab youre already on
var currentTab = "";
var friendListInterval = "";
// Function that loads in your friends page
function loadYourFriends() {
    if (currentTab != "your_friends") {
        ajaxGet("/your_friends", "friends-page-container", function() {
            currentTab = "your_friends";

            // Update friends list every 10 seconds to update online and offline friends status
            friendListInterval = setInterval(function() {
                ajaxGet("/your_friends", "friends-page-container")
            }, 10000)
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