from django import forms
from django_summernote.widgets import SummernoteInplaceWidget
from .models import ChannelPosts

class ChannelPostForm(forms.ModelForm):
    """
    This class is for the summernote editor form

    Parameters:
        super class: class that this class inherits from
    """
    class Meta:
        model = ChannelPosts
        fields = ['post']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['post'].widget = SummernoteInplaceWidget(attrs={'class': 'summernote'})



# use for the tag drop down list
# class AddUserToChannelForm(forms.Form):
#     user = forms.ModelChoiceField(queryset=User.objects.all(), label='Select User')