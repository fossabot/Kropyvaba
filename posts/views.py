# coding: utf-8

"""file with backend code"""

# django stuff
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
import random
from calendar import timegm
from datetime import datetime, timedelta
from django.core.paginator import Paginator

from django.views.decorators.cache import cache_page

# database models
from posts.models import Board, Posts

from posts.forms import PostForm
from kropyvaba.settings import config, CACHE_TTL

EMPTY_POST = '(коментар відсутній)'
boards_update = True  # switch when there are some adding/editing of boards
boards_cached = {}
boards_navlist = []

# @cache_page(CACHE_TTL)
def render_index(request):
    try:
        boards = get_boards_navlist()
        fields = ['id', 'body_nomarkup', 'thread', 'time', 'ip']
        posts = []
        for b in boards:
            for post in get_posts(b).values_list(*fields):
                posts += [post + (b,)]
        recent_posts = [PostBreaf(post) for post in posts[::-1]]
        recent_posts = sorted(recent_posts, key=lambda x: x.time, reverse=True)
        context = {
                    'config': config,
                    'boards': boards.exclude(uri='bugs'),
                    'slogan': random.choice(config['slogan']),
                    'stats': make_stats(posts),
                    'recent_posts': recent_posts[:30]
                }
        return render(request, 'posts/main_page.html', context)
    except ObjectDoesNotExist:
        return HttpResponse('404')


def render_board(request, board_name, current_page=1):
    try:
        board = get_board(board_name)
        board.url = board.uri
        posts = get_posts(board)
        threads = get_threads(board, posts).order_by('-bump')
        pages = Paginator(threads, 10)
        threads = pages.page(int(current_page))
        for thread in threads:
            thread.posts = posts.filter(thread=thread.id)
            posts_len = len(thread.posts)
            thread.omitted = posts_len - 3
            thread.posts = thread.posts[thread.omitted:]
        form = PostForm()
        context = {
                    'config': config,
                    'board': board,
                    'boards': get_boards_navlist(),
                    'threads': threads,
                    'pages': pages,
                    'hr': True,
                    'index': True,
                    'form': form
                }
        return render(request, 'posts/index.html', context)
    except ObjectDoesNotExist:
        return HttpResponse('404')


#@cache_page(CACHE_TTL)
def render_thread(request, board_name, thread_id):
    try:
        board = get_board(board_name)
        boards = get_boards_navlist()
        board.url = board.uri
        post = get_posts(board).get(id=thread_id)
        post.posts = get_posts(board).filter(thread=post.id)
        form = PostForm()
        context = {
                    'config': config,
                    'board': board,
                    'boards': boards,
                    'threads': [post],
                    'hr': True,
                    'form': form
                }
        return render(request, 'posts/index.html', context)
    except ObjectDoesNotExist:
        return HttpResponse('404')


def render_catalog(request, board_name):
    try:
        board = get_board(board_name)
        boards = get_boards_navlist()
        posts = get_posts(board)
        recent_posts = [post for post in get_threads(board, posts).order_by('-bump')]
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


def make_stats(posts):
    class Statistic(object):
        def __init__(self, posts):
            # functions for DRY
            def count_threads(threads):
                return len([post for post in threads if not post[2]])

            def count_posters(posts):
                return len(set(post[4] for post in posts))
            # getting time info
            past = datetime.utcnow() + timedelta(hours=-24)
            stamp = timegm(past.timetuple())
            # total objects
            self.total_posts = max(*[post[0] for post in posts])
            self.total_threads = count_threads(posts)
            self.posters = count_posters(posts)
            # objects for last 24 hours
            posts = [post for post in posts if post[3] >= stamp]
            print(type(posts))
            self.posts_per24 = len(posts)
            self.threads_per24 = count_threads(posts)
            self.posters_per24 = count_posters(posts)
    stats = Statistic(posts)
    return stats


def get_posts(board): return Posts[board.uri].objects


def get_threads(board, posts): return posts.filter(thread=None)

def get_board(board_uri):
    """
    Return cached board object
    """
    global boards_cached
    global boards_update
    if not (board_uri in boards_cached) or boards_update:
        boards_cached[board_uri] = Board.objects.get(uri=board_uri)
    return boards_cached[board_uri]

def get_boards_navlist():
    global boards_update
    global boards_navlist
    if boards_update:
        boards_navlist = Board.objects.exclude(uri='bugs').order_by('uri')
        boards_update = False
    return boards_navlist

class PostBreaf(object):
    def __init__(self, post):
        self.id, body, self.thread, self.time, _, board = post
        # slice last row

        def s(x): return '\n'.join(x.split('\n')[:-1])
        self.snippet = s(body) if len(s(body)) else EMPTY_POST
        self.board_name = board.title
        self.board_url = board.uri
