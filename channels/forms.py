from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from crispy_forms.bootstrap import FormActions
from django import forms
from .models import ChannelPosts
from django_summernote.widgets import SummernoteInplaceWidget

class ChannelPostForm(forms.ModelForm):
    """
    This class is for the summernote editor form

    Parameters:
        super class: class the this class inherits from
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('post', css_class='col-md-6'),
            ),
            FormActions(
                Submit('submit', 'Submit', css_class='btn btn-primary')
            )
        )

        # Add Summernote widget to the 'post' field
        self.fields['post'].widget = SummernoteInplaceWidget(attrs={'class': 'summernote'})

    class Meta:
        model = ChannelPosts
        fields = ['post']

# use for the tag drop down list
# class AddUserToChannelForm(forms.Form):
#     user = forms.ModelChoiceField(queryset=User.objects.all(), label='Select User')