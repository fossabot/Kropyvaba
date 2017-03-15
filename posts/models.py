# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Antispam(models.Model):
    board = models.CharField(max_length=58)
    thread = models.IntegerField(blank=True, null=True)
    hash = models.CharField(primary_key=True, max_length=40)
    created = models.IntegerField()
    expires = models.IntegerField(blank=True, null=True)
    passed = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'antispam'


class BanAppeals(models.Model):
    ban_id = models.IntegerField()
    time = models.IntegerField()
    message = models.TextField()
    denied = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ban_appeals'


class Bans(models.Model):
    ipstart = models.CharField(max_length=16)
    ipend = models.CharField(max_length=16, blank=True, null=True)
    created = models.IntegerField()
    expires = models.IntegerField(blank=True, null=True)
    board = models.CharField(max_length=58, blank=True, null=True)
    creator = models.IntegerField()
    reason = models.TextField(blank=True, null=True)
    seen = models.IntegerField()
    post = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bans'


class Boards(models.Model):
    uri = models.CharField(primary_key=True, max_length=58)
    title = models.TextField()
    subtitle = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'boards'


class Cites(models.Model):
    board = models.CharField(max_length=58)
    post = models.IntegerField()
    target_board = models.CharField(max_length=58)
    target = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'cites'


class Flood(models.Model):
    ip = models.CharField(max_length=39)
    board = models.CharField(max_length=58)
    time = models.IntegerField()
    posthash = models.CharField(max_length=32)
    filehash = models.CharField(max_length=32, blank=True, null=True)
    isreply = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'flood'


class IpNotes(models.Model):
    ip = models.CharField(max_length=39)
    mod = models.IntegerField(blank=True, null=True)
    time = models.IntegerField()
    body = models.TextField()

    class Meta:
        managed = False
        db_table = 'ip_notes'


class Modlogs(models.Model):
    mod = models.IntegerField()
    ip = models.CharField(max_length=39)
    board = models.CharField(max_length=58, blank=True, null=True)
    time = models.IntegerField()
    text = models.TextField()

    class Meta:
        managed = False
        db_table = 'modlogs'


class Mods(models.Model):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=256)
    version = models.CharField(max_length=64)
    type = models.SmallIntegerField()
    boards = models.TextField()

    class Meta:
        managed = False
        db_table = 'mods'
        unique_together = (('id', 'username'),)


class Mutes(models.Model):
    ip = models.CharField(max_length=39)
    time = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'mutes'


class News(models.Model):
    name = models.TextField()
    time = models.IntegerField()
    subject = models.TextField()
    body = models.TextField()

    class Meta:
        managed = False
        db_table = 'news'


class Noticeboard(models.Model):
    mod = models.IntegerField()
    time = models.IntegerField()
    subject = models.TextField()
    body = models.TextField()

    class Meta:
        managed = False
        db_table = 'noticeboard'


class Pms(models.Model):
    sender = models.IntegerField()
    to = models.IntegerField()
    message = models.TextField()
    time = models.IntegerField()
    unread = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'pms'


class Posts(models.Model):
    thread = models.IntegerField(blank=True, null=True)
    subject = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=30, blank=True, null=True)
    name = models.CharField(max_length=35, blank=True, null=True)
    trip = models.CharField(max_length=15, blank=True, null=True)
    capcode = models.CharField(max_length=50, blank=True, null=True)
    body = models.TextField()
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

    class Meta:
        managed = False
        db_table = 'posts_a'


class Reports(models.Model):
    time = models.IntegerField()
    ip = models.CharField(max_length=39)
    board = models.CharField(max_length=58, blank=True, null=True)
    post = models.IntegerField()
    reason = models.TextField()

    class Meta:
        managed = False
        db_table = 'reports'


class Robot(models.Model):
    hash = models.CharField(primary_key=True, max_length=40)

    class Meta:
        managed = False
        db_table = 'robot'


class SearchQueries(models.Model):
    ip = models.CharField(max_length=39)
    time = models.IntegerField()
    query = models.TextField()

    class Meta:
        managed = False
        db_table = 'search_queries'


class ThemeSettings(models.Model):
    theme = models.CharField(max_length=40)
    name = models.CharField(max_length=40, blank=True, null=True)
    value = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'theme_settings'
