from datetime import datetime
from django.utils.timesince import timesince
from django import template
from transliterate import translit

register = template.Library()

import re

@register.filter
def time_since(strval):
    """Time interval."""
    try:
        return timesince(strval)
    except:
        return strval

@register.filter
def strans(strval):
    """Reverse text."""
    ss = strval.split(';')
    for i, strval in enumerate(ss):
        s = strval.split(',')
        s.reverse()
        ss[i] = ' '.join(s)
    return ';'.join(ss)

@register.filter
def strip_text(s):
    """Remove special chars."""
    s = s.replace('"','')
    s = s.replace("'",'')
    s = s.replace(">",'')
    s = s.replace("<",'')
    s = s.replace("!",'')
    return s

@register.filter
def strip_anno(s):
    "Strip Annotation word from Book content."
    return s.replace('>Annotation<', '><', 1)

@register.filter
def to_translit(s):
    return re.sub('[^\w]', '', translit(s, 'ru', reversed=True).replace(" ", "_").lower())
