let emojiUnicodeArray = [];
let emojisUnicodeCategory = [];
let summernoteEditor = null;


async function fetchCategoriesAndEmojis() {
  try {
    const categories = await $.ajax({
      url: 'https://emoji-api.com/categories?access_key=faf0432c18282e92ff66ea49f432dd40c35849a1',
      async: true,
    });

    for (const category of categories) {
      emojisUnicodeCategory = [];
      let counter = 0;

      const emojis = await $.ajax({
        url: `https://emoji-api.com/categories/${category.slug}?access_key=faf0432c18282e92ff66ea49f432dd40c35849a1`,
        async: true,
      });

      if (emojis != null && emojis.length > 0) {
        for (const emojiObject of emojis) {
          emojisUnicodeCategory.push(emojiObject.character);
          counter++;
          if (counter === 50) {
            break;
          }
        }

      }
      if (emojisUnicodeCategory.length > 0) {
        emojiUnicodeArray.push(emojisUnicodeCategory);
      }

    }
    summernoteEditor = $('div.note-editable.card-block');
    showEmojis()    
  } catch (error) {
    console.error('Error fetching data:', error);
  }
}

fetchCategoriesAndEmojis();


$('#emoji-popup-btn').click(function(){
        $(".popup").show()
        

});

// Unbind and rebind the click event to prevent multiple click handlers
$(document).off('click', '.emoji').on('click', '.emoji', addToTextField);

function showEmojis(){

    for(let i = 0; i<emojiUnicodeArray.length; i++){

            // Create a new <li> element
        let imgLi = $("<li>");

        let emojiUnicode = emojiUnicodeArray[i][0];
        
        emojiHeaderImageUrl = twemoji.parse(emojiUnicode);
        // Create a jQuery object from the HTML string
        const $emojiImage = $(emojiHeaderImageUrl);

        // Add a data attribute to the image element
        $emojiImage.attr('data-num', i);


        // Append the <img> element to the <li> element
        imgLi.append($emojiImage);
        

        // Append the <li> element to the '.emoji-Header' container
        $('.emoji-header').append(imgLi);
    }


        for(const emojiUnicode of emojiUnicodeArray[0]){
            let imgLi2 = $("<li>");
    
            let emojiBody = twemoji.parse(emojiUnicode);
    
            // Append the <img> element to the <li> element
            imgLi2.append(emojiBody);
    
            // Append the <li> element to the '.emoji-body' container
            $('.emoji-body').append(imgLi2);

    }
    summernoteEditor.html("")
    summernoteEditor.focus()
    
};



function addToTextField(event) {
        // Access the dataset.value property of the clicked element
        const num = parseInt(event.currentTarget.dataset.num);
        
        if (num >= 0 && num <= emojiUnicodeArray.length) {
           
            $('.emoji-body li').each(function(index) {

                // Create a new <img> element with the new image source
                let newImg = twemoji.parse(emojiUnicodeArray[num][index]);

                // Replace the existing <img> element with the new one
                $(this).find('img').replaceWith(newImg);
                
            });

        } else {
           
            // Insert the emoji at the cursor position
            let emojiImg = $(event.target).clone();
            summernoteEditor.append(emojiImg);

            // Move the cursor to the end of the summernote editor
            moveCursorToEndOfsummerNoteTextArea(summernoteEditor[0]);  
            //hide emoji pop up
            $(".popup").hide()  
        }

}

function moveCursorToEndOfsummerNoteTextArea(summerNoteTextArea) {
    const range = document.createRange();
    range.selectNodeContents(summerNoteTextArea);
    range.collapse(false); // Collapse the range to the end
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
}







// $(".summernote-div").summernote({
//     height: 100,
//     toolbar: false,
//     placeholder: 'type starting with : and any alphabet',
//     hint: {
//       match: /:([\-+\w]+)$/,
//       search: function (keyword, callback) {
//         callback($.grep(emojis, function (item) {
//           return item.indexOf(keyword)  === 0;
//         }));
//       },
//       template: function (item) {
//         var content = emojiUrls[item];
//         return '<img src="' + content + '" width="20" /> :' + item + ':';
//       },
//       content: function (item) {
//         var url = emojiUrls[item];
//         if (url) {
//           return $('<img />').attr('src', url).css('width', 20)[0];
//         }
//         return '';
//       }
//     }
//   });
  