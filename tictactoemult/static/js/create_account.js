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
                case "ok":
                    window.location.href = "/main";
            }
        },
        error: function() {
            showError("Something went wrong. Try again later.")
        },
        cache: false,
        contentType: false,
        processData: false,
    });
})