
const tagNameModal = $("#tag-name-modal");
  


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
          console.log(data)
      })
      .fail(function(jqXHR, textStatus, errorThrown) {
          console.error('There was a problem with the AJAX request:', errorThrown);
      });
  });
