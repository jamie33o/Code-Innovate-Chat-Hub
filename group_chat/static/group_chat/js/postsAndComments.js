let channel_id = null;
// let postId = null;
// let comment_id = null;
let emojiUrl = null;
let url = null;
let emojiPicker = new EmojiPicker();
let olderPosts = null;
let scrolledToTop = false;
let tenthPost = null;
let htmlStructure = null;
let deletePostUrl = null;
let postBeingDeleted = null;
const SM_BRAKE_POINT = 575.98;
const LG_BRAKE_POINT = 991.98;
let deleteModelBody = null;
let sizeFactor = 1;
let csrfToken = null;


////////////////////////// functions for posts ///////////////////////////////////


// emoji call back function when user clicks emoji
function emojiPickerCallback(emoji) {
    let emojiColonName = emoji.alt
    postRequestToDjango(emojiUrl, emojiColonName, null, emoji)    
}

// function thats called from posts template when its loaded
function initPosts(){
    scrolledToTop = false;
    tenthPost = null

    $('#posts-list').scroll(function() {
        if ($(this).scrollTop() === 0 && !scrolledToTop && olderPosts != null) {
            scrolledToTop = true;

            $.ajax({
                type: "GET",
                url: olderPosts,
                success: function(response) {
                    // Update the div with the returned template
                    $('#posts-list').prepend(response)
                    initPosts()
                    scrolledToTop = false;

                },
                error: function(error) {
                    console.log("Error:", error);
                }
            });
        }    
    });

    $(document).on('click', '.card-emoji-btn', function(event) {
        event.preventDefault()
        emojiUrl = $(this).data('emoji-url')
        emojiPicker.addListener(event, emojiPickerCallback) 
         
        emojiPicker.$panel.show() 
    })
    
    //event listener for the comments links on each post
    $(".comments-link").click(function(event) {
        event.preventDefault();
        let url = $(this).attr('href');  // Use $(this) to access the clicked element
        getRequestToDjango('#post-comments', url)

        if(window.innerWidth < SM_BRAKE_POINT) {
            $('#channel-posts').toggleClass('d-flex');
        }else if(window.innerWidth < LG_BRAKE_POINT){
            $('#channel-posts').toggleClass('d-sm-flex');
        }
        $('#post-comments').addClass('d-flex');
    });

    // button for hiding the comments list
    $(document).on('click', '.comments-close-btn', function() {
        if(window.innerWidth < SM_BRAKE_POINT) {
            $('#channel-posts').toggleClass('d-flex');
        }else if(window.innerWidth < LG_BRAKE_POINT){
            $('#channel-posts').toggleClass('d-sm-flex');
        }
        $('#post-comments').removeClass('d-flex');
    });

    $(document).on('click', '.post-images img', function(e) {
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
    $(document).on('click', '.zoom-in', function() {
    resizeImage(1.2, $('#modal').find('img')[0]); // Increase size by 20%
    });

    // Event listener for the minus button
    $(document).on('click', '.zoom-out', function() {
    resizeImage(0.8, $('#modal').find('img')[0]); // Decrease size by 20%
    });


     // Click event for the close posts button
    $(".posts-close-btn").click(function(event) {
        $('#channel-posts').toggleClass('d-flex');
        $('#channel-links-container').toggleClass('hide');
        $('#nav-bar').removeClass('d-none')
        $('header').removeClass('d-none')
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

    //get the post count
    let postCount = $('.scrollable-div .card').length;
    // if post count can be divided by 10 then oldpostcount is ten if not oldpost count is the remainder
    let oldPostCount = postCount % 10 === 0 ? 10 : postCount % 10;
    //get the post at a older posts count index
    postAtIndex = $('.scrollable-div .card').eq(oldPostCount - 1); 
    
    // scroll to 1post at index above if there are more 10 else scroll to bottom
    if (postCount > 10) {
        // Scroll to the 10th post
        $('#channel-posts .scrollable-div').animate({ scrollTop: postAtIndex.offset().top }, 'fast');
    } else {
        $('#channel-posts .scrollable-div').animate({ scrollTop: $('.scrollable-div')[1].scrollHeight }, 'fast');
    }

    $(document).on({
        click: function(event) {
            event.preventDefault();
            let emojiCode = $(this).data('emoji-code')
            let url = $(this).data('emoji-url');
            postRequestToDjango(url, emojiCode, this);
        },
        mouseenter: function() {
            $(this).css('cursor', 'pointer');
            let emojiId = $(this).data('target');
            $(emojiId).removeClass('d-none');
        },
        mouseleave: function() {
            $(this).css('cursor', 'pointer');
            let emojiId = $(this).data('target');
            $(emojiId).addClass('d-none');
        }
    }, '.added-emoji-btn');

    $(document).on('click', '.delete-post-btn', function() {
        // Get the URL of the image
        deletePostUrl = $(this).data('delete-post-url')
        // Make AJAX delete request
        postBeingDeleted = $(this).closest('.card');

        let header =
            `<h5 class="modal-title text-center">
            Are you sure you want to delete this post?
            </h5>`;
        
                // Clone postBeingDeleted
        const clonedPost = postBeingDeleted.clone();
        clonedPost.find('.dropdown-menu').removeClass('show')

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
        clonedPost.append(overlay);
        let body = $(deleteModelBody).prepend(clonedPost)
                
        showModal(header, body)

      });

    $(document).on('click', '#delete-btn', function(event) {
        event.preventDefault()   
        let csrfToken = $(this).closest('form').find('input[name="csrfmiddlewaretoken"]').val();
        postBeingDeleted.remove();
        deleteObject(deletePostUrl, csrfToken)
    })

    $(document).on('click', '.save-post-btn', function(event) {
        event.preventDefault()
        let savePostUrl = $(this).data('save-post-url');

        $.ajax({
            type: 'POST',
            url: savePostUrl,    
            success: function(response) {
                // Handle success, e.g., redirect to success_url or update UI
                displayMessage(response)
            },
            error: function(error) {
                // Handle error, e.g., display an error message
                displayMessage(error)
            }
        });   
    })

    $(document).on('click', '.edit-btn', function(event) {

        // Find the closest ancestor with the class 'card-body'
        var card = $(this).closest('.card');
        let carbody = card.find('.card-body').html()
        let cardText = card.find('.card-text').html();
        let cardImages = card.find('.post-images').html()
        card.addClass('edit-post')
        let postId = card.data("post-id")
        let editPostUrl = card.data('post-url')

        // Append the HTML structure to the body
        editPostUrl += postId + '/'
        summernoteEnhancerEditPost.init('.edit-post .card-body', editPostUrl, csrfToken)
        summernoteEnhancerEditPost.addToSummernoteeditorField(cardText)

        $('.edit-post .summernote-btn-bottom .cancel-submit').prepend('<button style=" border-radius: 20px; border: 1px solid black;" class="cancel-edit px-1">cancel</button>');

        $('.cancel-edit').on('click', function(event){
            event.preventDefault()
            $('.edit-post .card-body').html(carbody)
        })

        if(cardImages){
            $(cardImages).each(function () {
            var src = $(this).attr('src');
            if(src != undefined){
                summernoteEnhancerEditPost.addimageToSummernote(src)
            }
            }); 
        }
    });

}

 // Function to resize the image
 function resizeImage(factor, imgElement) {
    // Update the size factor
    
    sizeFactor *= factor;

    // Apply the new size to the image
    $(imgElement).css('width', 100 * sizeFactor + '%');
    console.log(imgElement)

  }


  function showModal(header, body) {
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
