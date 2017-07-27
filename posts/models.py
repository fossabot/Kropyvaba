import os

from django.db import models
from config.settings import MEDIA_ROOT


class Board(models.Model):
    NO_FLAGS = 'NO'
    REAL_LOCATION = 'RL'
    USER_CHOICE = 'UC'
    FLAGS_OPTIONS_CHOICES = (
        (NO_FLAGS, 'All posts without flags'),
        (REAL_LOCATION, "Flags represents location based on poster's ip"),
        (USER_CHOICE, 'Posters can choose flag for post'),
    )
    uri = models.CharField(max_length=58)
    title = models.TextField()
    subtitle = models.TextField(blank=True, null=True)
    posts = models.IntegerField(default=0)
    nsfw = models.BooleanField(default=False, blank=True)
    flags = models.CharField(
        max_length=2,
        choices=FLAGS_OPTIONS_CHOICES,
        default=NO_FLAGS,
    )

    def save(self, *args, **kwargs):
        super(Board, self).save(*args, **kwargs)
        if not self.pk:
            if not os.path.exists('{0}thumb/{1}'.format(MEDIA_ROOT, self.uri)):
                os.makedirs('{0}thumb/{1}'.format(MEDIA_ROOT, self.uri))
            print('{0}thumb/{1}'.format(MEDIA_ROOT, self.uri))
            if not os.path.exists('{0}src/{1}'.format(MEDIA_ROOT, self.uri)):
                os.makedirs('{0}src/{1}'.format(MEDIA_ROOT, self.uri))

    def __str__(self):
        return self.title


class Post(models.Model):
    global_id = models.AutoField(primary_key=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    id = models.IntegerField(blank=True, null=True)
    thread = models.IntegerField(blank=True, null=True)
    subject = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=30, blank=True, null=True)
    name = models.CharField(max_length=35, blank=True, null=True)
    trip = models.CharField(max_length=15, blank=True, null=True)
    capcode = models.CharField(max_length=50, blank=True, null=True)
    body = models.TextField(blank=True)
    body_nomarkup = models.TextField(blank=True, null=True, max_length=16_000)
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

    def __str__(self):
        return '{0}     |       {1}'.format(self.id, self.body_nomarkup)
