let channel_id = null;
let postId = null;
let emojiPostUrl = null;
let url = null
let emojiPickerPosts = null

////////////////////////// functions for posts ///////////////////////////////////
function initializeEmojiPicker() {
    // Your existing code for emojiPickerPosts
     emojiPickerPosts = new EmojiPicker('#for-emoji-picker', emojiPickerCallback);


}

// function thats called from posts template when its loaded
function initPosts(){
    // Click event for the close posts button
    $(".posts-close-btn").click(function(event) {
        $('#channel-posts').toggleClass('d-flex');
        $('#channel-links-container').toggleClass('hide');
        $('#nav-bar').removeClass('d-none')
        $('header').removeClass('d-none')
    });


    $(".post-emoji-btn").click(function(event) {
        event.preventDefault()
        postId = $(this).data('post-id')
        emojiPickerPosts.$panel.show()
    })
      
    //event listener for the comments links on each post
    $(".comments-link").click(function(event) {
        event.preventDefault();
        let url = event.target.href
        getRequestToDjamgo('#post-comments', url)

        if(window.innerWidth < 575){
            $('#channel-posts').toggleClass('d-flex');
            $('.back-btn').removeClass('d-none')
        }
        $('#post-comments').addClass('d-flex');
    });

    //add user form event listener
    $("#add-user-form").submit(function(event) {
        event.preventDefault();
        //get csrf token from the form
        let csrftoken = $(this).find('input[name="csrfmiddlewaretoken"]').val();
        let url = $(this).attr('action');
        // function in home.js to send post request to add user
        addUserPostRequest(url, csrftoken);
    });

    
    //scroll to bottom of the posts
    $('#channel-posts .scrollable-div').animate({ scrollTop: $('.scrollable-div')[1].scrollHeight }, 'fast');

    initializeEmojiPicker();

}


// add user to channel
function addUserPostRequest(url, csrftoken){
    // AJAX request
    $.ajax({
        type: "POST",
        url: url,
        headers: {
            'X-CSRFToken': csrftoken
        },
        success: function(response) {
            $('#overlay').addClass('d-none')
            displayMessage(response)
        },
        error: function(error) {
            displayMessage(error)
        }
    });
}


// emoji call back function when user choose emoji
function emojiPickerCallback(emoji) {
    let newEmojiPostUrl = emojiPostUrl.replace('0', postId)
    let emojiColonName = emoji.alt
    
    postRequestToDjamgo(newEmojiPostUrl, emojiColonName, postId,emoji)
   
}



// function to load posts
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

// function for adding and removing emoji on posts
function postRequestToDjamgo(url, emojiColonName, args, emoji){
    var id = url.match(/\d+/g);
    let spanElement = $(args).find('span');
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

                    let emojiUlClass = `.emoji-list${args}`
                    let em = $(emoji).prop('outerHTML');

                    let newLi = $(`
                        <li class="list-inline-item mr-2">
                            <button class="added-emoji-btn btn" data-post-url="${url}" 
                                    data-post-emoji-list=".emoji-list${id}"  
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
///////////////////////////////  initialize channels list listeners ////////////////////////////
function initChannels(){

    // Toggle the visibility of the messages list when the button is clicked
    $('.toggleLinksButton').click(function() {
        var target = $(this).data('target');

        $(target).toggleClass('d-none')
        $(this).find('i').toggleClass('fa-rotate-90');

    });

    // Use the ready function to execute code when the DOM is fully loaded
    // Click event for the button
    $(".channel-link").click(function(event) {
        event.preventDefault();
        $(this).find('.unread-indicator').remove()
        url = event.currentTarget.href
        getRequestToDjamgo('#channel-posts', url)
        if(window.innerWidth < 575){
            $('#channel-posts').toggleClass('d-flex');
            $('#channel-links-container').toggleClass('hide');
            $('#nav-bar').addClass('d-none')
            $('header').addClass('d-none')

        }
        $('#post-comments').removeClass('d-flex');
    });
}



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



/////////////////////// function for notification messages ///////////////////////////////
let isAnimationInProgress = false;

function displayMessage(response){     
    // Check if the animation is already in progress
    if (isAnimationInProgress) {
        return;
    } 

    isAnimationInProgress = true;
    let notification = $('.notification')
    $('.messages').removeClass('d-none')
    $(`.notification .${response.status}`).removeClass('d-none')
    notification.addClass('notification-keyframe-start')
    let animationEndHandled = false;

    
    setTimeout(function() {        
        notification.removeClass('notification-keyframe-start')
        notification.addClass('notification-keyframe-finish')

        notification.on('animationend webkitAnimationEnd oAnimationEnd', function() {
            if (!animationEndHandled) {

            $('.messages').addClass('d-none')
            notification.removeClass('notification-keyframe-finish')

            notification.off('animationend webkitAnimationEnd oAnimationEnd', this);
            $(`.notification .${response.status}`).addClass('d-none')         

            // Reset animation state       
            isAnimationInProgress = false;
            animationEndHandled = true;


            }
        });
    }, 5000);
}