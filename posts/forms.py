# coding: utf-8

"""handle with user forms (in static mode)"""

from subprocess import call
from tempfile import NamedTemporaryFile
from datetime import datetime
import re

import simplejson as json

from django.forms import ModelForm
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import UploadedFile
from PIL import Image
from imagekit import ImageSpec
from imagekit.processors import ResizeToFit

from config.settings import config
from config.settings import MEDIA_ROOT
from posts.models import Post, Board


class PostForm(ModelForm):
    """
    form for user posts
    """

    def process(self, board, _ip, thread):
        """
        Add new post/thread.

        :param self: form that needs to handle
        :param board: thread or reply board
        :param _ip: ip of poster
        :param thread: thread id if we work with reply
        :return: True if form is valid and processed
        """
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']
        password = self.cleaned_data['password']
        time = datetime.timestamp(datetime.now())
        if thread is None and self.files == {}:
            return False
        if len(self.files) <= config['max_images']:
            return False
        files = handle_files(self.files, str(time), board)
        new_post = Post.objects.create(
            id=Post.objects.filter(board__uri=board).last().id + 1,
            time=int(time),
            board=Board.objects.get(uri=board),
            sage=0,
            cycle=0,
            locked=0,
            sticky=0
        )
        new_post.name = name
        new_post.num_files = len(files)
        new_post.subject = subject
        new_post.email = email
        new_post.body = markup(body, board)
        new_post.files = json.dumps(files)
        nomarkup = '{0}\n<tinyboard proxy>{1}</tinyboard>'.format(body,
                                                                  _ip)
        new_post.body_nomarkup = nomarkup
        new_post.password = password
        new_post.ip = _ip
        new_post.thread = thread
        if not new_post.sage:
            op_post = Post.objects.get(id=thread)
            op_post.bump = int(time)
            op_post.save()
        new_post.bump = time
        new_post.save()
        return new_post.id

    class Meta(object):
        """
        meta class for ModelForm
        """
        model = Post
        exclude = ['time', 'sage', 'cycle', 'locked', 'sticky', 'ip']


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
                    content_type = preview.content_type
                    thumb_generator = Thumbnail(source=preview)
                    thumb = thumb_generator.generate()
                    preview.close()
                    image = Image.open(temp_path)
                else:
                    temp_th = open(path, 'rb+')
                    preview = UploadedFile(file=temp_th)
                    content_type = preview.content_type
                    preview.close()
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
                    "hash": "c5c76d11ff82103d18c3c9767bcb881e",  # TODO hash
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
            post = Post.objects.filter(board__uri=board).get(id=reply_id)
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


class Thumbnail(ImageSpec):

    """Thumbnail setting's."""

    processors = [ResizeToFit(255, 255)]
    format = 'JPEG'
    options = {'quality': 60}
