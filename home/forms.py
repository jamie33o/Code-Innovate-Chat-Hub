from django import forms
from .models import ChannelPosts, PostComments

class ChannelPostForm(forms.ModelForm):
    """
    This class is for the summernote editor form

    Parameters:
        super class: class that this class inherits from
    """
    class Meta:
        model = ChannelPosts
        fields = ['post', 'images']  # Include the 'images' field in the form

    

class PostCommentsForm(forms.ModelForm):
    """
    This class is for the summernote editor form

    Parameters:
        super class: class that this class inherits from
    """
    class Meta:
        model = PostComments
        fields = ['post']

    

# use for the tag drop down list
# class AddUserToChannelForm(forms.Form):
#     user = forms.ModelChoiceField(queryset=User.objects.all(), label='Select User')