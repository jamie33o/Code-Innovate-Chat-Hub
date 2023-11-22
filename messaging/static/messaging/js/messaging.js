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
