// Toggle the visibility of the messages list when the button is clicked
$('.toggleLinksButton').click(function() {
    var target = $(this).data('target');

    $(target).toggleClass('d-none')
    $(this).find('i').toggleClass('fa-rotate-90');

});

// Use the ready function to execute code when the DOM is fully loaded
// Click event for the button
$('main').on('click', '.channel-link', function(event) {
    event.preventDefault();
    
    $('.channel-link').removeClass('active')

    $(this).find('.unread-indicator').remove()
    $(this).addClass('active')
    lastChannel = $(this)
    let url = event.currentTarget.href
    ajaxRequest(url, null, 'Get', '#channel-posts', null, function(response){
        $('#channel-posts').html(response)
        autoScroll()
    } )
   

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


