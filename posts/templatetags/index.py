from django import template
import simplejson as json
register = template.Library()

@register.filter(name='to_dict')
def to_dict(json_string):
    if type(json_string) is str:
        return(json.loads(json_string))
