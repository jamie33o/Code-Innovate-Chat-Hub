from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from crispy_forms.bootstrap import FormActions
from django import forms
from .models import ChannelPosts
from django_summernote.widgets import SummernoteInplaceWidget

class ChannelPostForm(forms.ModelForm):
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
