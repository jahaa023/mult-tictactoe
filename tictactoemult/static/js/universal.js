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