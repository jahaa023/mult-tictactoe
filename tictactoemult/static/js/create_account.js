// JavaScript file for create account page

// Function that shows an error wehn something goes wrong during log in
function showError(error) {
    var errorElement = document.getElementById("create-account-form-error-notif")
    errorElement.innerHTML = error;
    errorElement.style.display = "block";
}

// When login form is submitted, do a AJAX post request
$('#create-account-form').on("submit", function (e){
    e.preventDefault();
    var formData = new FormData(this);

    $.ajax({
        url: '/create_account_form_handler',
        type: 'POST',
        data: formData,
        success: function (response) {
            switch(response) {
                case "error":
                    showError("Something went wrong. Make sure inputs are filled.")
                    break
                case "ascii":
                    showError("Only English characters can be used in username.")
                    break
                case "taken":
                    showError("This username is taken.")
                    break
                case "email_taken":
                    showError("This email is already registered to an account.")
                    break
                case "numeric":
                    showError("The username only contains numbers.")
                    break
                case "ok":
                    window.location.href = "/main";
            }
        },
        error: function() {
            showError("Something went wrong. Try again later or try refreshing.")
        },
        cache: false,
        contentType: false,
        processData: false,
    });
})

// Validate username on keyup of username input
document.getElementById("id_username").addEventListener("keyup", function() {
    // Changes opacity of validator
    $(".username-validator-container").children().css({"opacity" : "1"})
    $("li").css({"opacity" : "1"})

    // Post username input content to /username_validate
    var username = document.getElementById("id_username").value;
    $.ajax({
        url: '/username_validate',
        type: 'POST',
        data : {'username' : username},
        success: function (response) {
            if ("between_letters" in response) {
                $('#between_letters').css('color', 'red');
            } else {
                $('#between_letters').css('color', 'green');
            }

            if ("ascii" in response) {
                $('#ascii').css('color', 'red');
            } else {
                $('#ascii').css('color', 'green');
            }

            if ("taken" in response) {
                $('#not_taken').css('color', 'red');
            } else {
                $('#not_taken').css('color', 'green');
            }

            if ("numeric" in response) {
                $('#numeric').css('color', 'red');
            } else {
                $('#numeric').css('color', 'green');
            }
        },
        error: function() {
            $(".username-validator-container").html("Something went wrong while checking username.")
        },
        cache: false,
        dataType: 'json'
    });
})