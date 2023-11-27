/**
 * SummernoteEnhancer class for enhancing the functionality of Summernote editors in a web application.
 * This class provides methods to initialize, display, and handle events related to Summernote editors.
 *
 * Properties:
 * - sharedChannelUsers: Array containing shared channel user information.
 * - emojiImgs: Null or emoji images.
 * - imgUrl: Null or image URL.
 *
 * Methods:
 * - constructor(): Initializes class properties.
 * - init(divToLoadIn, djangoUrl, csrf_token): Initializes SummernoteEnhancer with the specified parameters.
 * - tagUser(): Tags a user in the Summernote editor.
 * - submitForm(djangoUrl): Submits the form data to Django.
 * - addToSummernoteeditorField(content): Adds content to the Summernote editor.
 * - addimageToSummernote(src): Adds an image to the Summernote editor.
 * - resizeEditor(): Adjusts the height of the editor.
 * - uploadImage(file, editor, welEditable): Uploads an image using AJAX.
 * - createForm(csrf_token): Creates the structure of the Summernote editor form.
 *
 * Instances:
 * - summernoteEnhancerPosts: Instance for handling Summernote editors in posts.
 * - summernoteEnhancerComments: Instance for handling Summernote editors in comments.
 * - summernoteEnhancerEditPost: Instance for handling Summernote editors in editing posts.
 */
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
    this.parentDiv = '';
  }

  /**
   * Initializes SummernoteEnhancer with the specified parameters.
   *
   * @param {string} divToLoadIn - The ID or class of the container where Summernote editor is loaded.
   * @param {string} djangoUrl - The Django URL for handling form submission.
   * @param {string} csrf_token - The CSRF token for form submission.
   */
  init(divToLoadIn, djangoUrl, csrf_token) {
    let self = this;
    this.divToLoadIn = divToLoadIn
    this.djangoUrl = djangoUrl
    let emojiPicker = new EmojiPicker()
    let counter = 0

    this.createForm(csrf_token)

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
              self.$sn.next().find('.note-editable').on('input', self.throttle(function (e) {
                // event Throttling function so function doesnt get called every time there is an input
                self.tagUser(false);
                self.parentDiv = $(e.target.lastChild.classList)                
            }, 300)); 
          
            
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
      
      tempDiv.find('img').each(function() {

        let altText = $(this).attr('alt');

        if (!altText.endsWith(":")) {
            altText = ":" + altText + ":";
            $(this).replaceWith(altText);
        }else{
          $(this).replaceWith($(this).attr('alt'));
        }
      });
      self.$sn.summernote('code', tempDiv.html());
    
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

    $(`${this.divToLoadIn} .add-image`).click(() => {
      $(`${this.divToLoadIn} .note-insert button`)[1].click();
    });

    $(`${this.divToLoadIn} .note-resizebar`).on('mousedown',() => {
      this.resizeEditor()
    });

    $(`${this.divToLoadIn} .note-toolbar button`).on('click',(e) => {
      e.preventDefault()
      $(e.currentTarget).addClass('btn-info');
    })

    $(`${this.divToLoadIn} .note-toolbar .note-misc button:first`).off().addClass('codeview')

    $(`${this.divToLoadIn}`).on('click', `.codeview`, function(e) {
      e.preventDefault()
      let txt = self.$sn.summernote('code')
      let txtContent = $(txt).text()
      let pElement = null
      if(self.parentDiv[0] === 'codeview-div'){
        pElement = $(`<p class="p-1"></p>`)[0]
        self.$sn.summernote('editor.insertNode', pElement);
        self.parentDiv = ''
      }else{
        if(txtContent.length === 0){
          pElement = $(`<p class="codeview-div p-2">${txtContent}</p>`)[0]
          self.$sn.summernote(`code`, pElement );
        }else{
          pElement = $(`<p class="codeview-div p-2"></p>`)[0]
          self.$sn.summernote(`editor.insertNode`, pElement );
        }
      }
      self.$sn.summernote(`focus`)
  })

    //overlay event listener to close modals
    $(`.hide-modal`).click(() => {
      $(`${this.divToLoadIn} .tag-name-modal`).hide();
      $(`.hide-modal`).hide();
    });


    // Add this code to bind the click event of existing button
    $(`${this.divToLoadIn} .emoji-popup-btn`).on('click', function (event) {      
      $(`.hide-modal`).show()
        emojiPicker.addListener(event, function(emoji){
        self.$sn.summernote('editor.insertNode', emoji);
        $(`.hide-modal`).hide()
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

  /**
   * Tags a user in the Summernote editor.
   */
  tagUser() {
    
    let nameSuggestions = SummernoteEnhancer.sharedChannelUsers;
    let $snText = $('<p>').html(this.$sn.summernote('code')).text();
    
    if($snText.includes('@')){
        let atIndex = $snText.lastIndexOf("@");
        // Check if "@" was the last character entered and the character before it is not a letter or symbol
        if ($snText.endsWith('@') && !/[A-Za-z\d]/.test($snText.slice(atIndex -1, atIndex))) {
            $(`${this.divToLoadIn} .tag-name-modal`).show()

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
            text: '@' + name
          });
          suggestion.on("click", (event) => {
            event.preventDefault()
            // Replace the typed text with the selected name

            this.$sn.summernote(`editor.insertNode`, suggestion[0]);

            $(`${this.divToLoadIn} .tag-name-modal`).hide()

            $(`${this.divToLoadIn} .note-editable p`).contents().filter(function() {
              return this.nodeType === 3 && /[^a-zA-Z0-9]@/.test(this.nodeValue);
          }).each(function() {
              const text = this.nodeValue.replace(/([^a-zA-Z0-9])@/g, '$1');
              $(this).replaceWith(document.createTextNode(text));
          });
        });
        $(`${this.divToLoadIn} .channel-users`).append(suggestion);
      });
    }
  }

  /**
   * Submits the form data to Django.
   *
   * @param {string} djangoUrl - The Django URL for handling form submission.
   */
  submitForm(djangoUrl){
    const self = this;
    // Serialize the form data
    let formData = this.snForm.serialize();
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
          self.$sn.summernote('code', "");
          $(`${self.divToLoadIn} div.note-editing-area .sn-img`).remove()

        },
        error: function(error) {
            // Handle errors
            console.log(error);
        }
    });
    self.uploadImageUrls = []

  }

  /**
   * Adds content to the Summernote editor.
   *
   * @param {string} content - The content to be added.
   */
  addToSummernoteeditorField(content){
    this.$sn.summernote('code', content);
  }

  /**
   * Adds an image to the Summernote editor.
   *
   * @param {string} src - The source URL of the image.
   */
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

  /**
   * Adjusts the height of the editor.
   */
  resizeEditor() {
      const fullScreen = 400
      if($('.note-editable').height() < fullScreen-30){
        $('.note-editable').css({height:` ${fullScreen}px`});
      }else {
        $('.note-editable').css({height:` 50px`});
      }
  }

  /**
   * Uploads an image using AJAX.
   *
   * @param {File} file - The image file to be uploaded.
   * @param {object} editor - The Summernote editor object.
   * @param {object} welEditable - The editable element in the editor.
   */
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
        headers: {
          'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value
        },
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
  /**
   * Creates the structure of the Summernote editor form.
   *
   * @param {string} csrf_token - The CSRF token for form submission.
   */
    createForm(csrf_token){
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

                  <div class="mb-2 ml-2">  
                      <button class="mx-1 add-image d-none" type="button">
                          <span class="fa-solid fa-plus fa-xl" style="color: var(--ci-orange);"></span>
                      </button>
                      <button class="mx-1 mt-1 emoji-popup-btn" type="button">
                          <span class="fa-regular fa-face-smile fa-xl emoji-btn" style="color: var(--ci-orange);"></span>
                      </button>
                      <button class="mx-1 at-symbol" type="button">
                          <span class="fa-solid fa-at fa-xl" style="color: var(--ci-orange);"></span>
                      </button>
                      
                  </div>
                  <div class="cancel-submit">   
  
                      <button class="post-arrow-btn mx-3 sn-submit-btn" type="submit">
                          <span class="fa-solid fa-play fa-xl" style="color: var(--ci-orange);"></span>
                      </button>
                  </div>
              </div>
          </form>
      </div>
      `;
      let $htmlStructure = $(htmlStructure);

      
  
    $(this.divToLoadIn).append($htmlStructure)  
       if(window.innerWidth < 575.98){ 
        $('.add-image').removeClass("d-none")
       }
    }


    throttle(func, delay) {
      let timer = null;
  
      return function () {
          const context = this;
          const args = arguments;
  
          if (!timer) {
              func.apply(context, args);
              timer = setTimeout(() => {
                  timer = null;
              }, delay);
          }
      };
  }
}
/**
 * Instance for handling Summernote editors in posts.
 */
const summernoteEnhancerPosts = new SummernoteEnhancer();
/**
 * Instance for handling Summernote editors in comments.
 */
const summernoteEnhancerComments = new SummernoteEnhancer();

/**
 * Instance for handling Summernote editors in editing posts.
 */
const summernoteEnhancerEditPost = new SummernoteEnhancer();


