from django.forms import ModelForm, TextInput, Textarea
from .models import Post

class PostForm(ModelForm):
	class Meta:
		model = Post
		fields = ['replay_to', 'author', 'theme', 'body', 'file']
		widgets = {
            'author': TextInput(attrs={'id':'author', 'type':'text', 'length':'64'}),
            'theme': TextInput(attrs={'class':'validate', 'type':'text', 'length':'100'}),
			'body': Textarea(attrs={'id':'body', 'class':'materialize-textarea', 'type':'text', 'length':'15000'}),
        }