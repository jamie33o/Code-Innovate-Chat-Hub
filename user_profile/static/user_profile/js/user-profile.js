$(document).ready(function () {

    $('body').on('click', '.edit-profile-btn', function () {
        $('.update_profile_container').removeClass('d-none')
        $('.profile-container').addClass('d-none')
        $('#nav-bar').addClass('d-none')
        $('header').addClass('d-none')
    });

    $('body').on('click', '.close-edit-profile-btn', function () {
        $('.update_profile_container').addClass('d-none')
        $('.profile-container').removeClass('d-none')
        $('#nav-bar').removeClass('d-none')
        $('header').removeClass('d-none')
    });

    $('body').on('click', '.view-save-posts-btn', function () {
        $('.saved-posts-container').removeClass('d-none')
        if (window.innerWidth < 575.98) {
            $('.profile-container').addClass('d-none')
            $('#nav-bar').addClass('d-none')
            $('header').addClass('d-none')
        }
    });

    $('body').on('click', '.saved-posts-close-btn', function () {
        $('.saved-posts-container').addClass('d-none')
        if (window.innerWidth < 575.98) {
            $('.profile-container').removeClass('d-none')
            $('#nav-bar').removeClass('d-none')
            $('header').removeClass('d-none')
        }
    });

    $('.saved-posts-container').on('click', '.remove-post-btn', function(e){
        e.preventDefault()
        let url = $(this).data('url')
        let csrf = $(this).data('csrf')
        let post = $(this).closest('.card')
        ajaxRequest(url, csrf, 'POST', '.saved-posts-container', null, function(response){
            displayMessage(response, '.saved-posts-container')
            post.remove()

        })
    })

    $('body').on('change', '#id_profile_picture', function () {
        console.log("Event triggered!");
        var selectedFile = event.target.files[0];

        if (selectedFile) {
            // Get a temporary URL for the selected file
            var imageURL = URL.createObjectURL(selectedFile);
            $('.modal-body .profile_pic').attr('src', imageURL)

            // Log or use the imageURL as needed
            console.log("Image URL:", imageURL);
        }
    })
    $('body').on('click', '.sub-form', function () {
        event.preventDefault();

        let url = $(this).parent().data('url')
        var formData = new FormData($(this).closest('form')[0]);

        var csrfToken = $(this).find('input[name="csrf_token"]').val();



        ajaxRequest(url, csrfToken, 'Post', '.profile-container', formData, function (response) {
            if (response.status === 'success') {

                $('.status').html(`Current Status: ${response.message}`)
                displayMessage(response, '.profile-container');
                //$('#modal').hide()

            } else if (response.success === 'image') {
                $('.profile_pic').attr('src', response.message);
                displayMessage({ 'status': 'success', 'message': 'Profile picture updated' }, '.profile-container');

            } else {
                alert(`Error updating ${response.success}.`);
                console.log(response.errors);
            }
        })


    });




    $('.status-update-btn').on('click', function () {
        showModal('<h3>Update Your Status</h3>', statusModalBody)

    });



    $('.profile-img-modal').on('click', function () {
        showModal('<h3>Update Profile Picture</h3>', profileImgModal)
    })


});
