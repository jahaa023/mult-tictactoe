// JavaScript file for account recovery page

document.getElementById("cancel-button").addEventListener("click", function() {
    window.location.href = "/";
})

// Function that shows an error when something goes wrong during account recovery
function showError(error) {
    var errorElement = document.getElementById("error-warning")
    errorElement.innerHTML = error;
    errorElement.style.display = "block";
}

// Function that hides error
function hideError() {
    var errorElement = document.getElementById("error-warning")
    errorElement.innerHTML = "";
    errorElement.style.display = "none";
}

// When email form is submitted, do fetch api request
if (document.getElementById("email-form")) {
    document.getElementById("email-form").addEventListener("submit", function(e) {
        e.preventDefault();
        $("#next-button").prop("disabled", true);
        var formData = new FormData(this);

        var url = "/account_recovery_email"

        fetch(url, {
            method : "POST",
            body : formData
        })

        .then(response => response.json())

        .then(response => {
            switch (response.error) {
                case "error":
                    showError("Something went wrong. Make sure inputs are filled.");
                    break;
                case "not_registered":
                    showError("This e-mail is not registered to an account.");
                    break;
            }

            if (response.redirect == 1) {
                window.location.href = "/account_recovery_inputcode";
            }
        })

        .catch(error => {
            showError("Something went wrong. Try again later.")
            console.error(error)
        })

        .finally(() => {
            $("#next-button").prop("disabled", false);
        })
    })
}

// When code form is submitted, do fetch api request
if (document.getElementById("code-form")) {
    document.getElementById("code-form").addEventListener("submit", function(e) {
        e.preventDefault();
        $("#next-button").prop("disabled", true);
        var formData = new FormData(this);

        var url = "/account_recovery_code"

        fetch(url, {
            method : "POST",
            body : formData
        })

        .then(response => response.json())

        .then(response => {
            switch (response.error) {
                case "error":
                    showError("Something went wrong. Make sure input only contains numbers.")
                    break
                case "expired_notfound":
                    showError("The code you typed in is invalid or expired. Please try again.")
                    break
            }

            if (response.redirect == 1) {
                window.location.href = "/account_recovery_final";
            }
        })

        .catch(error => {
            showError("Something went wrong. Try again later.")
            console.error(error)
        })

        .finally(() => {
            $("#next-button").prop("disabled", false);
        })
    })
}

// When reset password button is pressed, show form for resetting password
if (document.getElementById("reset-password-button")) {
    document.getElementById("reset-password-button").addEventListener("click", function() {
        passwordForm = document.getElementById("reset-password-form")
        passwordButtonIcon = document.getElementById("reset-password-button-icon")

        if (window.getComputedStyle(passwordForm).display === 'none'){
            passwordForm.style.display = 'block';
            passwordButtonIcon.style.transform = "rotate(180deg)"
        } else {
            passwordForm.style.display = "none";
            passwordButtonIcon.style.transform = "rotate(0deg)"
        }
    })
}

// When reset password form is submitted, do fetch api request
if (document.getElementById("reset-password-form")) {
    document.getElementById("reset-password-form").addEventListener("submit", function(e) {
        e.preventDefault();
        $("#save-password-button").prop("disabled", true);
        var formData = new FormData(this);

        var url = "/reset_password"

        fetch(url, {
            method : "POST",
            body : formData,
            credentials : "same-origin"
        })

        .then(response => response.json())

        .then(response => {
            switch(response.error) {
                case "error":
                    showError("Something went wrong. Make sure inputs are filled out.")
                    break
                case "same":
                    showError("New password cannot be the same as the old password.")
                    break
                case "no_match":
                    showError("New password and confirm new password does not match.")
                    break
            }

            if (response.ok == 1) {
                document.getElementById("reset-password-form").innerHTML = "Password successfully saved!";
                hideError();
            }
        })

        .catch(error => {
            showError("Something went wrong. Try again later.")
            console.error(error)
        })

        .finally(() => {
            $("#save-password-button").prop("disabled", false);
        })
    })
}

// Event listeners for password visibility buttons
if (document.getElementById("password-visibility-button-new")) {
    document.getElementById("password-visibility-button-new").addEventListener("click", function() {
        changeVisibility('id_new_password', 'password-visibility-button-new')
    })

    document.getElementById("password-visibility-button-confirm").addEventListener("click", function() {
        changeVisibility('id_new_password_confirm', 'password-visibility-button-confirm')
    })
}