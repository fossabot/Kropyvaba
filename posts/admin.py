from django.contrib import admin

# Register your models here.
from .models import Board, Post

admin.site.register(Board)
admin.site.register(Post)