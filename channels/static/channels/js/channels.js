/////////////////code to add user to channel with ajax////////////////////
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
          console.log(data)
      })
      .fail(function(jqXHR, textStatus, errorThrown) {
          console.error('There was a problem with the AJAX request:', errorThrown);
      });
  });

// /////////////////// Functions to load the posts and send posts on larger screens with ajax///////////////////
document.addEventListener('DOMContentLoaded', function () {
    const channnelBtns = $('.back-btn');
    const channelLinks = $('#channel-links-container');
    const channelPosts = $('#channnnel-posts');
    const summernote = $('.channels-summernote');
    const tabsNav = $('#nav-bar')

    if(channel_id > 0 && window.innerWidth < 575){
        channelPosts.toggleClass('hide');
        channelLinks.toggleClass('hide');
        summernote.toggleClass('d-none')
    }
    channnelBtns.click(function () {
        channelPosts.toggleClass('hide');
        channelLinks.toggleClass('hide');
        summernote.toggleClass('d-none');
        tabsNav.toggleClass('d-none');

    });
});

