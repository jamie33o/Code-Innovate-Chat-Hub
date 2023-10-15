class SummernoteEnhancer {

  static sharedChannelUsers= [];

  constructor() {
    this.divToLoadIn = null;
    this.emojiUnicodeArray = [];
    this.emojisUnicodeCategory = [];
    this.$sn = null;  // Initialize as null
    this.editor = null;
    this.editorNode = null;
    this.atTextNode = document.createTextNode('@');
    this.snSubmitForm = null;
    this.djangoUrl = null
    this.snForm = null;
    this.divsection = null;
    //this.init();
  }

  async fetchCategoriesAndEmojis() {
    try {
      const categories = await $.ajax({
        url: 'https://emoji-api.com/categories?access_key=faf0432c18282e92ff66ea49f432dd40c35849a1',
        async: true,
      });

      for (const category of categories) {
        this.emojisUnicodeCategory = [];
        let counter = 0;

        const emojis = await $.ajax({
          url: `https://emoji-api.com/categories/${category.slug}?access_key=faf0432c18282e92ff66ea49f432dd40c35849a1`,
          async: true,
        });

        if (emojis != null && emojis.length > 0) {
          for (const emojiObject of emojis) {
            this.emojisUnicodeCategory.push(emojiObject.character);
            counter++;
            if (counter === 50) {
              break;
            }
          }
        }

        if (this.emojisUnicodeCategory.length > 0) {
          this.emojiUnicodeArray.push(this.emojisUnicodeCategory);
        }
      }

      this.showEmojis();
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  }

  init(divToLoadIn,djangoUrl) {
    this.divToLoadIn = divToLoadIn
    this.djangoUrl = djangoUrl
    this.$sn = $(`${this.divToLoadIn} textarea`);  

    this.$sn.summernote({
      toolbar: [
          ['style', ['bold', 'italic', 'underline']],
          ['para', ['ul', 'ol', 'paragraph']],
          ['color', ['color']],
          ['insert', ['link', 'picture']],
          ['misc', ['codeview', 'undo', 'redo']],
      ],
      width: '100%',
      attachment_require_authentication: true,
      placeholder: 'Type @ to get a list of people you can tag',
      focus: true,
    //   callbacks: {
    //     onResize: function(content, $editable) {
    //         var newHeight = $editable.innerHeight();
    //         $sn.summernote('height', newHeight);
    //         console.log('working')
    //     }
    // }
    });
    this.snSubmitForm = $(`${this.divToLoadIn} .sn-submit-btn`)
    this.snForm = $(`${this.divToLoadIn} .sn-form`)

    this.snSubmitForm.click((event) => {
            event.preventDefault();
            this.submitForm(this.djangoUrl);
        });


    this.editor = $(`${this.divToLoadIn} div.note-editable`);
    this.editorNode = this.editor.get(0);

    this.divsection = $(this.divToLoadIn)
    this.fetchCategoriesAndEmojis();

    $(`${this.divToLoadIn} .emoji-popup-btn`).click(() => {
      $(`${this.divToLoadIn} .emoji-modal`).show();
      $(`${this.divToLoadIn} .hide-modal`).show();
    });

    $(document).off('click', `${this.divToLoadIn} .emoji`).on('click', `${this.divToLoadIn} .emoji`, this.addToTextField.bind(this));

    $(`${this.divToLoadIn} .at-symbol`).click(() => {
      this.insertNodeAtCursor(this.atTextNode);
      this.tagUser(true);
      this.moveCursorToEndOfsummerNoteTextArea(this.editor[0]);
      $(`${this.divToLoadIn} div.note-placeholder`).attr('style', 'none !important');
    });

    this.editor.on('input', () => {
      this.tagUser(false);
    });

    $(`${this.divToLoadIn} .hide-modal`).click(() => {
      $(`${this.divToLoadIn} .emoji-modal`).hide();
      $(`${this.divToLoadIn} .tag-name-modal`).hide();
      $(`${this.divToLoadIn} .hide-modal`).hide();
    });
    

  }

  showEmojis() {
    for (let i = 0; i < this.emojiUnicodeArray.length; i++) {
      // Create a new <li> element
      let imgLi = $("<li>");
      let emojiUnicode = this.emojiUnicodeArray[i][0];
      let emojiHeaderImageUrl = twemoji.parse(emojiUnicode);
      // Create a jQuery object from the HTML string
      const $emojiImage = $(emojiHeaderImageUrl);
      // Add a data attribute to the image element
      $emojiImage.attr('data-num', i);
      // Append the <img> element to the <li> element
      imgLi.append($emojiImage);
      // Append the <li> element to the '.emoji-Header' container
      $(`${this.divToLoadIn} .emoji-header`).append(imgLi);
    }

    for (const emojiUnicode of this.emojiUnicodeArray[0]) {
      let imgLi2 = $("<li>");
      let emojiBody = twemoji.parse(emojiUnicode);
      // Append the <img> element to the <li> element
      imgLi2.append(emojiBody);
      // Append the <li> element to the '.emoji-body' container
      $(`${this.divToLoadIn} .emoji-body`).append(imgLi2);
    }
  }

  addToTextField(event) {
    // Access the dataset.num property of the clicked element
    const num = parseInt(event.currentTarget.dataset.num);

    if (num >= 0 && num <= this.emojiUnicodeArray.length) {

      $(`${this.divToLoadIn} .emoji-body li`).each(function (index) {

        $(`${this.divToLoadIn} .emoji-body li`).each((index) => {
          const newImg = twemoji.parse(this.emojiUnicodeArray[num][index]);
          $(this).find('img').replaceWith(newImg);
      });

      });

    } else {
      // clone the img tag with the emoji link
      let emojiImg = $(event.target).clone();

      this.insertNodeAtCursor(emojiImg)

      // hide emoji pop up
      $(`${this.divToLoadIn} .popup, ${this.divToLoadIn} .hide-modal`).hide();

      // remove the placeholder from summernote when emoji added
      $(`${this.divToLoadIn} div.note-placeholder`).attr('style', 'none !important');
    }
  }

  insertNodeAtCursor(element) {
    // Get the current range
    let range = this.$sn.summernote('createRange');
    console.log(range);
    // Insert the HTML at the current cursor position
    range.insertNode($(element)[0]);
    range.collapse(true); // true collapses the range to the start
    this.moveCursorToEndOfsummerNoteTextArea(this.editorNode)
  }

  tagUser(btn_bool) {
    let nameSuggestions = SummernoteEnhancer.sharedChannelUsers;
    let $snText = this.editor.text();
    let atIndex = $snText.lastIndexOf("@");

    // Check if "@" was the last character entered and the character before it is not a letter or symbol
    if ($snText.slice(-1) === '@' & !/[A-Za-z\d]/.test($snText.slice(-2, -1)) || btn_bool) {
      $(`${this.divToLoadIn} .tag-name-modal`).show()

      $(`${this.divToLoadIn} .hide-modal`).show()
      $(`${this.divToLoadIn} div.note-placeholder`).attr('style', 'none !important');

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
        this.atTextNode.remove()
        this.insertNodeAtCursor(suggestion)

        this.moveCursorToEndOfsummerNoteTextArea(this.editorNode)

        $(`${this.divToLoadIn} .tag-name-modal`).hide()

        $(`${this.divToLoadIn} .hide-modal`).hide()
        $(`${this.divToLoadIn} div.note-placeholder`).attr('style', 'none !important');

      });

      $(`${this.divToLoadIn} .channel-users`).append(suggestion);
    });
  }

  moveCursorToEndOfsummerNoteTextArea(summerNoteTextArea) {
    const range = document.createRange();
    range.selectNodeContents(summerNoteTextArea);
    range.collapse(false); // Collapse the range to the end
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
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

