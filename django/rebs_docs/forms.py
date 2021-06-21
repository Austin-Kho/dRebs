from django import forms

from board.models import Post, Link, File

LinkInlineFormSet = forms.models.inlineformset_factory(
    Post,
    Link,
    fields=['link'],
    extra=1,
    can_delete=True,
    can_delete_extra=False
)

FileInlineFormSet = forms.models.inlineformset_factory(
    Post,
    File,
    fields=['file'],
    extra=1,
    can_delete=True,
    can_delete_extra=False
)
