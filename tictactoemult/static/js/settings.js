// JavaScript file for settings page

// onload, default page is profile editing
ajaxGet("/edit_profile", "settings-page-container");

// Event listeners for navbar

document.getElementById("edit-profile").addEventListener("click", function() {
    ajaxGet("/edit_profile", "settings-page-container", showConfirm("Hello"));
})