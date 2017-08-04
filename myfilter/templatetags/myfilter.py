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
    ss = strval.split(';')
    for i, strval in enumerate(ss):
        s = strval.split(',')
        s.reverse()
        ss[i] = ' '.join(s)
    return ';'.join(ss)
