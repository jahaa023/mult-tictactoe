// JavaScript file for function for every page

// Get color preference and change favicon
function changeFavicon() {
    var link = document.querySelector("link[rel~='icon']");
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        // dark mode
        link.href = '/static/img/favicon-darkmode.ico';
    } else {
        // Light mode
        link.href = '/static/img/favicon.ico';
    }
}

$( document ).ready(function() {
    changeFavicon();
});

// Get csrftoken from cookie
const universalCsrfToken = document.cookie.split(';')
    .find(cookie => cookie.trim().startsWith('csrftoken='))
    ?.split('=')[1];

//password visibility button
function changeVisibility(inputID, buttonID){
    var passwordInput = document.getElementById(inputID)
    var visibilityButton = document.getElementById(buttonID)

    if (passwordInput.type === "password") {
        passwordInput.type = "text"
        visibilityButton.style.backgroundImage = "url(/static/img/icons/eye-password-show.svg)"
        visibilityButton.setAttribute('title', 'Hide password')
    }
    else {
        passwordInput.type = "password"
        visibilityButton.style.backgroundImage = "url(/static/img/icons/eye-password-hide.svg)"
        visibilityButton.setAttribute('title', 'Show password')
    }
}

// Shows a black bar at top of screen with a message and fades it out
function showConfirm(message, duration = 1000) {
    $("#confirmContainer").stop( true, true ).fadeOut();
    var confirmContainer = document.getElementById("confirmContainer")
    confirmContainer.style.display = "inline"
    confirmContainer.innerHTML = message
    $('#confirmContainer').delay(duration).fadeOut(1000)
}

// Does a GET request, and loads contents into element. Is called "ajax"Get because it used jquery in the past. It now uses fetch api
function ajaxGet(staticpath, location, onload = function(){}) {
    fetch(staticpath, {
        method : "GET",
        credentials : "same-origin"
    })

    .then(response => response.text())

    .then(response => {
        var insertContainer = document.getElementById(location)
        insertContainer.innerHTML = response
    })

    .then(() => {
        onload();
        if (location == "dark-container") {
            $('#dark-container').fadeIn(300)
        }
    })

    .catch(error => {
        showConfirm("Something went wrong")
        console.error(error)
    })
}

// Hides dark container div
function hideDarkContainer() {
    var darkContainer = document.getElementById("dark-container");
    darkContainer.innerHTML = "";
    $('#dark-container').fadeOut(300)
}

// Shows a modal with a profile based on user id
function displayProfile(user_id) {
    ajaxGet("/display_profile/" + user_id + "/", "dark-container")
}

// Event listeners for dropdowns if they exist on page
if ($('#universal-dropdown').length > 0) {
    document.getElementById("universal-dropdown-mobile-header-button").addEventListener("click", function() {
        $('#universal-dropdown-background').fadeIn(300)
        document.getElementById("universal-dropdown").style.display = "inline";
        $('#universal-dropdown').animate({
            width:'290px',
        }, 300);
    })

    // Hides dropdown
    function hideUniversalDropdown() {
        $('#universal-dropdown-background').fadeOut(300)
        $('#universal-dropdown').animate({
            width:'0px',
        }, 300);
        setTimeout(function(){
            document.getElementById("universal-dropdown").style.display = "none";
        }, 300)
    }

    document.getElementById("universal-dropdown-mobile-exit").addEventListener("click", function() {
        hideUniversalDropdown();
    })
}

// Request that tells server that user is online
function ping() {
    var url = "/ping";

    fetch(url, {
        method : "GET",
        credentials : "same-origin"
    })
}

// Check if you have any invites to a match
function checkMatchInvites() {
    var url = "/check_match_invites"
    fetch(url, {
        method: "GET",
        credentials: "same-origin"
    })

    .then(response => response.json())

    .then(response => {
        if (response.found == 1) {
            var profilepic = response.profilepic
            var nickname = response.nickname
            var row_id = response.row_id
            invitePopUp(row_id, nickname, profilepic)
        } else {
            hideInvitePopUp()
        }
    })
}

// Shows a popup for an invite
function invitePopUp(row_id, nickname, profilepic) {
    // Get relevant elements on page
    var inviteContainer = document.getElementById("friend-invite-popup")
    var inviteProfilePic = document.getElementById("friend-invite-profilepic")
    var inviteNickname = document.getElementById("friend-invite-nickname")
    var inviteAccept = document.getElementById("friend-invite-accept")
    var inviteDecline = document.getElementById("friend-invite-decline")

    // Change nickname and profile picture
    inviteNickname.innerHTML = nickname;
    inviteProfilePic.style.backgroundImage = `url(static/img/profile_pictures/${profilepic})`

    // Replace buttons to remove previous event listeners
    var newAccept = inviteAccept.cloneNode(true);
    inviteAccept.parentNode.replaceChild(newAccept, inviteAccept);
    var newDecline = inviteDecline.cloneNode(true);
    inviteDecline.parentNode.replaceChild(newDecline, inviteDecline);

    // Add event listeners
    newAccept.addEventListener("click", function() {
        acceptInvite(row_id)
    })
    newDecline.addEventListener("click", function() {
        declineInvite(row_id)
    })

    // Show container
    inviteContainer.style.display = "flex"
}

// Hides invite popup
function hideInvitePopUp() {
    // Get relevant elements on page
    var inviteContainer = document.getElementById("friend-invite-popup")
    var inviteProfilePic = document.getElementById("friend-invite-profilepic")
    var inviteNickname = document.getElementById("friend-invite-nickname")
    var inviteAccept = document.getElementById("friend-invite-accept")
    var inviteDecline = document.getElementById("friend-invite-decline")

    // reset nickname and profilepic
    inviteNickname.innerHTML = "";
    inviteProfilePic.style.backgroundImage = "";

    // Replace buttons to remove previous event listeners
    var newAccept = inviteAccept.cloneNode(true);
    inviteAccept.parentNode.replaceChild(newAccept, inviteAccept);
    var newDecline = inviteDecline.cloneNode(true);
    inviteDecline.parentNode.replaceChild(newDecline, inviteDecline);

    // hide container
    inviteContainer.style.display = "none"
}

// Accepts an invite
function acceptInvite(row_id) {
    var url = "/accept_invite"

    fetch(url, {
        method: "POST",
        body: JSON.stringify({
            "row_id": row_id
        }),
        credentials : "same-origin",
        headers : {
            "X-CSRFToken" : universalCsrfToken,
        }
    })

    .then(response => response.json())

    .then(response => {
        switch(response.error) {
            case "notfound":
                showConfirm("The invite was not found.")
                break;
            case "notallowed":
                showConfirm("The invite was not sent to you.")
                break;
        }
        if (response.ok == 1) {
            window.location = response.redirect
        }
    })

    .catch(error => {
        showConfirm("Something went wrong.")
        console.error(error)
    })
}

// Declines an invite
function declineInvite(row_id) {
    var url = "/decline_invite"

    fetch(url, {
        method: "POST",
        body: JSON.stringify({
            "row_id": row_id
        }),
        credentials : "same-origin",
        headers : {
            "X-CSRFToken" : universalCsrfToken,
        }
    })

    .then(response => response.json())

    .then(response => {
        if (response.ok == 1) {
            showConfirm("Invite declined.");
            hideInvitePopUp();
        }
    })

    .catch(error => {
        showConfirm("Something went wrong.")
        console.error(error)
    })
}