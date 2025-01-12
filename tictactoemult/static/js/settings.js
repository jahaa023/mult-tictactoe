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
    });
}

// Event listeners for navbar

document.getElementById("edit-profile").addEventListener("click", function() {
    loadEditProfile();
})

loadEditProfile();