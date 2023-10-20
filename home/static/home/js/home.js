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

function websocketInit(socketUrl) {
    let socket = null;

    function connect(socketUrl) {

        socket = new WebSocket(socketUrl);

        // Open event listener
        socket.addEventListener('open', function (event) {
            console.log('WebSocket connection opened:', event);
            // Additional actions when the connection is open, if needed
        });

          // Message event listener
          socket.addEventListener('message', function (event) {
             // when a new message is broadcast, this websocket will receive it
            // and create and add the post to the list
            const data = JSON.parse(event.data);
            const currentTime = getCurrentTime(); 

            if (data.type === 'post_notification') {
                handlePostNotification(data, currentTime);
            } else if (data.type === 'comment_notification') {
                handleCommentNotification(data, currentTime);
            } else {
                console.error('Unknown notification type:', data.type);
            }
            
        });

        socket.addEventListener('error', function(event) {
            console.error('WebSocket Error:', event);
        });

        socket.addEventListener('close', function(event) {
            console.log('WebSocket Closed:', event);
            // Attempt to reconnect after a delay
            setTimeout(() => connect(socketUrl), 1000);

        });

    }
    connect(socketUrl); //initial connect

}

function handlePostNotification(data, currentTime){
    if (data.post_content) {
        const newPostItem = $('<li class="post-item mx-auto">');
        const postHeader = $('<div class="post-header d-flex flex-dir-row">').html(`
            <h5>${data.post_creator}</h5>
            <p class="ml-3">${currentTime}</p>
        `);
        const postContent = $('<div class="post-content">').html(`<p>${data.post_content}</p>`);

        newPostItem.append(postHeader, postContent);
        $('#posts-ul').append(newPostItem);
        console.log('post');
    }
}

function handleCommentNotification(data, currentTime){
    if (data.comment_content) {
        const newPostItem = $('<li class="post-item mx-auto">');
        const postHeader = $('<div class="post-header d-flex flex-dir-row">').html(`
            <h5>${data.comment_creator}</h5>
            <p class="ml-3">${currentTime}</p>
        `);
        const postContent = $('<div class="post-content">').html(`<p>${data.comment_content}</p>`);

        newPostItem.append(postHeader, postContent);
        $('#comments-ul').append(newPostItem);
        console.log('comment');
    }
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


function getRequestToDjamgo(divToAddContent, url){
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


function addUserPostRequest(url, csrftoken){
    // AJAX request
    $.ajax({
        type: "POST",
        url: url,
        headers: {
            'X-CSRFToken': csrftoken
        },
        success: function(response) {
            $('#overlay').toggleClass('d-none')
            displayMessage(response)
        },
        error: function(error) {
            console.log('error')

            displayMessage(error)
        }
    });
}

function displayMessage(response){
    let notification = $('.notification')

       $('.messages').toggleClass('d-none')
       notification.addClass('notification-keyframe-start')
       $(`.notification .${response.status}`).toggleClass('d-none')
       setTimeout(function() {
           notification.addClass('notification-keyframe-finish')
           
           notification.on('animationend webkitAnimationEnd oAnimationEnd', function() {
           $(`.notification .${response.status}`).toggleClass('d-none')
           $('.messages').toggleClass('d-none')
        });
       }, 5000);

       
}