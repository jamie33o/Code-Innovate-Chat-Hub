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
        <div class="toast-header ${response.status.toLowerCase()}">
            <img src="..." class="rounded mr-2" alt="...">
            <strong class="mr-auto">${response.status.toUpperCase()}</strong>
            <small>11 mins ago</small>
        </div>
        <div class="toast-body message-item">
            
            <p>${response.message}</p>  
        </div>
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
                        $(`.edit-post`).replaceWith(data.html);
                        // if its not the user that created it then hide dropdown menu on the edited post
                        if(data.created_by != currentUser){
                            $('.post${data.edit_id} .dropdown').addClass('d-none')
                        }
                    }else{
                        $('#posts-list').append(data.html);
                        
                        if(data.created_by === currentUser){
                            // auto scroll if its the user that created it
                            autoScroll(true)
                        }else {
                            // otherwise display message to user that there is a new post
                            displayMessage({status: 'Success', message : data.message}, '#channel-posts');
                             // if its not the user that created it then hide dropdown menu on the edited post
                            $('#posts-list .card:last .dropdown').addClass('d-none')
                        } 
                    }                
                }            
            } else if (data.type === 'comment_notification') {
                if (data.html) {
                    if(data.edit_id){
                        $(`.edit-post`).replaceWith(data.html);
                        //let user = $('#message-list').data('user')
                        // if its the user that created it then hide dropdown menu on comments
                        if(data.created_by != currentUser){
                            $('.comment${data.edit_id} .dropdown').addClass('d-none')
                        }
                    }else{
                        $('.comments-list').append(data.html);
                        
                        if(data.created_by === currentUser){
                            autoScroll(true)
                        }else {
                            displayMessage({status: 'Success', message : data.message}, '.comments-list');
                            $('.comment${data.edit_id} .dropdown').addClass('d-none')
                        }
                       
                    }
                }
            } else if (data.type === 'messaging_notification') {
                    $('#message-list').append(data.html)
                    let user = $('#message-list').data('user')
                   // if its the user that created it add the class my-message
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


//////////////////////////// show profile ///////////////////////////////////
// view profile modal shows when profile pic clicked

$(document).ready(function(){
    $('body').on('click', '.profile-pic', function(){
        console.log('woring')
        let header = `
        <div class="d-flex justify-content-between align-items-center w-100">
            <h3 class="display-7 text-center mb-0 mx-auto">User Profile</h3>
            <button class="btn btn-warning" data-dismiss="modal" type="button">X</button>
        </div>

        `;
        let url = $(this).data('url')
        ajaxRequest(url, csrfToken, 'GET', '#channel-posts', null, function(response){
            showModal(header, response)
            showModal()
        });
        
    });
})
