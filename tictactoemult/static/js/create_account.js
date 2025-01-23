// JavaScript file for create account page

// Function that shows an error wehn something goes wrong during log in
function showError(error) {
    var errorElement = document.getElementById("create-account-form-error-notif")
    errorElement.innerHTML = error;
    errorElement.style.display = "block";
}

// Get csrftoken from cookie
const csrfToken = document.cookie.split(';')
    .find(cookie => cookie.trim().startsWith('csrftoken='))
    ?.split('=')[1];


// When login form is submitted, do a fetch api post request
document.getElementById("create-account-form").addEventListener("submit", function(e){
    e.preventDefault();
    var formData = new FormData(this);

    var url = "/create_account_form_handler";

    fetch(url, {
        method : 'POST',
        body : formData,
        credentials: "same-origin"
    })

    // Convert response to json
    .then(response => response.json())

    // Handle response data
    .then(response => {
        switch(response.error) {
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
        }

        if (response.redirect == 1) {
            window.location.href = "/main"
        }
    })

    .catch(error => {
        showError("Something went wrong. Please try again later")
        console.error(error)
    })
})

// Post to username validator on keyup of username input
document.getElementById("id_username").addEventListener("keyup", function(){
    // Changes opacity of validator
    $(".username-validator-container").children().css({"opacity" : "1"})
    $("li").css({"opacity" : "1"})

    var username = document.getElementById("id_username").value;

    var url = "/username_validate";

    fetch(url, {
        method : 'POST',
        headers : {
            'Content-Type' : 'application/json',
            'X-CSRFToken' : csrfToken,
        },
        body : JSON.stringify({
            username : username
        }),
        credentials: "same-origin"
    })

    // Convert response to json
    .then(response => response.json())

    // Handle response data
    .then(response => {
        // If the username is not inbetween 5 to 30 letters
        if (response.between_letters == 1) {
            document.getElementById("between_letters").style.color = "red";
        } else {
            document.getElementById("between_letters").style.color = "green";
        }

        // If username contains non english chars
        if (response.ascii == 1) {
            document.getElementById("ascii").style.color = "red";
        } else {
            document.getElementById("ascii").style.color = "green";
        }

        // If username is taken
        if (response.taken == 1) {
            document.getElementById("taken").style.color = "red";
        } else {
            document.getElementById("taken").style.color = "green";
        }

        // If username is only numbers
        if (response.numeric == 1) {
            document.getElementById("numeric").style.color = "red";
        } else {
            document.getElementById("numeric").style.color = "green";
        }
    })

    .catch(error => {
        // If something went wrong
        document.getElementById("username-validator-container").innerHTML = "Something went wrong while validating username."
        console.error(error)
    })
})

// Event listener for password visibility button
document.getElementById("password-visibility-button").addEventListener("click", function() {
    changeVisibility('id_password', 'password-visibility-button')
})