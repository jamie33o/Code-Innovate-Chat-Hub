let csrfToken = null;
let msgToBeDel = null;
let deleteUrl = null;
let deleteModelBody = null;
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

// // event listener for the delete button on post and comments
// $(document).on('click', '.delete-btn', function() {
//     let deleteUrl = $(this).data('delete-url')
//     let msgToBeDel = $(this).closest('.message');
//     deleteObject(deleteUrl, msgToBeDel, 'message', '.messaging')
// });

// // listener for edit button on posts and comments dropdown menu
// $('main').on('click', '.edit-btn', function(event) {
//     // cancel any other post that is in edit mode
//     if($('.cancel-edit').length > 0){
//         $('.cancel-edit').click()
//     }else if($('.edit-post').length > 0 ){
//         $('.card.edit-post').removeClass('edit-post')
//     }
//     // Find the closest ancestor with the class 'card'
//     var card = $(this).closest('.card');
//     let carbody = card.find('.card-body').html()
//     let cardText = card.find('.card-text').html();
//     let cardImages = card.find('.post-images').html()
//     card.addClass('edit-post')
//     let postId = card.data("post-id")
//     let editPostUrl = card.data('post-url')
//     card.find('.card-body').html('')
//     // Append the HTML structure to the body
//     editPostUrl += postId + '/'
//     summernoteEnhancerEditPost.init('.edit-post .card-body', editPostUrl, csrfToken)
    

//     summernoteEnhancerEditPost.addToSummernoteeditorField(cardText)

//     $('.edit-post .summernote-btn-bottom .cancel-submit').prepend('<button class="cancel-edit">Cancel</button>');
    
//     $('main').on('click', '.cancel-edit', function(event) {
//         event.preventDefault()
//         $('.edit-post .card-body').html(carbody)
//         $('.card.edit-post').removeClass('edit-post')
//     })

//     if(cardImages){
//         $(cardImages).each(function () {
//         let src = $(this).attr('src');
//         if(src != undefined){
//             summernoteEnhancerEditPost.addimageToSummernote(src)
//         }
//         }); 
//     }
// });



