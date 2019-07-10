from django import forms
from .models import AtrticlePost

class ArticlePostForm(forms.ModelForm):
    class Meta:
        model = AtrticlePost
        fields = ('title', 'body')
