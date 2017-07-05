# coding: utf-8

"""file with backend code"""
from subprocess import call
from tempfile import NamedTemporaryFile

import logging

import re
import random
from calendar import timegm
from datetime import datetime, timedelta

import simplejson as json

# django stuff
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views.static import serve
from django.core.paginator import Paginator
from django.core.files.uploadedfile import UploadedFile

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
BOARDS_UPDATE = True  # switch when there are some adding/editing of boards
BOARDS_CACHED = {}
BOARDS_NAVLIST = []

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


# @cache_page(CACHE_TTL)
def render_index(request):
    """
    Render main page with lists of boards, recent posts and statistics.
    :param request: user's request
    :return: main page
    """
    try:
        boards = get_boards_navlist()
        fields = ['id', 'body_nomarkup', 'thread', 'time', 'ip']
        posts = []
        for board in boards:
            for post in get_posts(board).values_list(*fields):
                posts += [post + (board,)]
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
    Render board with lists of threads and last 5 posts for them.
    :param request: user's request
    :param board_name: name of board that we should render
    :param current_page: page that user requested
    :return: board page
    """
    try:
        board = get_board(board_name)
        board.url = board.uri
        posts = get_posts(board)
        threads = get_threads(posts).order_by('-bump')
        pages = Paginator(threads, 10)
        threads = pages.page(int(current_page))
        for thread in threads:
            thread.posts = posts.filter(thread=thread.id)
            posts_len = len(thread.posts)
            thread.omitted = posts_len - 5 if posts_len >= 5 else 0
            thread.posts = thread.posts[thread.omitted:]
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            _ip = get_ip(request)
            new_post_id = handle_form(form, board_name, _ip, None)
            if new_post_id:
                if 'json_response' in request.POST:
                    respond = json.dumps({
                        'id': new_post_id,
                        'noko': False,
                        'redirect': '/' + board_name
                    })
                    answer = HttpResponse(
                        respond,
                        content_type="application/json"
                    )
                else:
                    answer = HttpResponseRedirect(
                        reverse('thread', args=[board_name, new_post_id])
                    )
                return answer
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
    Render thread page with all thread's posts.
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
            _ip = get_ip(request)
            new_post_id = handle_form(form, board_name, _ip, thread_id)
            if new_post_id:
                if json_response:
                    respond = json.dumps({
                        'id': new_post_id,
                        'noko': False,
                        'redirect': '/' + board_name
                    })
                    answer = HttpResponse(
                        respond,
                        content_type="application/json"
                    )
                else:
                    answer = HttpResponseRedirect(
                        reverse('thread', args=[
                            board_name,
                            thread_id
                        ]) + '#{0}'.format(new_post_id)
                    )
                return answer
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


def handle_form(form, board, _ip, thread):
    """
    Add new post/thread.
    :param form: form that needs to handle
    :param board: thread or reply board
    :param _ip: ip of poster
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
        new_post = Posts[board].objects.create(
            time=int(time),
            sage=0,
            cycle=0,
            locked=0,
            sticky=0
        )
        new_post.name = name
        new_post.subject = subject
        new_post.email = email
        new_post.body = markup(body, board)
        new_post.files = json.dumps(files)
        nomarkup = '{0}\n<tinyboard proxy>{1}</tinyboard>'.format(body, _ip)
        new_post.body_nomarkup = nomarkup
        new_post.password = password
        new_post.ip = _ip
        new_post.thread = thread
        new_post.bump = time
        new_post.save()
        return new_post.id


def handle_files(files, time, board):
    """
    Check and save files.
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

                # file saving
                index = file[0].replace('file', '')
                path = choose_path(board, 'src', time, ext, index)

                with open(path, 'wb+') as destination:
                    for chunk in file[1].chunks():
                        destination.write(chunk)
                destination.close()

                # TODO: Refactor all this hell

                if ext == 'webm':
                    temp_file = NamedTemporaryFile()
                    temp_path = temp_file.name + '.png'
                    call(["ffmpeg",
                          "-i", path,
                          "-vframes", "1",
                          temp_path])
                    temp_file.close()
                    temp_th = open(temp_path, 'rb+')
                    preview = UploadedFile(file=temp_th)
                    LOGGER.debug(type(preview))
                    thumb_generator = Thumbnail(source=preview)
                    thumb = thumb_generator.generate()
                    preview.close()
                    image = Image.open(temp_path)
                else:
                    image = Image.open(path)
                    thumb_generator = Thumbnail(source=file[1])
                    thumb = thumb_generator.generate()

                path = choose_path(board, 'thumb', time, 'jpg', index)

                destination = open(path, 'wb+')
                destination.write(thumb.read())
                destination.close()

                thumb = Image.open(path)

                filename = '{0}-{1}.{2}'.format(time, index, ext)

                file_data = {
                    "name": name,
                    "type": content_type,
                    "tmp_name": ".",  # ???
                    "error": 0,
                    "size": size,
                    "filename": name,
                    "extension": ext,
                    "file_id": time,
                    "file": filename,
                    "thumb": '{0}-{1}.jpg'.format(time, index),
                    "is_an_image": content_type.split('/')[0] == 'image',
                    "hash": "c5c76d11ff82103d18c3c9767bcb881e",
                    "width": image.width,
                    "height": image.height,
                    "thumbwidth": thumb.width,
                    "thumbheight": thumb.height,
                    "file_path": '{0}/src/{1}'.format(board, filename),
                    "thumb_path": '{0}/thumb/{1}-{2}.jpg'.format(board,
                                                                 time,
                                                                 index)
                }
                image.close()
                thumb.close()
                _files.append(file_data)
    return _files


def choose_path(board, _type, time, ext, index):
    """
    Form a system path for file.
    :param board: file's board
    :param _type: type of file (src/thumb)
    :param time: current time
    :param ext: extension
    :param index: file's index in the form
    :return: path string
    """
    directory = '{0}{1}/{2}/'.format(MEDIA_ROOT, _type, board,)
    file = '{0}-{1}.{2}'.format(time, index, ext)
    return directory+file


def render_catalog(request, board_name):
    """
    Render catalog page for specific board.
    :param request: user's request
    :param board_name: board url
    :return: catalog page
    """
    try:
        board = get_board(board_name)
        boards = get_boards_navlist()
        posts = get_posts(board)
        recent_posts = [_ for _ in get_threads(posts).order_by('-bump')]
        for thread in recent_posts:
            thread.reply_count = len(get_posts(board).filter(thread=thread.id))
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
    Count posting statistics.
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
                Count number of threads in _posts.
                :param _posts: source data
                :return: number of threads
                """
                return len([post for post in _posts if not post[2]])

            def count_posters(_posts):
                """
                Count number of uniques posters in _posts.
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
    Return post's query.
    :param board: board %)
    :return: post's query
    """
    return Posts[board.uri].objects


def get_threads(posts):
    """
    Return threads objects.
    :param posts: data for filtering
    :return: threads query
    """
    return posts.filter(thread=None)


def markup(body, board):
    """
    Generate a markup for text.
    :param body: text for processing
    :param board: posts board
    :return: markuped text
    """
    strings = body.split('\n')
    respond = []
    for string in strings:
        string = string.replace('>', '&gt;')
        string = string.replace('<', '&lt;')

        def process_markup(regex, output):
            """
            Process markup for simple rules i.e. bold or cursive text.
            :param regex: regex condition
            :param output: rule for replace
            :return: processed string
            """

            def replace(match, result):
                text = match.group('text')
                return result.format(text)

            return re.sub(regex, lambda line: replace(line, output), string)

        # quotation

        string = process_markup(
            r"^(?P<quote_mark>&gt;)(?P<text>(?!&gt;).+)",
            '<span class="quote">&gt;{0}</span>'
        )

        # reply's

        def rep(match):
            reply_id = match.group('id')
            post = Posts[board].objects.get(id=reply_id)
            if post:
                thread_id = post.thread if post.thread else post.id
                link = reverse('thread', args=[board, thread_id])
                if not post.thread:
                    link += '#' + str(post.id)
                return '''<a onclick="highlightReply('{0}', event);\
                          "href="{1}">&gt;&gt;{0}</a>'''.format(reply_id, link)

        string = re.sub(r"^(?P<reply>&gt;&gt;)(?P<id>\d+)", rep, string)

        # bold

        string = process_markup(
            r"\*\*(?P<text>.+)\*\*",
            '<strong>{0}</strong>'
        )

        # italic

        string = process_markup(r"\*(?P<text>.+)\*", '<em>{0}</em>')

        # underline

        string = process_markup(r"\_\_(?P<text>.+)\_\_", '<u>{0}</u>')

        # strike

        string = process_markup(r"DEL(?P<text>.+)DEL", '<strike>{0}</strike>')

        # spoiler

        string = process_markup(
            r"\%\%(?P<text>.+)\%\%",
            '<span class="spoiler">{0}</span>'
        )

        respond += [string]

    return '<br>'.join(respond)


def get_ip(request):
    """
    Return a user ip.
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
    global BOARDS_CACHED
    global BOARDS_UPDATE
    if not (board_uri in BOARDS_CACHED) or BOARDS_UPDATE:
        BOARDS_CACHED[board_uri] = Board.objects.get(uri=board_uri)
    return BOARDS_CACHED[board_uri]


def get_boards_navlist():
    """
    TODO: rewrite
    :return: board
    """
    global BOARDS_UPDATE
    global BOARDS_NAVLIST
    if BOARDS_UPDATE:
        BOARDS_NAVLIST = Board.objects.exclude(uri='bugs').order_by('uri')
        BOARDS_UPDATE = False
    return BOARDS_NAVLIST


class PostBreaf(object):
    """
    Object for main page.
    """

    def __init__(self, post):
        self.id, body, self.thread, self.time, _, board = post

        # slice last row
        def _slice(text):
            """
            Cut off last row.
            :param text: text for cutting
            :return: text within last row
            """
            return '\n'.join(text.split('\n')[:-1])

        sliced_body = _slice(body)
        length_of_sliced_body = len(sliced_body)

        self.snippet = sliced_body if length_of_sliced_body else EMPTY_POST
        self.board_name = board.title
        self.board_url = board.uri


class Thumbnail(ImageSpec):
    """
    Thumbnail setting's.
    """
    processors = [ResizeToFit(255, 255)]
    format = 'JPEG'
    options = {'quality': 60}
