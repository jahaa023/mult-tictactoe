// JavaScript file for function for every page

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

// Does a GET request, and loads contents into element
function ajaxGet(staticpath, location, onload = function(){}) {
    $.get(staticpath, function(data){
        var insertContainer = document.getElementById(location)
        insertContainer.innerHTML = data
    })
    .done(function() {
        onload();
        if (location == "dark-container") {
            $('#dark-container').fadeIn(300)
        }
    })
    .fail(function() {
        showConfirm("Something went wrong")
    });
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