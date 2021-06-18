from django import forms
from .models import Post

from tinymce.widgets import TinyMCE
from django_summernote.widgets import SummernoteWidget

class PostForm(forms.ModelForm):
    # content = forms.CharField(widget=TinyMCE(attrs={'cols': '100%', 'rows': 25}))

    class Meta:
        model = Post
        fields = ['is_notice', 'category', 'title', 'execution_date', 'content', 'is_hide_comment', 'password']
        widgets = {
            'content': SummernoteWidget(),
        }
