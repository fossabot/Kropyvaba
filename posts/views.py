# coding: utf-8

"""file with backend code"""

import logging

import simplejson as json

# django stuff
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views.static import serve
import random
from calendar import timegm
from datetime import datetime, timedelta
from django.core.paginator import Paginator

# from django.views.decorators.cache import cache_page

# database models
from posts.models import Board, Posts

from posts.forms import PostForm
from config.settings import MEDIA_ROOT
from config.settings import config  # , CACHE_TTL

from PIL import Image
from imagekit import ImageSpec
from imagekit.processors import ResizeToFit

EMPTY_POST = '(коментар відсутній)'
boards_update = True  # switch when there are some adding/editing of boards
boards_cached = {}
boards_navlist = []

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


# @cache_page(CACHE_TTL)
def render_index(request):
    """
    Renders main page with lists of boards, recent posts and statistics
    :param request: user's request
    :return: main page
    """
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
    """
    Renders board with lists of threads and last 5 posts for them
    :param request: user's request
    :param board_name: name of board that we should render
    :param current_page: page that user requested
    :return: board page
    """
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
            thread.omitted = posts_len - 5 if posts_len >= 5 else 0
            thread.posts = thread.posts[thread.omitted:]
        if request.method == 'POST':
            # TODO: add dollchan's requests handling
            form = PostForm(request.POST, request.FILES)
            ip = get_ip(request)
            new_post_id = handle_form(form, board_name, ip, None)
            if new_post_id:
                return HttpResponseRedirect(
                    reverse('thread', args=[board_name, new_post_id])
                    )
        else:
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


# @cache_page(CACHE_TTL)
def render_thread(request, board_name, thread_id):
    """
    Renders thread page with all thread's posts
    :param request: user's request
    :param board_name: name of threads board
    :param thread_id: thread id
    :return: thread page
    """
    try:
        board = get_board(board_name)
        boards = get_boards_navlist()
        board.url = board.uri
        post = get_posts(board).get(id=thread_id)
        post.posts = get_posts(board).filter(thread=post.id)
        if request.method == 'POST':
            json_response = 'json_response' in request.POST
            form = PostForm(request.POST, request.FILES)
            ip = get_ip(request)
            new_post_id = handle_form(form, board_name, ip, thread_id)
            if new_post_id:
                if json_response:
                    respond = json.dumps({
                        'id': new_post_id,
                        'noko': False,
                        'redirect': '/'+board_name
                    })
                    return HttpResponse(
                        respond,
                        content_type="application/json"
                    )
                else:
                    return HttpResponseRedirect(
                        reverse('thread', args=[
                            board_name,
                            thread_id
                        ])+'#{0}'.format(new_post_id)
                    )
        else:
            form = PostForm()
        context = {
                    'config': config,
                    'board': board,
                    'boards': boards,
                    'threads': [post],
                    'hr': True,
                    'form': form,
                    'id': 1
                }
        return render(request, 'posts/page.html', context)
    except ObjectDoesNotExist:
        return HttpResponse('404')


def handle_form(form, board, ip, thread):
    """
    Adds new post/thread
    :param form: form that needs to handle
    :param board: thread or reply board
    :param ip: ip of poster
    :param thread: thread id if we work with reply
    :return: True if form is valid and processed
    """
    if form.is_valid():
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        subject = form.cleaned_data['subject']
        body = form.cleaned_data['body']
        password = form.cleaned_data['password']
        time = datetime.timestamp(datetime.now())
        if thread is None and form.files == {}:
            return False
        files = handle_files(form.files, str(time), board)
        sage = cycle = locked = sticky = 0
        new_post = Posts[board].objects.create(
            time=int(time),
            sage=sage,
            cycle=cycle,
            locked=locked,
            sticky=sticky
        )
        new_post.name = name
        new_post.subject = subject
        new_post.email = email
        new_post.body = body
        new_post.files = json.dumps(files)
        # Tinyboard logic…
        new_post.body_nomarkup = markup(body, ip)
        new_post.password = password
        new_post.ip = ip
        new_post.thread = thread
        new_post.bump = time
        new_post.save()
        return new_post.id


def handle_files(files, time, board):
    """
    Checks and save files.
    :param files: files fot handling
    :param time: current time
    :param board: post's board
    :return: json list of files features
    """
    _files = []
    for file in files.items():
        size = file[1].size
        if size <= config['max_filesize']:
            name = file[1].name
            ext = name.split('.')[-1]
            content_type = file[1].content_type  # TODO: doesn't work when doll
            if ext in config['allowed_ext']:
                path = '{0}src/{1}/{2}.{3}'.format(MEDIA_ROOT,
                                                   board,
                                                   time,
                                                   ext)
                # file saving
                # TODO: add file exist checking
                with open(path, 'wb+') as destination:
                    for chunk in file[1].chunks():
                        destination.write(chunk)
                destination.close()

                # TODO: add webm handling
                image = Image.open(path)

                path = '{0}thumb/{1}/{2}.jpg'.format(MEDIA_ROOT,
                                                     board,
                                                     time)
                # thumb generation
                thumb_generator = Thumbnail(source=file[1])
                thumb = thumb_generator.generate()

                destination = open(path, 'wb+')
                destination.write(thumb.read())
                destination.close()

                thumb = Image.open(path)

                file_data = {
                    "name": name,
                    "type": content_type,
                    "tmp_name": ".",  # ???
                    "error": 0,
                    "size": size,
                    "filename": name,
                    "extension": ext,
                    "file_id": time,
                    "file": '{0}.{1}'.format(time, ext),
                    "thumb": '{0}.jpg'.format(time),
                    "is_an_image": content_type.split('/')[0] == 'image',
                    "hash": "c5c76d11ff82103d18c3c9767bcb881e",
                    "width": image.width,
                    "height": image.height,
                    "thumbwidth": thumb.width,
                    "thumbheight": thumb.height,
                    "file_path": '{0}/src/{1}.{2}'.format(board, time, ext),
                    "thumb_path": '{0}/thumb/{1}.jpg'.format(board, time)
                }
                image.close()
                thumb.close()
                _files.append(file_data)
    return _files


def render_catalog(request, board_name):
    """
    Renders catalog page for specific board
    :param request: user's request
    :param board_name: board url
    :return: catalog page
    """
    try:
        board = get_board(board_name)
        boards = get_boards_navlist()
        posts = get_posts(board)
        recent_posts = [_ for _ in get_threads(board, posts).order_by('-bump')]
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


def get_media(request, board_name, media_type, path):
    """
    Deal with media files (sic!)
    """
    root = '{0}{1}/{2}'.format(MEDIA_ROOT, media_type, board_name)
    return serve(request, path, document_root=root)


def make_stats(data):
    """
    Counts posting statistics
    :param data: posts for statistics
    :return: Statistics object
    """
    class Statistic(object):
        """
        Object which contain next statistics data:
        Number of all posts;
        Number of posted threads;
        Number of posters;
        Variables with '_per24' prefix -- same things but for last 24 hours
        """
        def __init__(self, posts):
            # functions for DRY
            def count_threads(_posts):
                """
                Counts number of threads in _posts
                :param _posts: source data
                :return: number of threads
                """
                return len([post for post in _posts if not post[2]])

            def count_posters(_posts):
                """
                Counts number of uniques posters in _posts
                :param _posts: source data
                :return: number of posters
                """
                return len(set(post[4] for post in _posts))
            # getting time info
            past = datetime.utcnow() + timedelta(hours=-24)
            stamp = timegm(past.timetuple())
            # total objects
            self.total_posts = sum([max(*[p[0]
                                          for p in posts if p[5] is board])
                                    for board in get_boards_navlist()])
            self.total_threads = count_threads(posts)
            self.posters = count_posters(posts)
            # objects for last 24 hours
            last_posts = [post for post in posts if post[3] >= stamp]
            self.posts_per24 = len(last_posts)
            self.threads_per24 = count_threads(last_posts)
            self.posters_per24 = count_posters(last_posts)
    stats = Statistic(data)
    return stats


def get_posts(board):
    """
    Returns post's query
    :param board: board %)
    :return: post's query
    """
    return Posts[board.uri].objects


def get_threads(board, posts): return posts.filter(thread=None)  # TODO: ???


def markup(body, ip):
    """
    Generates a markup for text
    :param body: text for processing
    :param ip: user's ip
    :return: markuped text
    """
    return '{0}\n<tinyboard proxy>{1}</tinyboard>'.format(body, ip)


def get_ip(request):
    """
    Return a user ip
    :param request: http/s request
    :return: ip address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_board(board_uri):
    """
    TODO: rewrite
    :return: cached board object
    """
    global boards_cached
    global boards_update
    if not (board_uri in boards_cached) or boards_update:
        boards_cached[board_uri] = Board.objects.get(uri=board_uri)
    return boards_cached[board_uri]


def get_boards_navlist():
    """
    TODO: rewrite
    :return: board
    """
    global boards_update
    global boards_navlist
    if boards_update:
        boards_navlist = Board.objects.exclude(uri='bugs').order_by('uri')
        boards_update = False
    return boards_navlist


class PostBreaf(object):
    """
    Object for main page
    """
    def __init__(self, post):
        self.id, body, self.thread, self.time, _, board = post

        # slice last row
        def s(x): return '\n'.join(x.split('\n')[:-1])
        self.snippet = s(body) if len(s(body)) else EMPTY_POST
        self.board_name = board.title
        self.board_url = board.uri


class Thumbnail(ImageSpec):
    """
    Thumbnail setting's
    """
    processors = [ResizeToFit(255, 255)]
    format = 'JPEG'
    options = {'quality': 60}
