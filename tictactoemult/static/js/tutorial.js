// JavaScript file for the tutorial page
const tutorialPageContainer = document.getElementById("tutorial-page-container")
var currentPage = "";

// Loads in the welcome page on startup
document.addEventListener("DOMContentLoaded", function() {
    loadTutorialPage("welcome")
})

// Function to load in pages for tutorial
function loadTutorialPage(name) {
    const url = `/tutorial/${name}`

    fetch(url, {
        method: "GET",
        credentials: "same-origin"
    })

    .then(response => response.text())

    .then(response => {
        tutorialPageContainer.innerHTML = response;
        hideUniversalDropdown();
        currentPage = name
    })

    .catch(error => {
        console.error(error);
        showConfirm("Something went wrong.")
    })
}

// Make back link point to correct page
const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const origin = urlParams.get('origin')
const backLink = document.getElementById("back-link")
const backLinkMobile = document.getElementById("back-link-mobile")
if (origin == "index") {
    backLink.setAttribute("href", "/")
    backLink.innerHTML = "Back to login"
    backLink.title = "Back to login"

    backLinkMobile.setAttribute("href", "/")
    backLinkMobile.innerHTML = "Back to login"
    backLinkMobile.title = "Back to login"
} else if (origin == "main") {
    backLink.setAttribute("href", "/main")
    backLink.innerHTML = "Back to main page"
    backLink.title = "Back to main page"

    backLinkMobile.setAttribute("href", "/main")
    backLinkMobile.innerHTML = "Back to main page"
    backLinkMobile.title = "Back to main page"
}


const pages = ["welcome", "creating-account", "editing-profile"]

pages.forEach(function(pageName) {
    document.getElementById(pageName).addEventListener("click", function() {
        if (currentPage != pageName) {
            loadTutorialPage(pageName)
        }
    })

    document.getElementById(`${pageName}-mobile`).addEventListener("click", function() {
        if (currentPage != pageName) {
            loadTutorialPage(pageName)
        }
    })
})