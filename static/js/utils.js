/**
 * Flag to track whether an animation is currently in progress.
 * @type {boolean}
 */
let isAnimationInProgress = false;

/**
 * Reference to the current user.
 * @type {null}
 */
let currentUser = null;
let postsWebSocket = null;
let commentsWebSocket = null;


/////////////////////// function for notification messages ///////////////////////////////


/**
 * Displays a notification message and handles the animation.
 * @param {Object} response - The response object containing status and message.
 * @param {string} divClass - The class of the HTML element to append the notification.
 */
function displayMessage(response, divClass){     
    // Check if the animation is already in progress
    if (isAnimationInProgress) {
        return;
    } 
    let messageLi = `
    <div class="notification">
        <ul class="notification-messages">
            <li class="message-item ${response.status.toLowerCase()}">
                <h3>${response.status}</h3>
                <p>${response.message}</p>
            </li>
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

///////////////////////websocket for comments/ posts///////////////////////////////
/**
 * Initializes the WebSocket connection.
 * @param {string} socketUrl - The WebSocket URL.
 */
function websocketInit(socket) {
        
        // Open event listener
        socket.addEventListener('open', function (event) {

        });

          // Message event listener
          socket.addEventListener('message', function (event) {
             // when a new message is broadcast, this websocket will receive it
            // and create and add the post/comment to the list
            const data = JSON.parse(event.data);
            if (data.type === 'post_notification') {
                if (data.html) {
                    if(data.edit_id){
                        $(`.post${data.edit_id}`).replaceWith(data.html);
                    }else{
                        $('#posts-list').append(data.html);
                        
                        if(data.created_by === currentUser){
                            autoScroll(true)
                        }else {
                            displayMessage({status: 'Success', message : data.message}, '#channel-posts');
                        } 
                    }                
                }            
            } else if (data.type === 'comment_notification') {
                if (data.html) {
                    if(data.edit_id){
                        $(`.comment${data.edit_id}`).replaceWith(data.html);
                    }else{
                        $('.comments-list').append(data.html);
                        
                        if(data.created_by === currentUser){
                            autoScroll(true)
                        }else {
                            displayMessage({status: 'Success', message : data.message}, '.comments-list');
                        }
                    }
                }
            } else {
                console.error('Unknown notification type:', data.type);
            }
            
        });

        socket.addEventListener('error', function(event) {
            setTimeout(() => websocketInit(this), 1000);
        });

        socket.addEventListener('close', function(event) {
            // Attempt to reconnect after a delay if the socket ends due to error 
            if(!event.wasClean){
                setTimeout(() => websocketInit(this), 1000);
            }
        });

}

/**
 * Sends an AJAX request.
 * @param {string} url - The URL for the AJAX request.
 * @param {string} csrfToken - The CSRF token for the request headers.
 * @param {string} type - The type of the request (e.g., 'GET' or 'POST').
 * @param {string} divClass - The class of the HTML element to append the response.
 * @param {Object} data - The data to send with the request.
 * @param {function} callBackFunction - Callback function to handle the response.
 */
function ajaxRequest(url, csrfToken, type, divClass, data, callBackFunction) {
    $.ajax({
        type: type,
        url: url,
        data: data,
        processData: false,  
        contentType: false,  
        headers: {'X-CSRFToken': csrfToken},  
        success: (response) => {
            if(callBackFunction){
                callBackFunction(response)
            }else{
                displayMessage(response, divClass)            
            }
        },
        error: function(error) {
            displayMessage({status:'error', message: error.statusText}, divClass)
        }
    });
}

/**
 * function to choose which url to use based on the protocol and parameters
 * for posts and comments in production and development.
 * @param {string} type - posts or comments.
 * @param {string} id - The ID for the WebSocket connection.
 */
function startWebSocket(type, id){
    let url = null;
    if (window.location.protocol === 'http:') {
        url = `ws://${window.location.host}/ws/${type}/${id}/`
    } else if (window.location.protocol === 'https:') {
        url = `wss://${window.location.host}/ws/${type}/${id}/`
    } 

    if(type === 'channel_posts'){
        if(postsWebSocket){
            postsWebSocket.close()
        }
        postsWebSocket = new WebSocket(url)
        websocketInit(postsWebSocket); 
    }else{
        if(commentsWebSocket){
            commentsWebSocket.close()
        }
        commentsWebSocket = new WebSocket(url)
        websocketInit(commentsWebSocket); 
    }

}

