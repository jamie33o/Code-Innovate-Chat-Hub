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

///////////////////// Functions to hide and show channels, posts and summernote///////////////////
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

///////////////////////websocket for channel posts///////////////////////////////

const socket = new WebSocket('ws://127.0.0.1:8000/ws/home/1/');

socket.addEventListener('message', function(event) {
    const data = JSON.parse(event.data);
    const currentTime = getCurrentTime();

    if (data.post_content) {
    
        // Create a new <li> element with the received post content
        const newPostItem = $('<li class="post-item mx-auto">').html(`
            <div class="post-header d-flex flex-dir-row">
                <h5>${data.post_creator}</h5>
                <p class="ml-3">${currentTime}</p>
            </div>
            <div class="post-content">
                <p>${data.post_content}</p>
            </div>
        `);

        // Append the new <li> element to the existing <ul> element
        $('#posts-ul').append(newPostItem);
    
    }
});

function getCurrentTime() {
    const now = new Date();

    // Get hours, minutes, and seconds
    let hours = now.getHours();
    let minutes = now.getMinutes();

    // Add leading zero if needed
    hours = (hours < 10) ? `0${hours}` : hours;
    minutes = (minutes < 10) ? `0${minutes}` : minutes;

    // Construct the time string in 24-hour format
    const currentTime = `${hours}:${minutes}`;

    return currentTime;
}