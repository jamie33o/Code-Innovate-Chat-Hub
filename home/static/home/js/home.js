let channel_id = null;

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

///////////////////// Functions to hide and show channels, posts and comments///////////////////


///////////////////////websocket for channel posts///////////////////////////////

function websocketInit(channel_id, url) {
    const socketUrl = `wss://${window.location.host}/ws/home/${channel_id}/`

    let socket = new WebSocket(socketUrl);

    socket.addEventListener('message', function(event) {
        // when a new message is broadcast this websocket will receive it 
        // and create and add the post to the list
        const data = JSON.parse(event.data);
        const currentTime = getCurrentTime();

        if (data.post_content) {
        
            const newPostItem = $('<li class="post-item mx-auto">');
            const postHeader = $('<div class="post-header d-flex flex-dir-row">').html(`
                <h5>${data.post_creator}</h5>
                <p class="ml-3">${currentTime}</p>
            `);
            const postContent = $('<div class="post-content">').html(`<p>${data.post_content}</p>`);
            
            newPostItem.append(postHeader, postContent);
            $('#posts-ul').append(newPostItem);
            
        
        }
    });

    socket.addEventListener('error', function(event) {
        console.error('WebSocket Error:', event);
    });

    socket.addEventListener('close', function(event) {
        console.log('WebSocket Closed:', event);
    });

}

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
//////////////////// function to load posts ///////////////////////


  function getRequestToDjamgo(event, divToAddContent){
    const url = event.currentTarget.href;

     // AJAX request
     $.ajax({
        type: "GET",
        url: url,
        success: function(response) {
          // Update the div with the returned template
          $(divToAddContent).html(response);
  
        },
        error: function(error) {
          console.log("Error:", error);
        }
      });
  }