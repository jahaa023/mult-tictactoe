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

// When email form is submitted, do ajax request
$('#email-form').on("submit", function (e){
    e.preventDefault();
    $("#next-button").prop("disabled", true);
    var formData = new FormData(this);

    $.ajax({
        url: '/account_recovery_email',
        type: 'POST',
        data: formData,
        success: function (response) {
            switch(response) {
                case "error":
                    showError("Something went wrong. Make sure inputs are filled.")
                    break
                case "not_registered":
                    showError("This e-mail is not registered to an account.")
                    break
                case "ok":
                    window.location.href = "/account_recovery_inputcode";
            }
        },
        error: function() {
            showError("Something went wrong. Try again later.")
        },
        complete: function() {
            $("#next-button").prop("disabled", false);
        },
        cache: false,
        contentType: false,
        processData: false,
    });
})

// When code form is submitted, do ajax request
$('#code-form').on("submit", function (e){
    e.preventDefault();
    $("#next-button").prop("disabled", true);
    var formData = new FormData(this);

    $.ajax({
        url: '/account_recovery_code',
        type: 'POST',
        data: formData,
        success: function (response) {
            switch(response) {
                case "error":
                    showError("Something went wrong. Make sure input only contains numbers.")
                    break
                case "expired_notfound":
                    showError("The code you typed in is invalid or expired. Please try again.")
                    break
                case "ok":
                    window.location.href = "/account_recovery_final";
            }
        },
        error: function() {
            showError("Something went wrong. Try again later.")
        },
        complete: function() {
            $("#next-button").prop("disabled", false);
        },
        cache: false,
        contentType: false,
        processData: false,
    });
})

// When reset password button is pressed, show form for resetting password
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

// When reset password form is submitted, do ajax request
$('#reset-password-form').on("submit", function (e){
    e.preventDefault();
    $("#save-password-button").prop("disabled", true);
    var formData = new FormData(this);

    $.ajax({
        url: '/reset_password',
        type: 'POST',
        data: formData,
        success: function (response) {
            switch(response) {
                case "error":
                    showError("Something went wrong. Make sure inputs are filled out.")
                    break
                case "same":
                    showError("New password cannot be the same as the old password.")
                    break
                case "no_match":
                    showError("New password and confirm new password does not match.")
                    break
                case "ok":
                    document.getElementById("reset-password-form").innerHTML = "Password successfully saved!"
            }
        },
        error: function() {
            showError("Something went wrong. Try again later.")
        },
        complete: function() {
            $("#save-password-button").prop("disabled", false);
        },
        cache: false,
        contentType: false,
        processData: false,
    });
})