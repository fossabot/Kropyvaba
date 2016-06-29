from django.forms import CharField, IntegerField, FileField, DateTimeField, ModelChoiceField, ModelForm, TextInput, Textarea, Form
from .models import Board, Post, ThreadPost

class PostForm(ModelForm):
	class Meta:
		model = Post
		fields = ['thread', 'author', 'body', 'file']
		widgets = {
            'author': TextInput(attrs={'id':'author', 'type':'text', 'length':'64'}),
			'body': Textarea(attrs={'id':'body', 'class':'materialize-textarea', 'type':'text', 'length':'15000'}),
        }
		
class ThreadForm(Form):
	thread = IntegerField()
	author = CharField(widget=TextInput(attrs={'id':'author', 'type':'text', 'length':'64'}))
	theme = CharField(widget=TextInput(attrs={'class':'validate', 'type':'text', 'length':'100'}))
	body = CharField(widget=Textarea(attrs={'id':'body', 'class':'materialize-textarea', 'type':'text', 'length':'15000'}))
	file = FileField()