// JavaScript file for settings page

// onload, default page is profile editing
function loadEditProfile() {
    ajaxGet("/edit_profile", "settings-page-container", function() {
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

loadEditProfile();

// Funciton that hides mobile dropdown
function hideDropdown() {
    dropdown = document.getElementById("navbar-background")
    if (window.getComputedStyle(dropdown).display !== 'none'){
        $('#settings-navbar').animate({
            width:'0px'
        }, 200);
        setTimeout(function() {
            document.getElementById("settings-navbar").style.display = "none"
        }, 200)
        $('#navbar-background').delay(200).fadeOut(200)
    }
}

// Event listeners for navbar

document.getElementById("edit-profile").addEventListener("click", function() {
    loadEditProfile();
    hideDropdown()
})

document.getElementById("personal_information").addEventListener("click", function() {
    ajaxGet("/personal_information", "settings-page-container", function() {
        hideDropdown()

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
    })
})

document.getElementById("dropdown-button").addEventListener("click", function() {
    document.getElementById("navbar-background").style.display = "inline"
    document.getElementById("settings-navbar").style.display = "inline"
    $('#settings-navbar').animate({
        width:'290px'
    });
})

document.getElementById("dropdown-button-exit").addEventListener("click", function() {
    $('#settings-navbar').animate({
        width:'0px'
    }, 200);
    setTimeout(function() {
        document.getElementById("settings-navbar").style.display = "none"
    }, 200)
    $('#navbar-background').delay(200).fadeOut(200)
})

