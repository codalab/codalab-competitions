from django import forms

from .models import Thread, Post


class ThreadForm(forms.ModelForm):
    """Base Thread Form. Allows to start a new topic."""

    content = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Thread
        fields = ('title',)


class PostForm(forms.ModelForm):
    """Base Post Form. Allows to post."""

    class Meta:
        model = Post
        fields = ('content',)
