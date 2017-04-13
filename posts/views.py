# django stuff
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

# database models
from posts import models

def render_board(request, board_name):
    try:
        current_board = models.Board.objects.get(uri = board_name)
        threads = models.Post.objects.filter(thread = None)
        for thread in threads:
            print(thread.id)
        contex = {
                    'board': current_board,
                    'threads': threads
                }
        return render(request, 'posts/index.html', contex)
    except ObjectDoesNotExist:
        return HttpResponse('404')
