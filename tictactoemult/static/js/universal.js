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
    })
    .fail(function() {
        showConfirm("Something went wrong")
    });
}