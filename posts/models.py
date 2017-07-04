from __future__ import unicode_literals

from django.db import models


class Antispam(models.Model):
    board = models.CharField(max_length=58)
    thread = models.IntegerField(blank=True, null=True)
    hash = models.CharField(primary_key=True, max_length=40)
    created = models.IntegerField()
    expires = models.IntegerField(blank=True, null=True)
    passed = models.SmallIntegerField()

    class Meta(object):
        managed = False
        db_table = 'antispam'


class BanAppeal(models.Model):
    ban_id = models.IntegerField()
    time = models.IntegerField()
    message = models.TextField()
    denied = models.IntegerField()

    class Meta(object):
        managed = False
        db_table = 'ban_appeals'


class Ban(models.Model):
    ipstart = models.CharField(max_length=16)
    ipend = models.CharField(max_length=16, blank=True, null=True)
    created = models.IntegerField()
    expires = models.IntegerField(blank=True, null=True)
    board = models.CharField(max_length=58, blank=True, null=True)
    creator = models.IntegerField()
    reason = models.TextField(blank=True, null=True)
    seen = models.IntegerField()
    post = models.TextField(blank=True, null=True)

    class Meta(object):
        managed = False
        db_table = 'bans'


class Board(models.Model):
    uri = models.CharField(primary_key=True, max_length=58)
    title = models.TextField()
    subtitle = models.TextField(blank=True, null=True)

    class Meta(object):
        managed = False
        db_table = 'boards'


class Cite(models.Model):
    board = models.CharField(max_length=58)
    post = models.IntegerField()
    target_board = models.CharField(max_length=58)
    target = models.IntegerField()

    class Meta(object):
        managed = False
        db_table = 'cites'


class Flood(models.Model):
    ip = models.CharField(max_length=39)
    board = models.CharField(max_length=58)
    time = models.IntegerField()
    posthash = models.CharField(max_length=32)
    filehash = models.CharField(max_length=32, blank=True, null=True)
    isreply = models.IntegerField()

    class Meta(object):
        managed = False
        db_table = 'flood'


class IpNote(models.Model):
    ip = models.CharField(max_length=39)
    mod = models.IntegerField(blank=True, null=True)
    time = models.IntegerField()
    body = models.TextField()

    class Meta(object):
        managed = False
        db_table = 'ip_notes'


class Modlog(models.Model):
    mod = models.IntegerField()
    ip = models.CharField(max_length=39)
    board = models.CharField(max_length=58, blank=True, null=True)
    time = models.IntegerField()
    text = models.TextField()

    class Meta(object):
        managed = False
        db_table = 'modlogs'


class Mod(models.Model):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=256)
    version = models.CharField(max_length=64)
    type = models.SmallIntegerField()
    boards = models.TextField()

    class Meta(object):
        managed = False
        db_table = 'mods'
        unique_together = (('id', 'username'),)


class Mute(models.Model):
    ip = models.CharField(max_length=39)
    time = models.IntegerField()

    class Meta(object):
        managed = False
        db_table = 'mutes'


class News(models.Model):
    name = models.TextField()
    time = models.IntegerField()
    subject = models.TextField()
    body = models.TextField()

    class Meta(object):
        managed = False
        db_table = 'news'


class Noticeboard(models.Model):
    mod = models.IntegerField()
    time = models.IntegerField()
    subject = models.TextField()
    body = models.TextField()

    class Meta(object):
        managed = False
        db_table = 'noticeboard'


class Pm(models.Model):
    sender = models.IntegerField()
    to = models.IntegerField()
    message = models.TextField()
    time = models.IntegerField()
    unread = models.IntegerField()

    class Meta(object):
        managed = False
        db_table = 'pms'


boards = [b.uri for b in Board.objects.all()]

Posts = {}


for brd in boards:
    class Post(models.Model):
        thread = models.IntegerField(blank=True, null=True)
        subject = models.CharField(max_length=100, blank=True, null=True)
        email = models.CharField(max_length=30, blank=True, null=True)
        name = models.CharField(max_length=35, blank=True, null=True)
        trip = models.CharField(max_length=15, blank=True, null=True)
        capcode = models.CharField(max_length=50, blank=True, null=True)
        body = models.TextField(blank=True)
        body_nomarkup = models.TextField(blank=True, null=True)
        time = models.IntegerField()
        bump = models.IntegerField(blank=True, null=True)
        files = models.TextField(blank=True, null=True)
        num_files = models.IntegerField(blank=True, null=True)
        filehash = models.TextField(blank=True, null=True)
        password = models.CharField(max_length=20, blank=True, null=True)
        ip = models.CharField(max_length=39)
        sticky = models.IntegerField()
        locked = models.IntegerField()
        cycle = models.IntegerField()
        sage = models.IntegerField()
        embed = models.TextField(blank=True, null=True)
        slug = models.CharField(max_length=256, blank=True, null=True)

        class Meta(object):
            managed = False
            db_table = 'posts_'+brd

    Posts[brd] = Post


class Report(models.Model):
    time = models.IntegerField()
    ip = models.CharField(max_length=39)
    board = models.CharField(max_length=58, blank=True, null=True)
    post = models.IntegerField()
    reason = models.TextField()

    class Meta(object):
        managed = False
        db_table = 'reports'


class Robot(models.Model):
    hash = models.CharField(primary_key=True, max_length=40)

    class Meta(object):
        managed = False
        db_table = 'robot'


class SearchQuerie(models.Model):
    ip = models.CharField(max_length=39)
    time = models.IntegerField()
    query = models.TextField()

    class Meta(object):
        managed = False
        db_table = 'search_queries'


class ThemeSetting(models.Model):
    theme = models.CharField(max_length=40)
    name = models.CharField(max_length=40, blank=True, null=True)
    value = models.TextField(blank=True, null=True)

    class Meta(object):
        managed = False
        db_table = 'theme_settings'
