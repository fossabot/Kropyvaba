# django stuff
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
import random

# database models
from posts.models import Board, Posts

from kropyvaba.settings import config

EMPTY_POST = '(коментар відсутній)'


def render_index(request):
    try:
        boards = Board.objects.order_by('uri')
        recent_posts = []
        fields = ('id', 'body_nomarkup', 'thread')
        for b in boards:
            for post in get_posts(b).values_list(*fields)[::-1]:
                recent_posts.append(PostBreaf(post, b))
        context = {
                    'config': config,
                    'boards': boards.exclude(uri='bugs'),
                    'slogan': random.choice(config['slogan']),
                    'stats': make_stats(),
                    'recent_posts': recent_posts[:30]
                }
        return render(request, 'posts/main_page.html', context)
    except ObjectDoesNotExist:
        return HttpResponse('404')


def render_board(request, board_name):
    try:
        board = Board.objects.get(uri=board_name)
        board.url = board.uri
        boards = Board.objects.exclude(uri='bugs').order_by('uri')
        threads = get_threads(board).order_by('-bump')[:15]
        for thrd in threads:
            thrd.posts = get_posts(board).filter(thread=thrd.id)
            thrd.omitted = len(thrd.posts) - 3
            thrd.posts = thrd.posts[:3]
        pages = [Page(_) for _ in range(15)]
        context = {
                    'config': config,
                    'board': board,
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
        board = Board.objects.get(uri=board_name)
        boards = Board.objects.exclude(uri='bugs').order_by('uri')
        board.url = board.uri
        post = get_posts(board).get(id=thread_id)
        post.posts = get_posts(board).filter(thread=post.id)
        context = {
                    'config': config,
                    'board': board,
                    'boards': boards,
                    'threads': [post],
                    'hr': True
                }
        return render(request, 'posts/index.html', context)
    except ObjectDoesNotExist:
        return HttpResponse('404')


def render_catalog(request, board_name):
    try:
        board = Board.objects.get(uri=board_name)
        boards = Board.objects.exclude(uri='bugs').order_by('uri')
        recent_posts = [post for post in get_threads(board).order_by('-bump')]
        for thrd in recent_posts:
            thrd.reply_count = len(get_posts(board).filter(thread=thrd.id))
        context = {
                    'config': config,
                    'board': board,
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
            boards = Board.objects.all()
            self.total_posts = sum([get_posts(b).last().id for b in boards])
            self.posts_per24 = 1
            self.total_threads = sum([len(get_threads(b)) for b in boards])
            self.threads_per24 = 1
            self.unique_posters = 1
            self.unique_posters_per24 = 1
    stats = Statistic()
    return stats


def get_posts(board): return Posts[board.uri].objects


def get_threads(board): return get_posts(board).filter(thread=None)


class PostBreaf(object):
    def __init__(self, post, board):
        post_id = post[0]
        body = post[1]
        thread_id = post[2]
        self.id = post_id
        # slice last row

        def s(x): return '\n'.join(x.split('\n')[:-1])
        self.snippet = s(body) if len(s(body)) else EMPTY_POST
        self.board_name = board.title
        self.board_url = board.uri
        self.thread = thread_id


class Page(object):
    def __init__(self, number):
        self.num = number
