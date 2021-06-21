from django import forms

from board.models import Post, Link, File


LinkInlineFormSet = forms.models.inlineformset_factory(
    Post,
    Link,
    fields=['link'],
    extra=1
)

FileInlineFormSet = forms.models.inlineformset_factory(
    Post,
    File,
    fields=['file'],
    extra=1
)
