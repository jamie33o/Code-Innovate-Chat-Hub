///////////////////////////////  initialize channels list listeners ////////////////////////////

// Toggle the visibility of the messages list when the button is clicked
$('.toggleLinksButton').click(function() {
    var target = $(this).data('target');

    $(target).toggleClass('d-none')
    $(this).find('i').toggleClass('fa-rotate-90');

});

// Use the ready function to execute code when the DOM is fully loaded
// Click event for the button
$(".channel-link").click(function(event) {
    event.preventDefault();
    $(this).find('.unread-indicator').remove()
    url = event.currentTarget.href
    getRequestToDjango('#channel-posts', url)
    if(window.innerWidth < 575){
        $('#channel-posts').toggleClass('d-flex');
        $('#channel-links-container').toggleClass('hide');
        $('#nav-bar').addClass('d-none')
        $('header').addClass('d-none')

    }
    $('#post-comments').removeClass('d-flex');
});



/////////////////code to add user to channel with ajax////////////////////
// this is a button overlay that shows when user is not added to a the channel
const addChannelButton = document.getElementById('add-channel-button');
const overlay = document.getElementById('overlay');

if (addChannelButton && overlay) {
    addChannelButton.addEventListener('click', function() {
        overlay.style.display = 'block';
    });
  }

$("#add_user_to_channel").click(function(event) {
    event.preventDefault(); // Prevent the default navigation behavior

    $.get($(this).attr("href"), function(data) {
        // Display the response in the response-container element
        $("#add_user_to_channel").text(data);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        console.error('There was a problem with the AJAX request:', errorThrown);
    });
});


// add user to channel
function addUserPostRequest(url, csrftoken){
    // AJAX request
    $.ajax({
        type: "POST",
        url: url,
        headers: {
            'X-CSRFToken': csrftoken
        },
        success: function(response) {
            $('#overlay').addClass('d-none')
            displayMessage(response)
        },
        error: function(error) {
            displayMessage(error)
        }
    });
}