# django stuff
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

# database models
from posts import models

from kropyvaba.settings import config

def render_board(request, board_name):
    try:
        current_board = models.Board.objects.get(uri = board_name)
        current_board.url = current_board.uri
        threads = models.Posts[current_board.uri].objects.filter(thread = None)[:15]
        for thrd in threads:
            thrd.posts = models.Posts[current_board.uri].objects.filter(thread = thrd.id)[:3]
        context = {
                    'config': config,
                    'board': current_board,
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
        current_board.url = current_board.uri
        post = models.Posts[current_board.uri].objects.get(id = thread_id)
        post.posts = models.Posts[current_board.uri].objects.filter(thread = post.id)
        context = {
                    'config': config,
                    'board': current_board,
                    'post': post,
                    'hr': True
                }
        return render(request, 'posts/page.html', context)
    except ObjectDoesNotExist:
        return HttpResponse('404')
