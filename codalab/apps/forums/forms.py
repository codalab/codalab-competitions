from django import forms

from captcha.fields import CaptchaField

from .models import Thread, Post


class ThreadForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea)
    #captcha = CaptchaField()

    class Meta:
        model = Thread
        fields = ('title',)

class PostForm(forms.ModelForm):
    #captcha = CaptchaField()

    class Meta:
        model = Post
        fields = ('content',)
