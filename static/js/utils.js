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
let messageWebsocket = null;


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
            console.log(event)
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
            } else if (data.type === 'messaging_notification') {

                    $('#message-list').append(data.html)
                    let user = $('#message-list').data('user')
                   
                    if(data.created_by === user){

                        $('#message-list .new-message').removeClass('new-message').addClass('my-message');
                    }else{
                        $('#message-list .new-message').removeClass('new-message')
                    }

            }else {
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
    let processData = undefined;
    let contentType = undefined;

    if (data instanceof FormData) {
        processData = false;
        contentType = false;
    }
    
    $.ajax({
        type: type,
        url: url,
        data: data,
        processData: processData,  
        contentType: contentType,  
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
    }else if(type === 'messaging'){
        if(messageWebsocket){
            messageWebsocket.close()
        }
        messageWebsocket = new WebSocket(url)
        websocketInit(messageWebsocket); 
    
    }else{
        if(commentsWebSocket){
            commentsWebSocket.close()
        }
        commentsWebSocket = new WebSocket(url)
        websocketInit(commentsWebSocket); 
    }
}


    /**
 * Display a modal with the specified header and body content.
 *
 * @param {string} header - The header content of the modal.
 * @param {string} body - The body content of the modal.
 */
    function showModal(header, body,) {
        // Check if the modal already exists
        let modal = $('#modal');
        if (modal.length === 0) {
            // If not, create the modal element
            modal = $(`
            <div class="modal fade modal" id="modal" tabindex="-1" role="dialog" aria-labelledby="model" aria-hidden="true">
                <div class="modal-dialog modal-div " role="document">
                    <div class="modal-content mt-5 ">
                        <div class="modal-header d-block text-center"></div>
                        <div class="modal-body scrollable-div text-center"></div>
                    </div>
                </div>
            </div>
        `);

            // Append the modal to the body
            $('body').append(modal);
        }

        // Find the modal-header and modal-body elements within the modal
        modal.find('.modal-header').html(header);
        modal.find('.modal-body').html(body);

        modal.modal('show');
    }