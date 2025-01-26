// JavaScript file for page for cropping profile picture

// Configure cropper js when dom is ready
$( document ).ready(function() {
    // Set image src to blob in url
    const urlParams = new URLSearchParams(window.location.search);
    const file_url = urlParams.get('file_url')
    const image = document.getElementById("cropper-js-image")
    image.src = file_url

    // Configure cropper js
    const cropper = new Cropper(image, {
        aspectRatio: 1/1,
        dragMode: 'none',
        preview: '.profilepic-crop-preview'
    })

    // Save button, does a post request
    $('#save-button').on("click", function (e){
        $('#save-button').prop("disabled", true)
        canvas = cropper.getCroppedCanvas({
            width: 512,
            height: 512
        })

        // Convert cropped image to data url in base 64 and post it
        var base64image = canvas.toDataURL('image/jpeg')

        // include csrftoken
        var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();

        $.ajax({
            url: '/profilepic_cropped_upload',
            type: 'POST',
            data : {
                image_data : base64image,
                csrfmiddlewaretoken : csrfmiddlewaretoken
            },
            success: function (response) {
                switch(response) {
                    case "error":
                        showConfirm("Something went wrong.")
                        break
                    case "ok":
                        window.location.href = "/settings";
                }
            },
            error: function() {
                showConfirm("Something went wrong. Try again later.")
            },
            complete: function() {
                $('#save-button').prop("disabled", false)
            }
        });
    })    
});

// Event listeners

// Cancel button, redirects back to settings
document.getElementById("cancel-button").addEventListener("click", function(){
    window.location.href = "/settings"
})

// Ping interval
setInterval(function() {
    ping();
}, 5000)

// When document loads in, ping
document.addEventListener("DOMContentLoaded", function() {
    ping();
})