from django.contrib import admin

# Register your models here.
from .models import Board, Post, Report

admin.site.register(Board)
admin.site.register(Post)
admin.site.register(Report)
