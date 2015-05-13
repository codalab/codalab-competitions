from django import forms


from .models import Thread, Post


class ThreadForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Thread
        fields = ('title',)


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('content',)
