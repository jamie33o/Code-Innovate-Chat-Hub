class SummernoteEnhancer {

  static sharedChannelUsers= [];
  static emojiImgs = null;
  static imgUrl = null;

  constructor() {
    this.divToLoadIn = null;
    this.$sn = null;  // Initialize as null
    this.snSubmitForm = null;
    this.djangoUrl = null
    this.snForm = null;
    this.divsection = null;
    this.$storeText = null;
    this.uploadImageUrls = [];
  }



  init(divToLoadIn, djangoUrl, csrf_token) {
    let self = this;
    this.divToLoadIn = divToLoadIn
    this.djangoUrl = djangoUrl
    let emojiPicker = new EmojiPicker()



    let htmlStructure = `
      <!-- Container for summernote editor -->
      <div class="summernote-form mb-2 px-2">
          <!-- Container for usernames list that the user can tag with @ -->
          <div class="tag-name-modal popup">
              <ul class="channel-users d-flex flex-column ml-3 my-3"></ul>
          </div>

          <!-- Summernote editor form -->
          <form class="sn-form" method="post">
              
              <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">

              <textarea name="post"></textarea>

              <!-- Buttons at the bottom of summernote editor emoji,@ and arrow for posting -->
              <div class="summernote-btn-bottom">   
                  <div>  
                      <button class="mx-3 mt-1 emoji-popup-btn" type="button">
                          <span class="fa-regular fa-face-smile fa-lg emoji-btn" style="color: var(--ci-orange);"></span>
                      </button>
                      <button class="mx-3 at-symbol" type="button">
                          <span class="fa-solid fa-at fa-lg" style="color: var(--ci-orange);"></span>
                      </button>
                  </div>
                  <div class="cancel-submit">   

                      <button class="post-arrow-btn mx-3 sn-submit-btn" type="submit">
                          <span class="fa-solid fa-play fa-lg" style="color: var(--ci-orange);"></span>
                      </button>
                  </div>
              </div>
          </form>
      </div>
  `;
    $(divToLoadIn).append($(htmlStructure))

    this.$sn = $(`${this.divToLoadIn} textarea`);  


    this.$sn.summernote({
      toolbar: [
          ['style', ['bold', 'italic', 'strikethrough', 'underline']],
          ['para', ['ul', 'ol', 'paragraph']],
          ['insert', ['link', 'picture']],
          ['misc', ['codeview', 'undo', 'redo']],
      ],
      width: '100%',
      attachment_require_authentication: true,
      placeholder: 'Type @ to get a list of people you can tag',
      focus: true,
      callbacks: {
          onInit: function () {
              // Attach an input event handler to the Summernote editor
              self.$sn.next().find('.note-editable').on('input', function () {
                  self.tagUser(false);
              });
          },
          // image upload callback 
          onImageUpload: function(files) {
            self.uploadImage(files[0],self.$sn);
          }
        },  

    });


    // summernote submit button
    this.snSubmitForm = $(`${this.divToLoadIn} .sn-submit-btn`)
    // summernote form 
    this.snForm = $(`${this.divToLoadIn} .sn-form`)
    // submit btn listener
    this.snSubmitForm.click((event) => {
      event.preventDefault();
      // Check if the content is empty or meets your criteria
      let $summernoteContent = self.$sn.summernote('code');
      let tempDiv = $('<div>');
      tempDiv.html($summernoteContent);
      
      let plainText = tempDiv.text().trim();
      if (!plainText) {
        displayMessage({'status': 'summernote-error'})
      }else{
        this.submitForm(self.djangoUrl);
      }
  });

    this.divsection = $(this.divToLoadIn)

    //@ symbol event listener
    $(`${this.divToLoadIn} .at-symbol`).click(() => {
      let atSymbol = document.createTextNode(`@`);
      this.$sn.summernote(`editor.insertNode`, atSymbol);

      this.tagUser();      

    });
    // fading summerote buttons
    $(`${divToLoadIn} .note-editable`).on('focus', function() {
        $(`${divToLoadIn} .btn-group button, ${divToLoadIn} .note-placeholder, ${divToLoadIn} .note-toolbar`).removeClass('faded');
    });

    $(`${this.divToLoadIn} .note-editable`).on('blur', function() {
        $(`${divToLoadIn} .btn-group button, ${divToLoadIn} .note-placeholder, ${divToLoadIn} .note-toolbar`).addClass('faded');

    });

    //overlay event listener to close modals
    $(`${this.divToLoadIn} .hide-modal`).click(() => {
      $(`${this.divToLoadIn} .tag-name-modal`).hide();
      $(`${this.divToLoadIn} .hide-modal`).hide();
    });


    // Add this code to bind the click event of existing button
    $(`${this.divToLoadIn} .emoji-popup-btn`).on('click', function () {      
      $(`${self.divToLoadIn} .hide-modal`).show()
      emojiPicker.addListener(function(emoji){
        self.$sn.summernote('editor.insertNode', emoji);
        $(`${self.divToLoadIn} .hide-modal`).hide()
    });
      emojiPicker.$panel.show();
    });

    $(document).on('click', '.delete-img-icon', function() {
      // Get the URL of the image
      let url = $(this).parent().find('img').attr('src');
 
      // Iterate over each element in the array
      self.uploadImageUrls.forEach(function(uploadedImg, index) {
         if (uploadedImg === url) {
             // Remove the element at the corresponding index
             self.uploadImageUrls.splice(index, 1);
         }
      })
        // Remove the parent element
      $(this).parent().remove();
    });

  }

  tagUser() {
    
    let nameSuggestions = SummernoteEnhancer.sharedChannelUsers;
    let $snText = $('<p>').html(this.$sn.summernote('code')).text();
    
    if($snText.includes('@')){
      let atIndex = $snText.lastIndexOf("@");
      // Check if "@" was the last character entered and the character before it is not a letter or symbol
      if ($snText.endsWith('@') && !/[A-Za-z\d]/.test($snText.slice(atIndex -1, atIndex))) {
          $(`${this.divToLoadIn} .tag-name-modal`).show()

          $(`${this.divToLoadIn} .hide-modal`).show()
      }
      $(`${this.divToLoadIn} .channel-users`).empty()

      const searchText = $snText.slice(atIndex + 1);

      const matchingNames = nameSuggestions.filter(name =>
        name.toLowerCase().startsWith(searchText.toLowerCase())
      );

      // Display matching names as suggestions
      $.each(matchingNames, (index, name) => {

        const suggestion = $('<a>', {
          href: '#',
          text: '@ ' + name
        });
        suggestion.on("click", (event) => {
          event.preventDefault()
          // Replace the typed text with the selected name

          this.$sn.summernote(`editor.insertNode`, suggestion[0]);

          $(`${this.divToLoadIn} .tag-name-modal`).hide()

          $(`${this.divToLoadIn} .hide-modal`).hide()

        });

        $(`${this.divToLoadIn} .channel-users`).append(suggestion);
      });
    }
  }

  submitForm(djangoUrl){
    const self = this;
    // Serialize the form data
    let formData = this.snForm.serialize();
    console.log(self.uploadImageUrls)
    if(self.uploadImageUrls.length > 0 ){ // Loop through each URL in uploadImageUrls

      $.each(self.uploadImageUrls, function(index, url) {
          // Check if the URL is not already present in the form data
          if (formData.indexOf(encodeURIComponent(url)) === -1) {
              // Append the URL to the form data
              formData += `&urls[]=${encodeURIComponent(url)}`;
          }
      });
    }

   
    // Send the form data to Django
    $.ajax({
        url: djangoUrl, 
        type: 'POST',
        data: formData,
        success: function(response) {
          if(response.status){
            let postBody = $('<div class="card-body">' +
            '<p class="card-text">' +
                response.post +
            '</p>' +
            '<div class="post-images">' +
            '</div>' +
            '</div>');
            if(response.images){

              let imagesArray = response.images.split(',');

              if(imagesArray.length >= 1){
                  imagesArray.forEach(function(imageUrl) {
                  postBody.find('.post-images').append(`<img src="${imageUrl}" alt="Post Image">`);
                });
              }else if(imagesArray.length > 0){

                postBody.find('.post-images').append(`<img src="${response.images}" alt="Post Image">`)
              }

            }
            self.divsection.html(postBody)
            displayMessage(response);

          }else{
              self.divsection.html(response)
          }
        },
        error: function(error) {
            // Handle errors
            console.log(error);
        }
    });
    self.uploadImageUrls = []

  }
  addToSummernoteeditorField(content){
    this.$sn.summernote('code', content);
  }

  addimageToSummernote(src){
    this.uploadImageUrls.push(src)
    // Append the image and icon to the specified container
    $(`${this.divToLoadIn} div.note-editing-area`).append(`
      <div class="sn-img">
        <i class="fa-solid fa-x position-absolute delete-img-icon"></i>
        <img src="${src}"  alt="Uploaded Image">
      </div>
    `);    
    
  }


  uploadImage(file, editor, welEditable) {
      // Create a FormData object to send the file to the server
      var formData = new FormData();
      formData.append("file", file);
      let self = this
  
      // Send the file to the server using AJAX
      $.ajax({
        data: formData,
        type: "POST",
        url: 'upload-image/',  
        cache: false,
        contentType: false,
        processData: false,
        success: function(response) {
          self.addimageToSummernote(response.url)         

        },
        error: function(error) {
          console.error("Error uploading image:", error);
        }
      });
    }


}

const summernoteEnhancerPosts = new SummernoteEnhancer();
const summernoteEnhancerComments = new SummernoteEnhancer();
const summernoteEnhancerEditPost = new SummernoteEnhancer();


