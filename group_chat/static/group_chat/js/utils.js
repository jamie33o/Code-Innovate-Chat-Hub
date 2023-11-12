let isAnimationInProgress = false;
let currentUser = null;
/////////////////////// function for notification messages ///////////////////////////////


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
            // and create and add the post/comment to the list
            const data = JSON.parse(event.data);
            if (data.type === 'post_notification') {

                if (data.html) {
                    $('#posts-list').append(data.html);
                    if(data.created_by === currentUser){
                        autoScroll(true)
                    }else {
                        displayMessage({status: 'Success', message : data.message});
                    }                 
                }            
            } else if (data.type === 'comment_notification') {
                if (data.html) {
                    $('.comments-list').append(data.html);
                    if(data.created_by === currentUser){
                        autoScroll(true)
                    }else {
                        displayMessage({status: 'Success', message : data.message});
                    }
                    console.log('comment');
                }
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

function ajaxRequest(url, csrfToken, type, divClass, data, callBackFunction) {
    $.ajax({
        type: type,
        url: url,
        data: data,
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

function startWebSocket(type, id){
    let url = null;
    if (window.location.protocol === 'http:') {
        url = `ws://${window.location.host}/ws/${type}/${id}/`
    } else if (window.location.protocol === 'https:') {
        url = `wss://${window.location.host}/ws/${type}/${id}/`
    } 
    websocketInit(url); 

}


