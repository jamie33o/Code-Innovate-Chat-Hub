class EmojiPicker {
    static emojiSource = null;

    constructor() {
        this.icons = {};
        this.reverseIcons = {};
        this.$panel = null;
        this.emojiClickedCallback = null; //  callback function to send emoji to summernote.js
        // Initialize the emoji panel
    }

    addListener(event, emojiClickedCallback) {
        if(this.$panel == null){
            this.emojiPanel();
        }
        this.setContainerPos(event)

        this.emojiClickedCallback = emojiClickedCallback
        const KEY_ESC = 27;
        const KEY_TAB = 9;

        const $body = $('body');
        const self = this;

        $body.on('keydown', function (e) {
            if (e.keyCode === KEY_ESC || e.keyCode === KEY_TAB) {
                self.$panel.hide();
            }
        });


        $body.on('click', `.emoji-menu .emoji-menu-tab`, function (e) {
            e.stopPropagation();
            e.preventDefault();
            let index = 0;
            let curclass = $(this).attr("class").split(' ');

            curclass = curclass[1].split('-');
            if (curclass.length === 3) return;

            curclass = curclass[0] + '-' + curclass[1];
            
            $(`.emoji-menu .emoji-menu-tabs td`).each(function (i) {
                const $a = $(this).find('a');
                let aclass = $a.attr("class").split(' ');

                aclass = aclass[1].split('-');
                aclass = aclass[0] + '-' + aclass[1];

                if (curclass === aclass) {
                    $a.attr('class', 'emoji-menu-tab ' + aclass + '-selected');
                    if(i<6)
                    index = i;

                } else {
                    $a.attr('class', 'emoji-menu-tab ' + aclass);
                }

            });
            self.updateEmojisList(index);
        });
        $(document).off('click', `.emoji-menu .emoji-items a`)
        
        $(document).on('click', `.close-modal`, function () {
            self.$panel.hide()
        })

        $(document).on('click', `.emoji-menu .emoji-items a`, function () {
            const emoji = $('.label', $(this)).text();
            const $img = $(self.createdEmojiIcon(self.icons[emoji]));

            if ($img[0].attachEvent) {
                $img[0].attachEvent('onresizestart', function (e) {
                    e.returnValue = false;
                }, false);
            }
            
            if (self.emojiClickedCallback) {
                self.emojiClickedCallback($img[0]);
            }
            self.$panel.hide();


            ConfigStorage.get('emojis_recent', function (curEmojis) {
                curEmojis = curEmojis || Config.defaultRecentEmojis || [];
                const pos = curEmojis.indexOf(emoji);

                if (!pos) {
                    return false;
                }

                if (pos !== -1) {
                    curEmojis.splice(pos, 1);
                }

                curEmojis.unshift(emoji);

                if (curEmojis.length > 42) {
                    curEmojis = curEmojis.slice(42);
                }

                ConfigStorage.set({
                    emojis_recent: curEmojis
                });
            });
        });
    }

    loadEmojis() {
        let icons = {};
        let reverseIcons = {};

        for (let j = 0; j < Config.EmojiCategories.length; j++) {
            const totalColumns = Config.EmojiCategorySpritesheetDimens[j][1];
            for (let i = 0; i < Config.EmojiCategories[j].length; i++) {
                const dataItem = Config.Emoji[Config.EmojiCategories[j][i]];
                const name = dataItem[1][0];
                const row = Math.floor(i / totalColumns);
                const column = i % totalColumns;
                icons[':' + name + ':'] = [j, row, column, ':' + name + ':'];
                reverseIcons[name] = dataItem[0];
            }
        }

        this.icons = icons;
        this.reverseIcons = reverseIcons;

        if (!Config.rx_codes) {
            Config.init_unified();
        }
    }
    setContainerPos(event){
        const emojiMenu = $('.emoji-menu-container');
        let offsetY = emojiMenu.height() /2 ;
        let topPosition = event.clientY - offsetY;
        const windowHeight = $(window).height();

        console.table([
            {
              window: windowHeight,
              'if state': event.clientY - emojiMenu.height(),
              even: event.clientY,
              offs: offsetY,
              eheigt : emojiMenu.height()
            }
          ]);
          

        // Check if there is enough space below the event, otherwise, position above
        if (event.clientY + offsetY > windowHeight) {
            topPosition = event.clientY - emojiMenu.height() -50;
        }else if(event.clientY - emojiMenu.height() < 0){
            topPosition = event.clientY - 10 ;
        }

        emojiMenu.css({
        top: topPosition,
        left: event.clientX +10
        });
    }

    updateEmojisList(index) {
        const $items = $(`.emoji-menu .emoji-items`);
        $items.html('');

        if (index > 0) {
            $.each(this.icons, (key, icon) => {     
                if (this.icons.hasOwnProperty(key) && icon[0] === (index - 1)) {
                    $items.append('<a href="javascript:void(0)" title="' +
                        Config.htmlEntities(key) + '">' +
                        this.createdEmojiIcon(icon, true) +
                        '<span class="label">' + Config.htmlEntities(key) +
                        '</span></a>');
                }
            });
        } else {
            ConfigStorage.get('emojis_recent', (curEmojis) => {
                curEmojis = curEmojis || Config.defaultRecentEmojis || [];

                for (let i = 0; i < curEmojis.length; i++) {
                    const key = curEmojis[i];

                    if (this.icons[key]) {
                        $items.append('<a href="javascript:void(0)" title="' +
                            Config.htmlEntities(key) + '">' +
                            this.createdEmojiIcon(this.icons[key], true) +
                            '<span class="label">' + Config.htmlEntities(key) +
                            '</span></a>');
                    }
                }
            });
        }
    }

    createdEmojiIcon(emoji) {
        const category = emoji[0];
        const row = emoji[1];
        const column = emoji[2];
        const name = emoji[3];
        const filename = EmojiPicker.emojiSource + '/emoji_spritesheet_!.png';
        const blankGifPath = EmojiPicker.emojiSource + '/blank.gif';
        const iconSize = 25;
        const xoffset = -(iconSize * column);
        const yoffset = -(iconSize * row);
        const scaledWidth = (Config.EmojiCategorySpritesheetDimens[category][1] * iconSize);
        const scaledHeight = (Config.EmojiCategorySpritesheetDimens[category][0] * iconSize);

        let style = 'display:inline-block;';
        style += 'width:' + iconSize + 'px;';
        style += 'height:' + iconSize + 'px;';
        style += 'background:url(\'' + filename.replace('!', category) + '\') ' +
            xoffset + 'px ' + yoffset + 'px no-repeat;';
        style += 'background-size:' + scaledWidth + 'px ' + scaledHeight + 'px;';

        return '<img src="' + blankGifPath + '" class="img" style="' +
            style + '" alt="' + Config.htmlEntities(name) + '">';
    }

    colonToUnicode(emoij) {
        return emoij.replace(Config.rx_colons, (m) => {
            const val = Config.mapcolon[m];

            if (val) {
                return val;
            } else {
                return '';
            }
        });
    }

    emojiPanel() {
        this.$panel = $(`<div class="emoji-menu emoji-menu-container">\n` +
            '    <div class="emoji-items-wrap1">\n' +
            '        <table class="emoji-menu-tabs">\n' +
            '            <tbody>\n' +
            '            <tr>\n' +
            '                <td><a class="emoji-menu-tab icon-recent-selected"></a></td>\n' +
            '                <td><a class="emoji-menu-tab icon-smile"></a></td>\n' +
            '                <td><a class="emoji-menu-tab icon-flower"></a></td>\n' +
            '                <td><a class="emoji-menu-tab icon-bell"></a></td>\n' +
            '                <td><a class="emoji-menu-tab icon-car"></a></td>\n' +
            '                <td><a class="emoji-menu-tab icon-grid"></a></td>\n' +
            '            </tr>\n' +
            '            </tbody>\n' +
            '        </table>\n' +
            '        <div class="emoji-items-wrap mobile_scrollable_wrap">\n' +
            '            <div class="emoji-items"></div>\n' +
            '        </div>\n' +
            '    </div>\n' +
            '</div>'+
            '<div class="close-modal hide-modal"></div>').hide();
        this.$panel.appendTo('body');
        this.loadEmojis();
        this.updateEmojisList(0);
    }

    destroy() {
        this.$panel.remove();
        this.$panel = null;
    }
}
