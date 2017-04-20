# django stuff
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
import random

# database models
from posts import models

from kropyvaba.settings import config

EMPTY_POST='(коментар відсутній)'

def render_index(request):
    try:
        boards=models.Board.objects.exclude(uri='bugs').order_by('uri')
        recent_posts=[]
        for board in models.Board.objects.all():
            for pst in models.Posts[board.uri].objects.values_list('id', 'body_nomarkup', 'thread').order_by('-id')[:30]:
                post=PostBreaf(pst[0], pst[1], pst[2], board.title, board.uri)
                recent_posts.append(post)
        #for post in recent_posts:
            #post
        context={
                    'config': config,
                    'boards': boards,
                    'slogan': random.choice(config['slogan']),
                    'stats': make_stats(),
                    'recent_posts': recent_posts[:30]
                }
        return render(request, 'posts/main_page.html', context)
    except ObjectDoesNotExist:
        return HttpResponse('404')

def render_board(request, board_name):
    try:
        current_board=models.Board.objects.get(uri=board_name)
        current_board.url=current_board.uri
        boards=models.Board.objects.exclude(uri='bugs').order_by('uri')
        threads=models.Posts[current_board.uri].objects.filter(thread=None).order_by('-bump')[:15]
        for thrd in threads:
            thrd.posts=models.Posts[current_board.uri].objects.filter(thread=thrd.id)
            thrd.omitted=len(thrd.posts) - 3
            thrd.posts=thrd.posts[:3]
        pages=[Page(_) for _ in range(15)]
        context={
                    'config': config,
                    'board': current_board,
                    'boards': boards,
                    'threads': threads,
                    'pages': pages,
                    'hr': True,
                    'index': True
                }
        return render(request, 'posts/index.html', context)
    except ObjectDoesNotExist:
        return HttpResponse('404')

def render_thread(request, board_name, thread_id):
    try:
        current_board=models.Board.objects.get(uri=board_name)
        boards=models.Board.objects.exclude(uri='bugs').order_by('uri')
        current_board.url=current_board.uri
        post=models.Posts[current_board.uri].objects.get(id=thread_id)
        post.posts=models.Posts[current_board.uri].objects.filter(thread=post.id)
        context={
                    'config': config,
                    'board': current_board,
                    'boards': boards,
                    'threads': [post],
                    'hr': True
                }
        return render(request, 'posts/index.html', context)
    except ObjectDoesNotExist:
        return HttpResponse('404')

def render_catalog(request, board_name):
    try:
        current_board=models.Board.objects.get(uri=board_name)
        boards=models.Board.objects.exclude(uri='bugs').order_by('uri')
        recent_posts=[]
        for pst in models.Posts[current_board.uri].objects.filter(thread=None).order_by('-bump'):
            recent_posts.append(pst)
        for thrd in recent_posts:
            thrd.reply_count=len(models.Posts[current_board.uri].objects.filter(thread=thrd.id))
        context={
                    'config': config,
                    'board': current_board,
                    'boards': boards,
                    'recent_posts': recent_posts,
                    'hr': True
                }
        return render(request, 'posts/catalog.html', context)
    except ObjectDoesNotExist:
        return HttpResponse('404')

def make_stats():
    class Statistic(object):
        def __init__(self):
            self.total_posts=0      
            for board in models.Board.objects.all():
                self.total_posts += models.Posts[board.uri].objects.order_by('-id')[0].id
            self.posts_per24=1
            self.total_threads=0
            for board in models.Board.objects.all():
                self.total_threads += len(models.Posts[board.uri].objects.filter(thread=None))
            self.threads_per24=1
            self.unique_posters=1
            self.unique_posters_per24=1
    stats=Statistic()
    return stats

class PostBreaf(object):
    def __init__(self, post_id, body, thread_id, board_title, board_uri):
        self.id=post_id
        # slice last row
        s=lambda x: '\n'.join(x.split('\n')[:-1])
        self.snippet=s(body) if len(s(body)) else EMPTY_POST
        self.board_name=board_title
        self.board_url=board_uri
        self.thread=thread_id

class Page(object):
    def __init__(self, number):
        self.num=number
