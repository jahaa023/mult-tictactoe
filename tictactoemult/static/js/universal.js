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