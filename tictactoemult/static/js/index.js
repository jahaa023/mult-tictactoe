// Function that shows an error wehn something goes wrong during log in
function showError(error) {
    var errorElement = document.getElementById("login-form-error-notif")
    errorElement.innerHTML = error;
    errorElement.style.display = "block";
}

// When login form is submitted, do a fetch api post request
document.getElementById("login-form").addEventListener("submit", function(e) {
    e.preventDefault();
    var formData = new FormData(this);

    var url = "/login"
    fetch(url, {
        method : "POST",
        body : formData,
        credentials : "same-origin"
    })

    .then(response => response.json())

    .then(response => {
        switch(response.error) {
            case "error":
                showError("Something went wrong. Make sure inputs are filled.")
                break
            case "wrong":
                showError("Username or password incorrect!")
                break
        }

        if (response.redirect == 1) {
            window.location.href = "/main"
        }
    })

    .catch(error => {
        showError("Something went wrong. Please try again later.")
        console.error(error)
    })
});

// Changes type of password input when eye icon is pressed
document.getElementById("password-visibility-button").addEventListener("click", function() {
    changeVisibility('id_password', 'password-visibility-button')
})