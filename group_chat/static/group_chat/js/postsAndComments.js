// Variables
//url for adding or removing emojis
let emojiUrl = null;
// emoji picker class object
const emojiPicker = new EmojiPicker();
// url for loading older posts
let olderPostsUrl = null;
// boolean to check if user scrolled to top
let scrolledToTop = false;
// url to delete a post
let deleteUrl = null;
// outer html of the card class of post to be deleted
let cardBeingDeleted = null;
// small screen size breakpoint
const SM_BRAKE_POINT = 575.98;
// medium screen size breakpoint
const MD_BRAKE_POINT = 991.98;
// large screen size breakpoint
const LG_BRAKE_POINT = 1111.98;
// html form with csrf
let deleteModelBody = null;
let sizeFactor = 1;
let csrfToken = null;


////////////////////////// functions for posts ///////////////////////////////////


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

    // Send a post request to Django with the emoji information
    postRequestToDjango(emojiUrl, emojiColonName, null, emoji);
}

///////////////// event listeners ////////////////////////////

// event listener for the emoji button on posts and comments
$('main').on('click', '.card-emoji-btn', function(event) {
    event.preventDefault()
    emojiUrl = $(this).data('emoji-url')
    emojiPicker.addListener(event, emojiPickerCallback) 
    emojiPicker.$panel.show() 
})

// event listener for images 
$('main').on('click', '.post-images img', function(e) {
    let header =
        `<div class="buttons">
            <button type="button" class ="zoom-in">
                <i class="fa-solid fa-plus"></i>
            </button>
            <button type="button" class ="zoom-out">
                <i class="fa-solid fa-minus"></i>            
            </button>
        </div>
        <button type="button" class="close" data-dismiss="modal" 
            aria-label="Close"><span aria-hidden="true">×</span>
        </button>
        `;
    let img = $(e.currentTarget).clone()
    showModal(header, img)
    resizeImage(.5, $('#modal').find('img')[0]); // Increase size by 20%
})

// Event listener for the plus button
$('main').on('click', '.zoom-in', function() {
resizeImage(1.2, $('#modal').find('img')[0]); // Increase size by 20%
});

// Event listener for the minus button
$('main').on('click', '.zoom-out', function() {
resizeImage(0.8, $('#modal').find('img')[0]); // Decrease size by 20%
});

//event listener for the comments links on each post
$('main').on('click', '.comments-link', function(event) {
    event.preventDefault();
    let url = $(this).attr('href');  // Use $(this) to access the clicked element
    getRequestToDjango('#post-comments', url)

    if(window.innerWidth < LG_BRAKE_POINT){
        
        $('#channel-posts').removeClass('d-flex');
    }
    $('#post-comments').addClass('d-flex');
});

// button for hiding the comments list
$('main').on('click', '.comments-close-btn', function() {
    if(window.innerWidth < LG_BRAKE_POINT){
        $('#channel-posts').addClass('d-flex');
    }
    $('#post-comments').removeClass('d-flex');
    $('#post-comments').html('')
});

    // Click event for the x button to close posts 
$('main').on('click', '.posts-close-btn', function() {
    $('#channel-posts').removeClass('d-flex');
    $('#channel-links-container').removeClass('hide');
    $('#nav-bar').removeClass('d-none')
    $('header').removeClass('d-none')
});

// event listener for the add user button to 
// shows when user is not a channel member
$('main').on('submit', '#add-user-form', function(event) {
    event.preventDefault();
    //get csrf token from the form
    let csrftoken = $(this).find('input[name="csrfmiddlewaretoken"]').val();
    let url = $(this).attr('action');
    // function in home.js to send post request to add user
    addUserPostRequest(url, csrftoken);
});

// event listener for emojis that are added to posts or comments
$('main').on({
    click: function(event) {
        event.preventDefault();
        let emojiCode = $(this).data('emoji-code')
        let url = $(this).data('emoji-url');
        postRequestToDjango(url, emojiCode, this);
    },
    mouseenter: function() {
        if(window.innerWidth > LG_BRAKE_POINT){
            $(this).css('cursor', 'pointer');
            let emojiId = $(this).data('target');
            $(emojiId).removeClass('d-none');
        }
        
    },
    mouseleave: function() {
        if(window.innerWidth > LG_BRAKE_POINT){
            $(this).css('cursor', 'pointer');
            let emojiId = $(this).data('target');
            $(emojiId).addClass('d-none');
        }
    }
}, '.added-emoji-btn');

// event listener for the delete button on post and comments
$(document).on('click', '.delete-btn', function() {
    // Get the URL of the image
    deleteUrl = $(this).data('delete-url')
    // Make AJAX delete request
    cardBeingDeleted = $(this).closest('.card');

    let header =
        `<h5 class="modal-title text-center">
        Are you sure you want to delete this post?
        </h5>`;
    
    // Clone cardBeingDeleted
    const clonedCard = cardBeingDeleted.clone();
    clonedCard.find('.dropdown-menu').removeClass('show')

    // Create an overlay div
    const overlay = $('<div id="cover"></div>');

    // Set its CSS properties
    overlay.css({
        'position': 'absolute',
        'top': '0',
        'left': '0',
        'width': '100%',
        'height': '100%',
        'z-index': '3', 
    });

    // Append the overlay to the body
    clonedCard.append(overlay);
    deleteModelBody = `
    <form>
        <input type="hidden" name="csrfmiddlewaretoken" id="csrf_token" value="${csrfToken}">

        <div class="input-group text-center d-flex justify-content-between">
            <button type="button" class="btn-oval" 
            data-dismiss="modal" aria-label="Close">No</button>

            <button id="yes-btn" 
            class="btn btn-oval" data-dismiss="modal" 
            type="button">Yes</button>
        </div>
    </form>`;
    let body = $(deleteModelBody).prepend(clonedCard)
            
    showModal(header, body)

    });

// event listener for yes-btn on the delete post/comment card modal
$(document).on('click', '#yes-btn', function(event) {
    event.preventDefault()   
    let csrfToken = $(this).closest('form').find('input[name="csrfmiddlewaretoken"]').val();
    cardBeingDeleted.remove();
    deleteObject(deleteUrl, csrfToken)
})

// event listener for save post btn on posts dropdown menu
$('main').on('click', '.save-post-btn', function(event) {
    event.preventDefault()
    let savePostUrl = $(this).data('save-post-url');

    $.ajax({
        type: 'POST',
        url: savePostUrl,
        headers: {'X-CSRFToken': csrfToken},      
        success: function(response) {
            displayMessage(response, '#channel-posts')
        },
        error: function(error) {
            // Handle error, e.g., display an error message
            displayMessage(error)
        }
    });   
})

$('main').on('click', '.edit-btn', function(event) {
    if($('.cancel-edit').length > 0){
        $('.cancel-edit').click()
    }else if($('.edit-post').length > 0 ){
        console.log('work')
        $('.card.edit-post').removeClass('edit-post')
    }
    // Find the closest ancestor with the class 'card-body'
    var card = $(this).closest('.card');
    let carbody = card.find('.card-body').html()
    let cardText = card.find('.card-text').html();
    let cardImages = card.find('.post-images').html()
    card.addClass('edit-post')
    let postId = card.data("post-id")
    let editPostUrl = card.data('post-url')
    card.find('.card-body').html('')
    // Append the HTML structure to the body
    editPostUrl += postId + '/'
    summernoteEnhancerEditPost.init('.edit-post .card-body', editPostUrl, csrfToken)
    

    summernoteEnhancerEditPost.addToSummernoteeditorField(cardText)

    $('.edit-post .summernote-btn-bottom .cancel-submit').prepend('<button style=" border-radius: 20px; border: 1px solid black;" class="cancel-edit px-1">cancel</button>');
    
    $('main').on('click', '.cancel-edit', function(event) {
        event.preventDefault()
        $('.edit-post .card-body').html(carbody)
        $('.card.edit-post').removeClass('edit-post')
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

function loadOldPosts(){
    // Attach scroll event to load older posts when scrolling to the top
    if ($(this).scrollTop() === 0 && !scrolledToTop && olderPostsUrl != null) {
        scrolledToTop = true;

        $.ajax({
            type: "GET",
            url: olderPostsUrl,
            success: function(response) {
                // Update the div with the returned template
                $('#posts-list').prepend(response)
                scrollTo()
                scrolledToTop = false;
            },
            error: function(error) {
                displayMessage(response={status:'error', message: error.statusText},'#channel-posts')
            }
        });
    }    
}

function scrollTo(){
    //get the post count
    let postCount = $('#channel-posts .scrollable-div .card').length;
    //get the index of the last post before the older posts being appended
    let postAtIndex = $('#channel-posts .scrollable-div .card').eq(9); 

    // scroll to post at index above if there are more 10 else scroll to bottom
    if (postCount > 10) {
        // Scroll to the 10th post
        $('#channel-posts .scrollable-div').animate({ scrollTop: postAtIndex.offset().top }, 'fast');
    } else {
        $('#channel-posts .scrollable-div').animate({ scrollTop: $('.scrollable-div')[1].scrollHeight }, 'fast');
    }
}

 // Function to resize the image for zooming in and out
 function resizeImage(factor, imgElement) {
    // Update the size factor
    sizeFactor *= factor;
    // Apply the new size to the image
    $(imgElement).css('width', 100 * sizeFactor + '%');
  }


  function showModal(header, body,) {
    // Check if the modal already exists
    let modal = $('#modal');
    if (modal.length === 0) {
        // If not, create the modal element
        modal = $(`
            <div class="modal fade modal" id="modal" tabindex="-1" role="dialog" aria-labelledby="model" aria-hidden="true">
                <div class="modal-dialog modal-div " role="document">
                    <div class="modal-content mt-5 ">
                        <div class="modal-header"></div>
                        <div class="modal-body scrollable-div"></div>
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
