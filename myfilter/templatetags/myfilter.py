from datetime import datetime
from django import template
from django.utils.timesince import timesince

register = template.Library()

@register.filter
def time_since(strval):
    try:
        return timesince(strval)
    except:
        return strval

@register.filter
def strans(strval):
    s = strval.split(',')
    s.reverse()
    return ' '.join(s)
