class SummernoteEnhancer {

  static sharedChannelUsers= [];
  static emojiImgs = null;

  constructor() {
    this.divToLoadIn = null;
    this.$sn = null;  // Initialize as null
    this.snSubmitForm = null;
    this.djangoUrl = null
    this.snForm = null;
    this.divsection = null;
    this.$storeText = null;
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
          }
        }

    });
    this.snSubmitForm = $(`${this.divToLoadIn} .sn-submit-btn`)
    this.snForm = $(`${this.divToLoadIn} .sn-form`)

    this.snSubmitForm.click((event) => {
            event.preventDefault();
            this.submitForm(this.djangoUrl);
        });

    this.divsection = $(this.divToLoadIn)

    //@ symbol event listener
    $(`${this.divToLoadIn} .at-symbol`).click(() => {
      let atSymbol = document.createTextNode(`@`);
      this.$sn.summernote(`editor.insertNode`, atSymbol);

      this.tagUser();      

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
    // Serialize the form data
    const formData = this.snForm.serialize();
     // Preserve the reference to the class instance
     const self = this;
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


}

const summernoteEnhancerPosts = new SummernoteEnhancer();
const summernoteEnhancerComments = new SummernoteEnhancer();


