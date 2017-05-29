# coding: utf-8

"""handle with user forms (in static mode)"""

from django.forms import ModelForm
from posts.models import Post


class PostForm(ModelForm):
    """
    form for user posts
    """
    class Meta(object):
        """
        meta class for ModelForm
        """
        model = Post
        fields = '__all__'
