// JavaScript file for settings page

// Get csrftoken from cookie
const csrfToken = document.cookie.split(';')
    .find(cookie => cookie.trim().startsWith('csrftoken='))
    ?.split('=')[1];


// Varible for keeping track of which tab the user is on. This is to prevent unnessesary get requests for the tab youre already on
var currentTab = "";
// onload, default page is profile editing
function loadEditProfile() {
    if (currentTab != "edit_profile") {
        ajaxGet("/edit_profile", "settings-page-container", function() {
            currentTab = "edit_profile"
            // If user tries to change username
            document.getElementById("edit-profile-username").addEventListener("click", function() {
                showConfirm('You cannot change your username.')
            })

            // Charachter count for editing description
            var charcount = document.getElementById("description-charcount");
            charcount.innerHTML = ($("#id_description").val().length + "/300")

            document.getElementById("id_description").addEventListener("keyup", function() {
                var charcount = document.getElementById("description-charcount");
                var length = $("#id_description").val().length;
                charcount.innerHTML = (length + "/300")
                if (length < 270) {
                    charcount.style.color = "var(--primary-black)"
                } else if (length > 270 && length < 290) {
                    charcount.style.color = "#ff7b00"
                } else if (length >= 290) {
                    charcount.style.color = "red"
                }
            })

            // Event listener for edit profile form
            document.getElementById("edit-profile-savechanges").addEventListener("submit", function(e) {
                e.preventDefault();
                var formData = new FormData(this);

                var url = "/editprofile_savechanges"

                fetch(url, {
                    method : "POST",
                    body : formData,
                    credentials : "same-origin"
                })

                .then(response => response.json())

                .then(response => {
                    switch(response.error) {
                        case "error":
                            showConfirm("Something went wrong. Make sure inputs are filled.")
                            break
                    }

                    if (response.ok == 1) {
                        showConfirm("Changes saved!");
                    }
                })

                .catch(error => {
                    showConfirm("Something went wrong. Try again later.")
                    console.error(error)
                })
            })

            // Event listener for profile picture change
            document.getElementById("profilepic").addEventListener("click", function(){
                ajaxGet("/profilepic_upload", "dark-container", function() {
                    // shows a modal for uploading profile picture in dark container

                    // Add event listener for file input
                    document.getElementById("profilepic-upload").onchange = function() {
                        const formData = new FormData();
                        const fileInput = document.getElementById("profilepic-upload")
                        formData.append('file', fileInput.files[0]);

                        var url = "/profilepic_temp_upload";

                        fetch(url, {
                            method : "POST",
                            body : formData,
                            credentials : "same-origin",
                            headers : {
                                "X-CSRFToken" : csrfToken,
                            }
                        })

                        .then(response => response.json())

                        .then(response => {
                            switch (response.error) {
                                case "error":
                                    showConfirm("Something went wrong. Please try again.")
                                    break
                                case "too_big":
                                    showConfirm("File is too big. Max size is 3MB.")
                                    break
                                case "unsupported":
                                    showConfirm("File type unsupported. Please try uploading a supported type")
                                    break
                            }

                            if (response.file_url != null) {
                                window.location = "profilepic_crop?file_url=" + response.file_url
                            }
                        })

                        .catch(error => {
                            showConfirm("Something went wrong. Please try again later.")
                            console.error(error)
                        })
                    };

                    // Add event listener for cancel button
                    document.getElementById("profilepic-cancel").addEventListener("click", function(){
                        hideDarkContainer()
                    })
                })
            })
        });
    }
}

loadEditProfile();

// Event listeners for navbar

document.getElementById("edit-profile").addEventListener("click", function() {
    loadEditProfile();
})

document.getElementById("edit-profile-mobile").addEventListener("click", function() {
    loadEditProfile();
    hideUniversalDropdown()
})

// Config for personal information page
function loadPersonalInformation() {
    // If youre not already on personal info
    if (currentTab != "personalinfo") {
        // Get the personal info tab
        ajaxGet("/personal_information", "settings-page-container", function() {
            currentTab = "personalinfo"

            // Event listeners for password visibility buttons
            document.getElementById("password-visibility-button-one").addEventListener("click", function() {
                changeVisibility('id_new_password', 'password-visibility-button-one')
            })
    
            document.getElementById("password-visibility-button-two").addEventListener("click", function() {
                changeVisibility('id_new_password_confirm', 'password-visibility-button-two')
            })

            // when change email button is pressed, show form for changing email
            document.getElementById("change-email-button").addEventListener("click", function() {
                emailForm = document.getElementById("change-email-form")
                emailButtonIcon = document.getElementById("change-email-button-icon")

                if (window.getComputedStyle(emailForm).display === 'none'){
                    emailForm.style.display = 'block';
                    emailButtonIcon.style.transform = "rotate(180deg)"
                } else {
                    emailForm.style.display = "none";
                    emailButtonIcon.style.transform = "rotate(0deg)"
                }
            })

            // When change password form is submitted
            document.getElementById("change-password-form").addEventListener("submit", function(e) {
                e.preventDefault();
                // Disable submit button to prevent spam
                $('#password-submit').prop("disabled", true)
                var formData = new FormData(this);
                var modalLoaded = 0;

                var url = "/change_password_modal";

                // Post to url and load in modal if there are no errors
                fetch(url, {
                    method : "POST",
                    body : formData,
                    credentials : "same-origin"
                })

                // Convert response to text/html
                .then(response => response.text())

                .then(response => {
                    switch(response) {
                        case "error":
                            // If there was a general error, but not a server error
                            showConfirm("Something went wrong. Make sure inputs are filled.")
                            break
                        case "match":
                            // If the passwords dont match
                            showConfirm("The passwords you inputted do not match.")
                            break
                        case "same":
                            // If password is the same as the old one
                            showConfirm("Your new password can't be the same as your old one.")
                            break
                        default:
                            // Put modal into dark container and change modal loaded to 1
                            var darkcontainer = document.getElementById("dark-container")
                            darkcontainer.innerHTML = response
                            $('#dark-container').fadeIn(300)
                            modalLoaded = 1
                            break
                    }
                })

                .catch(error => {
                    // If something went wrong
                    showConfirm("Something went wrong. Try again later.")
                    console.error(error)
                })

                .finally(() => {
                    // After post request, if modal is loaded in, add event listeners for modal
                    $('#password-submit').prop("disabled", false)
                    if (modalLoaded == 1) {

                        // If user cancels action, hide modal
                        document.getElementById("change-email-password-cancel-button").addEventListener("click", function() {
                            hideDarkContainer();
                        })

                        // When form to input code to change password is submitted
                        document.getElementById("change-password-form-confirm").addEventListener("submit", function(e) {
                            e.preventDefault();
                            $('#change-email-password-submit').prop("disabled", true)
                            var formData = new FormData(this);

                            var url = "/change_password_modal_confirm"

                            // Post formdata to url
                            fetch(url, {
                                method : "POST",
                                body : formData,
                                credentials : "same-origin"
                            })

                            // Convert response to json
                            .then(response => response.json())

                            .then(response => {
                                switch(response.error) {
                                    case "error":
                                        // If there was something wrong with the input
                                        showConfirm("Something went wrong. Make sure inputs are filled.")
                                        break
                                    case "expired_notfound":
                                        // If code is expired or doesnt exist
                                        showConfirm("The code you inputted is expired or not found.")
                                        break
                                }

                                if (response.ok == 1) {
                                    // If everything went well, hide modal and reload page to show new changes
                                    hideDarkContainer();
                                    loadPersonalInformation();
                                    showConfirm("Password has been changed.");
                                }
                            })

                            .catch(error => {
                                // If something went wrong
                                showConfirm("Something went wrong. Try again later.")
                                console.error(error)
                            })

                            .finally(() => {
                                // After request is done, enable submit button
                                $('#change-email-password-submit').prop("disabled", false)
                            })
                        })
                    }
                })
            })

            // When change email form is submitted, same process as the password form, which is shown above. The diffrence is that password is changed out with email
            document.getElementById("change-email-form").addEventListener("submit", function(e) {
                e.preventDefault();
                $('#email-submit').prop("disabled", true)
                var formData = new FormData(this);
                var modalLoaded = 0;

                var url = "/change_email_modal";

                fetch(url, {
                    method : "POST",
                    body : formData,
                    credentials : "same-origin"
                })

                .then(response => response.text())

                .then(response => {
                    switch(response) {
                        case "error":
                            showConfirm("Something went wrong. Make sure inputs are filled.")
                            break
                        case "match":
                            showConfirm("The e-mails you inputted do not match.")
                            break
                        case "email_taken":
                            showConfirm("This e-mail is already registered to an account.")
                            break
                        default:
                            var darkcontainer = document.getElementById("dark-container")
                            darkcontainer.innerHTML = response
                            $('#dark-container').fadeIn(300)
                            modalLoaded = 1
                            break
                    }
                })

                .catch(error => {
                    showConfirm("Something went wrong. Try again later.")
                    console.error(error)
                })

                .finally(() => {
                    $('#email-submit').prop("disabled", false)
                    if (modalLoaded == 1) {
                        document.getElementById("change-email-password-cancel-button").addEventListener("click", function() {
                            hideDarkContainer();
                        })

                        document.getElementById("change-email-form-confirm").addEventListener("submit", function(e) {
                            e.preventDefault();
                            $('#change-email-password-submit').prop("disabled", true)
                            var formData = new FormData(this);

                            var url = "/change_email_modal_confirm"

                            fetch(url, {
                                method : "POST",
                                body : formData,
                                credentials : "same-origin"
                            })

                            .then(response => response.json())

                            .then(response => {
                                switch(response.error) {
                                    case "error":
                                        showConfirm("Something went wrong. Make sure inputs are filled and that code is a number.")
                                        break
                                    case "expired_notfound":
                                        showConfirm("The code you inputted is expired or not found.")
                                        break
                                }

                                if (response.ok == 1) {
                                    hideDarkContainer();
                                    currentTab = ""
                                    loadPersonalInformation();
                                    showConfirm("E-mail has been changed.");
                                }
                            })

                            .catch(error => {
                                showConfirm("Something went wrong. Try again later.")
                                console.error(error)
                            })

                            .finally(() => {
                                $('#change-email-password-submit').prop("disabled", false)
                            })
                        })
                    }
                })
            })
        })
    }
}

// Event listeners for dropdown
document.getElementById("personal-information").addEventListener("click", function() {
    loadPersonalInformation();
})

document.getElementById("personal-information-mobile").addEventListener("click", function() {
    loadPersonalInformation();
    hideUniversalDropdown();
})

// Ping interval
setInterval(function() {
    ping();
    checkMatchInvites();
}, 5000)

// When document loads in, ping
document.addEventListener("DOMContentLoaded", function() {
    ping();
    checkMatchInvites();
})