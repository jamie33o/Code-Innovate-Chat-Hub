from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from crispy_forms.bootstrap import Field, FormActions
from django import forms
from .models import ChannelPosts

class ChannelPostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-6'),
                Column('post', css_class='col-md-6'),
            ),
            FormActions(
                Submit('submit', 'Submit', css_class='btn btn-primary')
            )
        )

    class Meta:
        model = ChannelPosts
        fields = ['name', 'post']