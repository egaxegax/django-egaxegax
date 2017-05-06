from datetime import datetime
from django import template
from django.utils.timesince import timesince

register = template.Library()

@register.filter
def time_since(strval):
    try:
        return timesince(datetime.strptime(strval, '%Y-%m-%d %H:%M:%S'))
    except:
        return strval
