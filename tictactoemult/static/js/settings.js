// JavaScript file for settings page

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
            $('#edit-profile-savechanges').on("submit", function (e){
                e.preventDefault();
                var formData = new FormData(this);

                $.ajax({
                    url: '/editprofile_savechanges',
                    type: 'POST',
                    data: formData,
                    success: function (response) {
                        switch(response) {
                            case "error":
                                showConfirm("Something went wrong. Make sure inputs are filled.")
                                break
                            case "ok":
                                showConfirm("Changes saved!");
                        }
                    },
                    error: function() {
                        showConfirm("Something went wrong. Try again later.")
                    },
                    cache: false,
                    contentType: false,
                    processData: false,
                });
            })

            // Event listener for profile picture change
            document.getElementById("profilepic").addEventListener("click", function(){
                ajaxGet("/profilepic_upload", "dark-container", function() {
                    // shows a modal for uploading profile picture in dark container

                    // Add event listener for file input
                    document.getElementById("profilepic-upload").onchange = function(e) {
                        // Convert file to blob
                        blob_url = URL.createObjectURL(this.files[0]);
                        // Redirect to cropping page
                        window.location.href = "/profilepic_crop?blob=" + blob_url
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
    if (currentTab != "personalinfo") {
        ajaxGet("/personal_information", "settings-page-container", function() {
            currentTab = "personalinfo"

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
            $('#change-password-form').on("submit", function (e){
                e.preventDefault();
                $('#password-submit').prop("disabled", true)
                var formData = new FormData(this);
                var modalLoaded = 0;

                $.ajax({
                    url: '/change_password_modal',
                    type: 'POST',
                    data: formData,
                    success: function (response) {
                        switch(response) {
                            case "error":
                                showConfirm("Something went wrong. Make sure inputs are filled.")
                                break
                            case "match":
                                showConfirm("The passwords you inputted do not match.")
                                break
                            case "same":
                                showConfirm("Your new password can't be the same as your old one.")
                            default:
                                var darkcontainer = document.getElementById("dark-container")
                                darkcontainer.innerHTML = response
                                $('#dark-container').fadeIn(300)
                                modalLoaded = 1
                                break
                        }
                    },
                    error: function() {
                        showConfirm("Something went wrong. Try again later.")
                    },
                    complete: function() {
                        $('#password-submit').prop("disabled", false)
                        if (modalLoaded == 1) {
                            document.getElementById("change-email-password-cancel-button").addEventListener("click", function() {
                                hideDarkContainer();
                            })

                            $('#change-password-form-confirm').on("submit", function (e){
                                e.preventDefault();
                                $('#change-email-password-submit').prop("disabled", true)
                                var formData = new FormData(this);
                    
                                $.ajax({
                                    url: '/change_password_modal_confirm',
                                    type: 'POST',
                                    data: formData,
                                    success: function (response) {
                                        switch(response) {
                                            case "error":
                                                showConfirm("Something went wrong. Make sure inputs are filled.")
                                                break
                                            case "expired_notfound":
                                                showConfirm("The code you inputted is expired or not found.")
                                                break
                                            case "ok":
                                                hideDarkContainer();
                                                loadPersonalInformation();
                                                showConfirm("Password has been changed.");
                                                break
                                        }
                                    },
                                    error: function() {
                                        showConfirm("Something went wrong. Try again later.")
                                    },
                                    complete: function() {
                                        $('#change-email-password-submit').prop("disabled", false)
                                    },
                                    cache: false,
                                    contentType: false,
                                    processData: false,
                                });
                            })
                        }
                    },
                    cache: false,
                    contentType: false,
                    processData: false,
                });
            })

            // When change email form is submitted
            $('#change-email-form').on("submit", function (e){
                e.preventDefault();
                $('#email-submit').prop("disabled", true)
                var formData = new FormData(this);
                var modalLoaded = 0;

                $.ajax({
                    url: '/change_email_modal',
                    type: 'POST',
                    data: formData,
                    success: function (response) {
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
                    },
                    error: function() {
                        showConfirm("Something went wrong. Try again later.")
                    },
                    complete: function() {
                        $('#email-submit').prop("disabled", false)
                        if (modalLoaded == 1) {
                            document.getElementById("change-email-password-cancel-button").addEventListener("click", function() {
                                hideDarkContainer();
                            })

                            $('#change-email-form-confirm').on("submit", function (e){
                                e.preventDefault();
                                $('#change-email-password-submit').prop("disabled", true)
                                var formData = new FormData(this);
                    
                                $.ajax({
                                    url: '/change_email_modal_confirm',
                                    type: 'POST',
                                    data: formData,
                                    success: function (response) {
                                        switch(response) {
                                            case "error":
                                                showConfirm("Something went wrong. Make sure inputs are filled and that code is a number.")
                                                break
                                            case "expired_notfound":
                                                showConfirm("The code you inputted is expired or not found.")
                                                break
                                            case "ok":
                                                hideDarkContainer();
                                                currentTab = ""
                                                loadPersonalInformation();
                                                showConfirm("E-mail has been changed.");
                                                break
                                        }
                                    },
                                    error: function() {
                                        showConfirm("Something went wrong. Try again later.")
                                    },
                                    complete: function() {
                                        $('#change-email-password-submit').prop("disabled", false)
                                    },
                                    cache: false,
                                    contentType: false,
                                    processData: false,
                                });
                            })
                        }
                    },
                    cache: false,
                    contentType: false,
                    processData: false,
                });
            })
        })
    }
}

document.getElementById("personal-information").addEventListener("click", function() {
    loadPersonalInformation();
})

document.getElementById("personal-information-mobile").addEventListener("click", function() {
    loadPersonalInformation();
    hideUniversalDropdown();
})