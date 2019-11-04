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
