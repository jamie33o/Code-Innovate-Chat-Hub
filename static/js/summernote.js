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



  init(divToLoadIn, djangoUrl) {
    let self = this;
    this.divToLoadIn = divToLoadIn
    this.djangoUrl = djangoUrl
    this.$sn = $(`${this.divToLoadIn} textarea`);  



    document.emojiSource = SummernoteEnhancer.emojiImgs;


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
        }

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
      emojiPicker.$panel.hide();
    });

    let emojiPicker = new EmojiPicker(this.divToLoadIn, function(emoji){
        self.$sn.summernote('editor.insertNode', emoji);
        $(`${self.divToLoadIn} .hide-modal`).hide()
    });

    // Add this code to bind the click event of your existing button
    $(`${this.divToLoadIn} .emoji-popup-btn`).on('click', function () {      
      $(`${self.divToLoadIn} .hide-modal`).show()

      emojiPicker.$panel.show();
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
          // Replace the typed text with the selected name
          event.preventDefault()

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
    $.each(self.uploadImageUrls, function(index, url) {
      formData += `&urls[]=${encodeURIComponent(url)}`;
  });
    // Preserve the reference to the class instance
    // Send the form data to Django
    $.ajax({
        url: djangoUrl,  // Replace with your Django view URL
        type: 'POST',
        data: formData,
        success: function(response) {
            // Handle success
            self.divsection.html(response)
        },
        error: function(error) {
            // Handle errors
            console.log(error);
        }
    });

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
         
          $('#channel-posts div.note-editing-area').append('<img src="' + response.url + '" alt="Uploaded Image">');
          self.uploadImageUrls.push(response.url)
         
          self.$sn.summernote('focus');

        },
        error: function(error) {
          console.error("Error uploading image:", error);
        }
      });
    }


}

const summernoteEnhancerPosts = new SummernoteEnhancer();
const summernoteEnhancerComments = new SummernoteEnhancer();


