let channel_id = null;
let postId = null;
let emojiPostUrl = null;
let url = null
let emojiPickerPosts = null
let olderPosts = null
let scrolledToTop = false;
let tenthPost = null
let htmlStructure = null

////////////////////////// functions for posts ///////////////////////////////////
function initializeEmojiPicker() {
    // Your existing code for emojiPickerPosts
     emojiPickerPosts = new EmojiPicker('#for-emoji-picker', emojiPickerCallback);
}

// emoji call back function when user clicks emoji
function emojiPickerCallback(emoji) {
    let newEmojiPostUrl = emojiPostUrl.replace('0', postId)
    let emojiColonName = emoji.alt
    
    postRequestToDjango(newEmojiPostUrl, emojiColonName, postId,emoji)
   
}

// function thats called from posts template when its loaded
function initPosts(){
    scrolledToTop = false;
    tenthPost = null


    // Click event for the close posts button
    $(".posts-close-btn").click(function(event) {
        $('#channel-posts').toggleClass('d-flex');
        $('#channel-links-container').toggleClass('hide');
        $('#nav-bar').removeClass('d-none')
        $('header').removeClass('d-none')
    });

    $('#for-emoji-picker').scroll(function() {
        if ($(this).scrollTop() === 0 && !scrolledToTop && olderPosts != null) {
            scrolledToTop = true;

            $.ajax({
                type: "GET",
                url: olderPosts,
                success: function(response) {
                    // Update the div with the returned template
                    $('#for-emoji-picker').prepend(response)
                    initPosts()
                    scrolledToTop = false;

                },
                error: function(error) {
                    console.log("Error:", error);
                }
            });
        }    
    });

    $(".post-emoji-btn").click(function(event) {
        event.preventDefault()
        postId = $(this).data('post-id')
        emojiPickerPosts.$panel.show()
    })
   
    //event listener for the comments links on each post
    $(".comments-link").click(function(event) {
        event.preventDefault();
        let url = $(this).attr('href');  // Use $(this) to access the clicked element
        getRequestToDjango('#post-comments', url)

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
            let url = $(this).data('post-url');
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
        let postId = $(this).closest('.card').data('post-id');
        console.log(postId)
        postRequestToDjango()
       
          // Remove the parent element
        $(this).closest('.card').remove();
      });

    $(".edit-btn").click(function() {
        // Find the closest ancestor with the class 'card-body'
        var card = $(this).closest('.card');
        let cardText = card.find('.card-text').html();
        let cardImages = card.find('.post-images').html()
        card.addClass('edit-post')
        let postId = card.data("post-id")
        let editPostUrl = card.data('post-url')

            // Create the HTML structure
        $('.edit-post .card-body').html(htmlStructure)
        // Append the HTML structure to the body
        editPostUrl += postId + '/'
        summernoteEnhancerEditPost.init('.edit-post .card-body', editPostUrl)
        summernoteEnhancerEditPost.addToSummernoteeditorField(cardText)
        if(cardImages){
            console.log('home.js')
            $(cardImages).each(function () {
            var src = $(this).attr('src');
            if(src != undefined){
                summernoteEnhancerEditPost.addimageToSummernote(src)
            }
            }); 
        }

    });

    initializeEmojiPicker();


}
