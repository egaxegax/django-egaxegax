

from datetime import datetime
from django.utils.timesince import timesince
from django import template
register = template.Library()

import urllib, urllib2, urlparse, re
from HTMLParser import HTMLParser
ph = HTMLParser()

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

@register.filter
def strip_text(s):
    s = s.lstrip(' Annotation ')
    s = s.replace('"','')
    s = s.replace("'",'')
    s = s.replace(">",'')
    s = s.replace("<",'')
    s = s.replace("!",'')
    return s

@register.filter
def get_thumb(url, sz):
    if url is None:
        url = ''
    u = urlparse.urlparse(url)
    if u.netloc == 'yadi.sk':
        request = urllib2.Request(url)
        uri = re.findall(r'<img class="[^\"]*" src="([^\"]*)"', urllib2.urlopen(request).read())
    
        if uri:
            scheme, netloc, path, params, query, fragment = urlparse.urlparse(uri[0]) 
            q = urlparse.parse_qs((query))
            q['size'] = [sz + 'x']
            query = urllib.urlencode(q, True)
            muri = urlparse.urlunparse((scheme, netloc, path, params, query, fragment))
            return muri
    return url + '=s' + sz
