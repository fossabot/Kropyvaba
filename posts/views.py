# django stuff
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
import random
from calendar import timegm
from datetime import datetime, timedelta

from django.views.decorators.cache import cache_page

# database models
from posts.models import Board, Posts

from kropyvaba.settings import config, CACHE_TTL

EMPTY_POST = '(коментар відсутній)'

@cache_page(CACHE_TTL)
def render_index(request):
    try:
        boards = Board.objects.order_by('uri')
        recent_posts = []
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


@cache_page(CACHE_TTL)
def render_board(request, board_name, current_page=0):
    try:
        boards = Board.objects.all()
        board = boards.get(uri=board_name)
        board.url = board.uri
        posts = get_posts(board)
        threads = get_threads(board, posts).order_by('-bump')[int(current_page):15]
        for thrd in threads:
            thrd.posts = get_posts(board).filter(thread=thrd.id)
            thrd.omitted = len(thrd.posts) - 3
            thrd.posts = thrd.posts[:3]
        pages = [Page(_) for _ in range(15)]
        for page in pages:
            if page.num == current_page:
                page.set_active()
        context = {
                    'config': config,
                    'board': board,
                    'boards': boards.order_by('uri').exclude(uri='bugs'),
                    'threads': threads,
                    'pages': pages,
                    'hr': True,
                    'index': True
                }
        return render(request, 'posts/index.html', context)
    except ObjectDoesNotExist:
        return HttpResponse('404')


@cache_page(CACHE_TTL)
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


@cache_page(CACHE_TTL)
def render_catalog(request, board_name):
    try:
        board = Board.objects.get(uri=board_name)
        boards = Board.objects.exclude(uri='bugs').order_by('uri')
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


class PostBreaf(object):
    def __init__(self, post):
        self.id, body, self.thread, self.time, _, board = post
        # slice last row

        def s(x): return '\n'.join(x.split('\n')[:-1])
        self.snippet = s(body) if len(s(body)) else EMPTY_POST
        self.board_name = board.title
        self.board_url = board.uri


class Page(object):
    def __init__(self, number):
        self.num = number
        self.selected = False

    def set_active(self):
        self.selected = True
