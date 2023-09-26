import emoji

def replace_emoji_codes(text):
    return emoji.emojize(text, use_aliases=True)
