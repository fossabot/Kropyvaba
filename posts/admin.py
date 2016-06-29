from django.contrib import admin

# Register your models here.
from .models import Board, Post, ThreadPost

admin.site.register(Board)
admin.site.register(Post)
admin.site.register(ThreadPost)