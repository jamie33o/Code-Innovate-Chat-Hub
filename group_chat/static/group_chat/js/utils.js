/////////////////////// function for notification messages ///////////////////////////////
let isAnimationInProgress = false;

function displayMessage(response, divClass){     
    // Check if the animation is already in progress
    if (isAnimationInProgress) {
        return;
    } 
    let messageLi = `
    <div class="notification">
        <ul class="notification-messages">
        <li class="message-item ${response.status.toLowerCase()}"><h3>${response.status}</h3><p>${response.message}</p></li>
        </ul>
    </div>
    `;
    $(divClass).append(messageLi)

    isAnimationInProgress = true;
    let notification = $('.notification')
    notification.addClass('notification-keyframe-start')
    let animationEndHandled = false;

    
    setTimeout(function() {        
        notification.removeClass('notification-keyframe-start')
        notification.addClass('notification-keyframe-finish')

        notification.on('animationend webkitAnimationEnd oAnimationEnd', function() {
            if (!animationEndHandled) {

            notification.removeClass('notification-keyframe-finish')

            notification.off('animationend webkitAnimationEnd oAnimationEnd', this);
            $(`.notification`).remove()        

            // Reset animation state       
            isAnimationInProgress = false;
            animationEndHandled = true;


            }
        });
    }, 5000);
}

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


// function to load posts
function getRequestToDjango(divToAddContent, url){
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


// function for adding and removing emoji on posts
function postRequestToDjango(url, emojiColonName, args, emoji){
    let id = url.match(/\d+/g);
    let spanElement = $(emoji).find('span');
    let currentNumber = null
    $.ajax({
        url: url,  
        type: 'POST',
        data: {
            emoji_colon_name: emojiColonName,
        },
        success: function (response) {
            // Handle success
            switch (response.status) {
                case "added":

                    let emojiUlClass = `.emoji-list${id}`
                    let em = $(emoji).prop('outerHTML');

                    let newLi = $(`
                        <li class="list-inline-item mr-2">
                            <button class="added-emoji-btn btn" data-emoji-url="${url}" 
                                    data-target="#emojiModal${id}" 
                                    data-emoji-code="${emojiColonName}">
                                    ${em}
                                <span></span>
                            </button>
                            <!-- Small Box Modal -->
                            <div class="emoji-user-count-modal d-none" id="emojiModal${id}">
                                <div class="modal-dialog modal-sm">
                                    <div class="modal-content">
                                        <div class="modal-header">
                                            <h5 class="modal-title" id="emojiModalLabel">${em}</h5>
                                        </div>
                                        <div class="modal-body">
                                            <p>You reacted with ${emojiColonName}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </li>
                    `);
                    
                    $(emojiUlClass).append(newLi);
                  break;
                case "decremented":                   
                     currentNumber = parseInt(spanElement.html(), 10);

                    if (!isNaN(currentNumber)) {
                    // Check if currentNumber is a valid number

                    // Subtract 1 from the current number
                    let newNumber = currentNumber - 1;
                    if(newNumber > 1){
                    // Update the HTML content of the span element with the new number
                    spanElement.html(newNumber);
                    }else{
                        spanElement.html('');

                    }
                    }
                  break;
                case "incremented":
                     currentNumber = parseInt(spanElement.html(), 10);
                    if (!isNaN(currentNumber)) {
                    // add 1 to the current number
                    let newNumber = currentNumber + 1;
                    // Update the HTML content of the span element with the new number
                    spanElement.html(newNumber);
                    }else{
                        spanElement.html(2);
                    }
                   
                  break;
                  case "removed":
                    $(args).parent().remove()
                }           

        },
        error: function (error) {
            // Handle error
            // displayMessage({`status`: 'error'})
        }
    });
}

function deleteObject(deletePostUrl, csrfToken){
    $.ajax({
        type: 'DELETE',
        url: deletePostUrl,
        headers: {'X-CSRFToken': csrfToken},  // Use a function to get the CSRF token

        success: function(response) {
            // Handle success, e.g., redirect to success_url or update UI
            displayMessage(response, '#channel-posts')
        },
        error: function(error) {
            // Handle error, e.g., display an error message
            displayMessage(error, '#channel-posts')
        }
    });
}



