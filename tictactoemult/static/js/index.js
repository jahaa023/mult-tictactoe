// Function that shows an error wehn something goes wrong during log in
function showError(error) {
    var errorElement = document.getElementById("login-form-error-notif")
    errorElement.innerHTML = error;
    errorElement.style.display = "block";
}

// When login form is submitted, do a AJAX post request
$('#login-form').on("submit", function (e){
    e.preventDefault();
    var formData = new FormData(this);

    $.ajax({
        url: '/login',
        type: 'POST',
        data: formData,
        success: function (response) {
            switch(response) {
                case "error":
                    showError("Something went wrong. Make sure inputs are filled.")
                    break
                case "wrong":
                    showError("Username or password incorrect!")
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

document.getElementById("password-visibility-button").addEventListener("click", function() {
    changeVisibility('id_password', 'password-visibility-button')
})