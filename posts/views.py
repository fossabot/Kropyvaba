# django stuff
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
import random

# database models
from posts import models

from kropyvaba.settings import config

def render_index(request):
    try:
        boards = models.Board.objects.exclude(uri = 'bugs').order_by('uri')
        # threads = models.Posts[.uri].objects.filter(thread = None)[:15]
        context = {
                    'config': config,
                    'boards': boards,
                    'slogan': random.choice(config['slogan']),
                }
        return render(request, 'posts/main_page.html', context)
    except ObjectDoesNotExist:
        return HttpResponse('404')

def render_board(request, board_name):
    try:
        current_board = models.Board.objects.get(uri = board_name)
        current_board.url = current_board.uri
        boards = models.Board.objects.exclude(uri = 'bugs').order_by('uri')
        threads = models.Posts[current_board.uri].objects.filter(thread = None)[:15]
        for thrd in threads:
            thrd.posts = models.Posts[current_board.uri].objects.filter(thread = thrd.id)[:3]
        context = {
                    'config': config,
                    'board': current_board,
                    'boards': boards,
                    'threads': threads,
                    'hr': True,
                    'index': True
                }
        return render(request, 'posts/index.html', context)
    except ObjectDoesNotExist:
        return HttpResponse('404')

def render_thread(request, board_name, thread_id):
    try:
        current_board = models.Board.objects.get(uri = board_name)
        boards = models.Board.objects.exclude(uri = 'bugs').order_by('uri')
        current_board.url = current_board.uri
        post = models.Posts[current_board.uri].objects.get(id = thread_id)
        post.posts = models.Posts[current_board.uri].objects.filter(thread = post.id)
        context = {
                    'config': config,
                    'board': current_board,
                    'boards': boards,
                    'threads': [post],
                    'hr': True
                }
        return render(request, 'posts/index.html', context)
    except ObjectDoesNotExist:
        return HttpResponse('404')
