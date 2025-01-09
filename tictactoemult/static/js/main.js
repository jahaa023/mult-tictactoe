// JavaScript file for the main page

// jQuery animations for play buttons

$('#header-play-button-1').mouseenter(function() {
    $('#header-play-button-1').stop()
    $('#header-play-button-1').animate({
        width: '500px'
    });
})

$('#header-play-button-1').mouseleave(function() {
    $('#header-play-button-1').stop()
    $('#header-play-button-1').animate({
        width: '400px'
    });
})

$('#header-play-button-2').mouseenter(function() {
    $('#header-play-button-2').stop()
    $('#header-play-button-2').animate({
        width:'500px'
    });
})

$('#header-play-button-2').mouseleave(function() {
    $('#header-play-button-2').stop()
    $('#header-play-button-2').animate({
        width:'400px'
    });
})