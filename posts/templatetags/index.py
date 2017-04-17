from django import template
import simplejson as json
import datetime as dttm
import os, random
from kropyvaba.settings import config, STATIC_ROOT

register = template.Library()

@register.filter(name='to_dict')
def to_dict(json_string):
    if type(json_string) is str:
        return(json.loads(json_string))

@register.filter(name='to_time')
def to_time(timestamp):
    if type(timestamp) is int:
        return(dttm.datetime.fromtimestamp(timestamp).strftime(config['post_date']))

@register.simple_tag
def random_logo():
    return random.choice(os.listdir(STATIC_ROOT+'randlogo/'))
