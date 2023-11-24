let csrfToken = null;
let msgToBeDel = null;
let deleteUrl = null;
let deleteModelBody = null;
let emojiPicker = new EmojiPicker()
// ////////////////////////////// inbox functionality ////////////////////////////

$('#messages-list-container').on('click', '.close-messages-btn', function(e){
    $('.inbox-container').removeClass('d-none')
    $('#messages-list-container').addClass('d-none')
    $('#messages-list-container').removeClass('d-flex')

    $('#nav-bar').removeClass('d-none')
    $('header').removeClass('d-none')
})
$('.inbox-container').on('click', '.message-link', function(e){
    e.preventDefault()
    let url = $(this).closest('.message-link').data('url')
    $('.message-link').removeClass('active')
    $(this).addClass('active')

    ajaxRequest(url, null, 'GET', '#messages-list-container', null, function(response){
        $('#messages-list-container').html(response)
        //autoScroll()
        if(window.innerWidth < 575){
            $('.inbox-container').addClass('d-none')
            $('#messages-list-container').removeClass('d-none')
            $('#messages-list-container').addClass('d-flex')
            $('#nav-bar').addClass('d-none')
            $('header').addClass('d-none')
        }
    })
})

$('.inbox-container').on('click', '.delete-conversation', function(e){
    const url = $(this).data('url')
    const csrfToken = $(this).data('csrf-token')

    let users_name = $(this).closest("li").find("h3").text();

    let header = `<h3>Are you sure you want to delete your conversation with ${users_name}</h3>`
    let body = `
        <form>
            <div class="input-group text-center d-flex justify-content-between">
                <button type="button" class="btn btn-oval btn-info" 
                data-dismiss="modal" aria-label="Close">No</button>

                <button id="yes-btn" 
                class="btn btn-oval btn-info" data-dismiss="modal" 
                type="button">Yes</button>
            </div>
        </form>`;
            
    showModal(header, body)

    $('body').on('click', '#yes-btn', function(e){
         ajaxRequest(url, csrfToken, 'DELETE', '.messaging', null) 
    })

})

// event listener for the delete button on post and comments
$(document).on('click', '.delete-btn', function() {
    let deleteUrl = $(this).data('delete-url')
    let msgToBeDel = $(this).closest('.message');
    deleteObject(deleteUrl, msgToBeDel, 'message', '.messaging')
});

// listener for edit button on posts and comments dropdown menu
$('main').on('click', '.edit-btn', function(event) {
    // cancel any other post that is in edit mode
    if($('.cancel-edit').length > 0){
        $('.cancel-edit').click()
    }else if($('.edit-post').length > 0 ){
        $('.card.edit-post').removeClass('edit-post')
    }
    // Find the closest ancestor with the class 'card'
    var card = $(this).closest('.message');
    //let carbody = card.find('.message-body').html()
    let cardText = card.find('.message-text').html();
    let cardImages = card.find('.message-img').html()
    card.addClass('edit-post')
    let postId = card.data("post-id")
    let editPostUrl = card.data('url')
    card.find('.message-text').html('')
    card.find('.message-img').html('')
    // Append the HTML structure to the body
    
    summernoteEnhancerEditPost.init('.edit-post .message-text', editPostUrl, csrfToken)
    
    summernoteEnhancerEditPost.addToSummernoteeditorField(cardText)

    $('.edit-post .summernote-btn-bottom .cancel-submit').prepend('<button class="cancel-edit">Cancel</button>');
    
    $('main').on('click', '.cancel-edit', function(event) {
        event.preventDefault()
        $('.edit-post .message-text').html(cardText)
        $('.edit-post .message-img').html(cardImages)
        $('.message').removeClass('edit-post')
    })

    if(cardImages){
        $(cardImages).each(function () {
        let src = $(this).attr('src');
        if(src != undefined){
            summernoteEnhancerEditPost.addimageToSummernote(src)
        }
        }); 
    }
});




///////////////// Emoji functionality //////////////////////
// event listener for the emoji button on posts and comments
$('main').on('click', '.card-emoji-btn', function(event) {
    event.preventDefault()
    emojiUrl = $(this).data('emoji-url')
    emojiPicker.addListener(event, emojiPickerCallback) 
    emojiPicker.$panel.show() 
})

// event listener for emojis that are added to posts or comments
$('main').on({
    click: function(event) {
        event.preventDefault();
        const emojiCode = $(this).data('emoji-code')
        const url = $(this).data('emoji-url');
        const self = this;
        data = {
            emoji_colon_name: emojiCode,
        }
         // Send a post request to Django with the emoji information
    ajaxRequest(url, csrfToken, 'POST', 'main', data, function(response){
        updateEmoji(emojiCode, null, self, response, url)
    });
    },
    mouseenter: function() {
        if(window.innerWidth > 1111){
            $(this).css('cursor', 'pointer');
            $(this).siblings('.emoji-user-count-modal').removeClass('d-none');
        }
        
    },
    mouseleave: function() {
        if(window.innerWidth > 1111){
            $(this).css('cursor', 'pointer');
            $(this).siblings('.emoji-user-count-modal').addClass('d-none');
        }
    }
}, '.added-emoji-btn');

/**
 * Callback function triggered when a user clicks an emoji in the emoji picker.
 *
 * This function sends a post request to the Django server with the selected emoji's
 * information.
 *
 * @param {Object} emoji - The emoji object representing the clicked emoji.
 */
function emojiPickerCallback(emoji) {
    // Extract the emoji's colon name
    let emojiColonName = emoji.alt;
    let data = {
        emoji_colon_name: emojiColonName,
    }
    // Send a post request to Django with the emoji information
    ajaxRequest(emojiUrl, csrfToken, 'POST', 'main', data, function(response){
        console.log(response)

        updateEmoji(emojiColonName, emoji, null, response, emojiUrl)
    });
}

/**
 * Update Emoji function for handling the response and updating the emoji UI.
 *
 * @param {string} emojiColonName - The colon-style name of the emoji (e.g., ':smile:').
 * @param {string} emojiImg - The HTML representation of the emoji image.
 * @param {HTMLElement} clickedBtn - The button element that was clicked to trigger the update.
 * @param {object} response - The response object containing the status of the update.
 * @param {string} url - The URL associated with the emoji update.
 */
function updateEmoji(emojiColonName, emojiImg, clickedBtn, response, url) {
    let id = url.match(/\d+/g);
    let spanElement;
    let emojiUlClass = `.emoji-list${id}`
    const emojiClass = emojiColonName.slice(1,-1)
    if(clickedBtn){
        spanElement = $(clickedBtn).find('span');
    }
    let currentNumber = null
    // Handle success
    switch (response.status) {

        case "added":
            let em = $(emojiImg).prop('outerHTML');

            let newLi = $(`
                <li class="list-inline-item mr-2">
                    <button class="added-emoji-btn btn ${emojiClass}" data-emoji-url="${url}" 
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
                if (newNumber > 1) {
                    // Update the HTML content of the span element with the new number
                    spanElement.html(newNumber);
                } else {
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
            } else {
                spanElement.html(2);
            }

            break;
        case "removed":
                $(emojiUlClass).find(`.${emojiClass}`).parent().remove()
            
    }
    
}