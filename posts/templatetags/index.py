from django import template
import simplejson as json
from datetime import datetime
import os
import random
from kropyvaba.settings import config, STATIC_ROOT

register = template.Library()


@register.filter(name='to_dict')
def to_dict(json_string):
    if type(json_string) is str:
        return json.loads(json_string)


@register.filter(name='to_time')
def to_time(timestamp):
    if type(timestamp) is int:
        return datetime.fromtimestamp(timestamp).strftime(config['post_date'])


@register.simple_tag
def random_logo():
    return random.choice(os.listdir(STATIC_ROOT+'randlogo/'))
