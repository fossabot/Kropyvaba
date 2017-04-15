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
        threads = models.Post.objects.filter(thread = None)
        for thrd in threads:
            thrd.posts = models.Post.objects.filter(thread = thrd.id)
        context = {
                    'config': config,
                    'board': current_board,
                    'threads': threads,
                    'hr': True
                }
        return render(request, 'posts/index.html', context)
    except ObjectDoesNotExist:
        return HttpResponse('404')
