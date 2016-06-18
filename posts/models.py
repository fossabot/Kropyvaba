from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage

fs = FileSystemStorage(location = settings.MEDIA_ROOT)

from imagekit.models.fields import ImageSpecField
from imagekit.processors import ResizeToFit, ResizeToFill
# Create your models here.
class Board(models.Model):
	name = models.CharField(max_length=8)
	description = models.CharField(max_length=32)
	def __str__(self):
		return self.name

class Post(models.Model):
	replay_to = models.IntegerField(default=0)
	close = models.IntegerField(default=0)
	posts = models.IntegerField(default=0)
	board = models.ForeignKey(Board, on_delete=models.CASCADE)
	author = models.CharField(blank=True, max_length=64)
	pub_date = models.DateTimeField('date_published')
	body = models.CharField(blank=True, max_length=15000)
	theme = models.CharField(blank=True, max_length=100)
	file = models.FileField(upload_to='' ,max_length=256, blank=True, null=True)
	thumb = ImageSpecField(source='file',processors =[ResizeToFit(250, 250)],format='PNG',options={'quality': 90})
	threadthumb=  ImageSpecField(source='file',processors =[ResizeToFill(300, 150)],format='PNG',options={'quality': 90})
	def __str__(self):
		return self.body