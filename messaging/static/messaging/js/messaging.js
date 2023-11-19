// ////////////////////////////// inbox functionality ////////////////////////////
$()
        $('#messages-list-container').on('click', '.close-messages-btn', function(e){
            $('.inbox-container').removeClass('d-none')
            $('#messages-list-container').addClass('d-none')
            $('#messages-list-container').removeClass('d-flex')

            $('#nav-bar').removeClass('d-none')
            $('header').removeClass('d-none')
        })
        $('.inbox-container').on('click', '.message-link', function(e){
            e.preventDefault()
            let url = $(this).data('url')

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