from django import forms
from .models import PostsModel, CommentsModel

class PostsForm(forms.ModelForm):
    """
    This class is for the summernote editor form

    Parameters:
        super class: class that this class inherits from
    """
    class Meta:
        model = PostsModel
        fields = ['post', 'images']  # Include the 'images' field in the form

    

class CommentsForm(forms.ModelForm):
    """
    This class is for the summernote editor form

    Parameters:
        super class: class that this class inherits from
    """
    class Meta:
        model = CommentsModel
        fields =  ['post', 'images']

    

# use for the tag drop down list
# class AddUserToChannelForm(forms.Form):
#     user = forms.ModelChoiceField(queryset=User.objects.all(), label='Select User')