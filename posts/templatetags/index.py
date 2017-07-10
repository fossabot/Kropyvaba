from django import template
import simplejson as json
from datetime import datetime
from math import floor, log
import os
import random
from config.settings import config, STATIC_ROOT

register = template.Library()


@register.simple_tag
def get_config():
    return config


@register.filter(name='truncate')
def truncate(string):
    return string.split('\n')[0]


@register.filter(name='to_dict')
def to_dict(json_string):
    if type(json_string) is str:
        return json.loads(json_string)


@register.filter(name='first_file')
def first_file(json_string):
    if type(json_string) is str:
        data = json.loads(json_string)
        if len(data):
            return data[0]['thumb']


@register.filter(name='extension')
def extension(filename):
    if type(filename) is str:
        return filename.split('.')[-1]


@register.filter(name='to_time')
def to_time(timestamp):
    if type(timestamp) is int:
        return datetime.fromtimestamp(timestamp).strftime(config['post_date'])


@register.simple_tag
def random_logo():
    return random.choice(os.listdir(STATIC_ROOT+'randlogo/'))


@register.filter(name='format_size')
def format_size(size_in_bytes):
    if size_in_bytes == 0:
        return "0B"
    size_name = ("", "K", "M", "G")
    i = int(floor(log(size_in_bytes, 1024)))
    p = pow(1024, i)
    s = round(size_in_bytes / p, 2)
    return "{0} {1}B".format(s, size_name[i])
